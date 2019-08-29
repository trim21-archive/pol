import json.decoder
from os import path
from enum import IntEnum
from typing import Dict, Optional
from pathlib import Path

import requests_async as requests
import dateutil.parser
from fastapi import Depends, APIRouter
from pydantic import BaseModel, ValidationError
from peewee_async import Manager
from starlette.status import HTTP_502_BAD_GATEWAY
from starlette.requests import Request
from starlette.responses import HTMLResponse, RedirectResponse
from starlette.exceptions import HTTPException
from starlette.templating import Jinja2Templates

from app import db_models
from app.log import logger
from app.core import config
from app.db.redis import PickleRedis
from app.db.depends import get_db, get_redis
from app.api.bgm_tv_auto_tracker.auth import get_current_user
from app.api.bgm_tv_auto_tracker.auth.scheme import cookie_scheme
from app.api.bgm_tv_auto_tracker.auth.session import new_session

templates = Jinja2Templates(
    str(path.normpath(Path(__file__) / '..' / 'templates'))
)

router = APIRouter()


@router.get(
    '/auth',
    description='redirect user to bgm.tv OAuth page, for userscript',
    include_in_schema=config.DEBUG,
)
async def auth_redirect():
    return RedirectResponse(config.BgmTvAutoTracker.oauth_url, status_code=302)


class AuthResponse(BaseModel):
    access_token: str
    expires_in: int
    token_type: str
    scope: Optional[str]
    user_id: int
    refresh_token: str


class UserGroupEnum(IntEnum):
    admin = 1
    bangumi_admin = 2
    window_admin = 3
    quite_user = 4
    banned_user = 5
    character_admin = 8
    wiki_admin = 9
    normal_user = 10
    wiki = 11


class UserInfo(BaseModel):
    id: int
    url: str
    username: str
    nickname: str
    avatar: Dict[str, str]
    sign: str
    usergroup: UserGroupEnum


@router.get(
    '/oauth_callback',
    description='bgm.tv OAuth callback, this api is for userscript',
    include_in_schema=config.DEBUG,
)
async def oauth_callback(
    code: str,
    request: Request,
    db: Manager = Depends(get_db),
    redis: PickleRedis = Depends(get_redis),
):
    try:
        resp = await requests.post(
            'https://bgm.tv/oauth/access_token',
            data={
                'code': code,
                'client_id': config.BgmTvAutoTracker.APP_ID,
                'grant_type': 'authorization_code',
                'redirect_uri': config.BgmTvAutoTracker.callback_url,
                'client_secret': config.BgmTvAutoTracker.APP_SECRET,
            },
        )
        r = AuthResponse.parse_raw(resp.text)
        auth_time = dateutil.parser.parse(resp.headers['Date']).timestamp()
        user_info_resp = await requests.get(
            f'https://api.bgm.tv/user/{r.user_id}'
        )
        user_info = UserInfo.parse_raw(user_info_resp.text)
        await db.execute(
            db_models.UserToken.upsert(
                user_id=r.user_id,
                scope=r.scope or '',
                token_type=r.token_type,
                expires_in=r.expires_in,
                auth_time=auth_time,
                access_token=r.access_token,
                refresh_token=r.refresh_token,
                username=user_info.username,
                nickname=user_info.nickname,
                usergroup=user_info.usergroup
            )
        )

        session = await new_session(user_id=r.user_id, redis=redis)

        response = templates.TemplateResponse(
            'callback.html', {'request': request, 'data': json.dumps(r.dict())}
        )
        html_response = HTMLResponse(content=response.body)
        html_response.set_cookie(cookie_scheme.model.name, session.api_key)
        return html_response
    except json.decoder.JSONDecodeError:
        return RedirectResponse('./auth')
    except ValidationError:
        return RedirectResponse('./auth')


class RefreshResponse(BaseModel):
    access_token: str
    expires_in: int
    token_type: str
    scope: Optional[str] = ''
    refresh_token: str
    auth_time: int


@router.post(
    '/refresh',
    description='bgm.tv OAuth Callback, for userscript',
    response_model=RefreshResponse,
    include_in_schema=config.DEBUG,
)
async def refresh_token(
    db: Manager = Depends(get_db),
    current_user: db_models.UserToken = Depends(get_current_user),
):
    try:
        resp = await requests.post(
            'https://bgm.tv/oauth/access_token',
            data={
                'grant_type': 'refresh_token',
                'refresh_token': current_user.refresh_token,
                'client_id': config.BgmTvAutoTracker.APP_ID,
                'redirect_uri': config.BgmTvAutoTracker.callback_url,
                'client_secret': config.BgmTvAutoTracker.APP_SECRET,
            }
        )
        auth_time = dateutil.parser.parse(resp.headers['Date']).timestamp()
        resp = resp.json()
        resp['auth_time'] = auth_time
        resp = RefreshResponse.parse_obj(resp)
        await db.execute(
            db_models.UserToken.upsert(
                user_id=current_user.user_id,
                token_type=resp.token_type,
                scope=resp.scope or '',
                auth_time=auth_time,
                expires_in=resp.expires_in,
                access_token=resp.access_token,
                refresh_token=resp.refresh_token,
            )
        )
    except (
        requests.ConnectTimeout,
        requests.ConnectionError,
        json.decoder.JSONDecodeError,
        ValidationError,
    ):
        raise HTTPException(
            HTTP_502_BAD_GATEWAY, detail='refresh user token failure'
        )

    try:
        user_info_resp = await requests.get(
            f'https://api.bgm.tv/user/{current_user.user_id}'
        )
        user_info = UserInfo.parse_raw(user_info_resp.text)
        await db.execute(
            db_models.UserToken.upsert(
                user_id=current_user.user_id,
                username=user_info.username,
                nickname=user_info.nickname,
                usergroup=user_info.usergroup
            )
        )
    except (
        requests.ConnectTimeout,
        requests.ConnectionError,
        json.decoder.JSONDecodeError,
        ValidationError,
    ) as e:
        logger.exception(e)
    return resp


class Me(AuthResponse, RefreshResponse):
    pass


@router.get(
    '/me',
    response_model=Me,
    include_in_schema=config.DEBUG,
)
async def get_my_user_info(
    user: db_models.UserToken = Depends(get_current_user),
):
    return user.dict()
