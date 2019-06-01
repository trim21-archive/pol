import json.decoder
from enum import IntEnum
from pathlib import Path
from typing import Dict, Optional

import dateutil.parser
import requests_async as requests
from fastapi import APIRouter, Depends
from peewee_async import Manager
from pydantic import BaseModel, ValidationError
from starlette.requests import Request
from starlette.responses import RedirectResponse
from starlette.templating import Jinja2Templates

from app import curd, db_models
from app.api.bgm_tv_auto_tracker.auth import get_current_user
from app.api.bgm_tv_auto_tracker.auth.scheme import cookie_scheme
from app.api.bgm_tv_auto_tracker.auth.session import new_session
from app.core import config
from app.db.depends import get_db, get_redis
from app.db.redis import PickleRedis

templates = Jinja2Templates(str(Path(__file__) / '..' / 'templates'))

router = APIRouter()


@router.get(
    '/auth',
    description='redirect user to bgm_tv_spider.tv OAuth page',
    include_in_schema=False,
)
async def auth_redirect():
    return RedirectResponse(config.BgmTvAutoTracker.oauth_url)


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
    description='bgm_tv_spider.tv OAuth callback',
    include_in_schema=False,
)
async def auth_redirect(
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
            }
        )
        r = AuthResponse.parse_raw(resp.text)
        auth_time = dateutil.parser.parse(resp.headers['Date']).timestamp()
        user_info_resp = await requests.get(
            f'https://api.bgm.tv/user/{r.user_id}'
        )
        user_info = UserInfo.parse_raw(user_info_resp.text)
        await db.execute(
            curd.user_token.UserToken.replace(
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
        response.set_cookie(cookie_scheme.model.name, session.api_key)
        return response
    except json.decoder.JSONDecodeError as e:
        print(e)
        return RedirectResponse('./auth')
    except ValidationError as e:
        print(e)
        return RedirectResponse('./auth')


class RefreshResponse(BaseModel):
    access_token: str
    expires_in: int
    token_type: str
    scope: Optional[str]
    refresh_token: str
    auth_time: int


@router.post(
    '/refresh',
    description='bgm_tv_spider.tv OAuth Callback',
    response_model=RefreshResponse,
    include_in_schema=False,
)
async def auth_redirect(
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

        user_info_resp = await requests.get(
            f'https://api.bgm.tv/user/{current_user.user_id}'
        )
        user_info = UserInfo.parse_raw(user_info_resp.text)
        await db.execute(
            db_models.UserToken.replace(
                user_id=current_user.user_id,
                token_type=resp.token_type,
                scope=resp.scope or '',
                auth_time=auth_time,
                expires_in=resp.expires_in,
                access_token=resp.access_token,
                refresh_token=resp.refresh_token,
                username=user_info.username,
                nickname=user_info.nickname,
                usergroup=user_info.usergroup
            )
        )
        return resp
    except json.decoder.JSONDecodeError as e:
        raise e
    except ValidationError as e:
        raise e


@router.get('/me', response_model=AuthResponse, include_in_schema=False)
async def get_my_user_info(
    user: db_models.UserToken = Depends(get_current_user),
):
    return user.dict()
