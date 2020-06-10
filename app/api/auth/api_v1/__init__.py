import json
from urllib.parse import urlencode

import aiohttp
import dateutil.parser
from fastapi import Depends, APIRouter
from pydantic import ValidationError
from aiologger import Logger
from databases import Database
from starlette.status import HTTP_502_BAD_GATEWAY, HTTP_503_SERVICE_UNAVAILABLE
from starlette.responses import HTMLResponse, RedirectResponse
from starlette.exceptions import HTTPException

from app import res
from app.res import ORJSONResponse
from app.core import config
from app.models import ErrorDetail
from app.depends import get_logger, aiohttp_session
from app.db.redis import PickleRedis
from app.db.utils import preserve_fields
from app.db_models import sa
from app.db.depends import get_db, get_redis
from app.services.bgm_tv.model import UserInfo, AuthResponse
from app.services.bgm_tv.model import RefreshResponse as _RefreshResponse
from app.api.auth.api_v1.models import FinishAuth
from app.api.auth.api_v1.scheme import cookie_scheme
from app.api.auth.api_v1.depends import get_current_user
from app.api.auth.api_v1.session import new_session

CALLBACK_URL = (
    f"{config.PROTOCOL}://{config.VIRTUAL_HOST}" f"/auth/api.v1/bgm.tv_oauth_callback"
)

OAUTH_URL = "https://bgm.tv/oauth/authorize?" + urlencode(
    {
        "client_id": config.BgmTvAutoTracker.APP_ID,
        "response_type": "code",
        "redirect_uri": CALLBACK_URL,
    }
)

router = APIRouter()


@router.get(
    "/bgm.tv_auth",
    description="如果需要授权, 客户端应该把用户转跳到此地址让用户进行授权\n\n会把用户转跳到bgm真正的授权页面",
    summary="login with bgm.tv oauth",
    status_code=307,
    response_class=HTMLResponse,
)
async def auth_redirect():
    return RedirectResponse(OAUTH_URL)


@router.get(
    "/bgm.tv_oauth_callback",
    description=(
        "bgm.tv OAuth callback\n\n"
        "应该在用户使用bgm授权后转跳, 而非客户端主动调用\n\n"
        "会设置一个cookies, 做为后续请求的认证方式\n\n"
        "并不会在任何情况下返回422请求, 如果缺失了query中的code会被转跳到认证页面."
    ),
    response_model=FinishAuth,
    response_description="授权成功时, 会设置cookies. 在对应cookies存在的情况下不需要把返回的`api_key`放在请求头中",
    responses={
        200: res.response(
            headers={"set-cookies": res.header(str, "会设置cookies, 后续请求会自动通过认证.")},
        ),
        302: res.response(
            cls=ORJSONResponse, description="如果授权不成功, 如服务器返回502等, 会将用户转跳会bgm.tv重新进行授权",
        ),
        503: res.response(
            model=ErrorDetail, description="bgm.tv unreachable", cls=ORJSONResponse
        ),
    },
)
async def oauth_callback(
    code: str = None,
    db: Database = Depends(get_db),
    redis: PickleRedis = Depends(get_redis),
    aio_client: aiohttp.ClientSession = Depends(aiohttp_session),
):
    redirect_response = RedirectResponse("./bgm.tv_auth")
    if code is None:
        return redirect_response
    try:
        async with aio_client.post(
            "https://bgm.tv/oauth/access_token",
            data={
                "code": code,
                "client_id": config.BgmTvAutoTracker.APP_ID,
                "grant_type": "authorization_code",
                "redirect_uri": CALLBACK_URL,
                "client_secret": config.BgmTvAutoTracker.APP_SECRET,
            },
        ) as auth_resp:
            auth_time = dateutil.parser.parse(auth_resp.headers["Date"]).timestamp()
            auth_response = AuthResponse.parse_obj(await auth_resp.json())
        async with await aio_client.get(
            f"https://mirror.api.bgm.rin.cat/user/{auth_response.user_id}"
        ) as user_info_resp:
            user_info = UserInfo.parse_obj(await user_info_resp.json())

        user = Me(auth_time=auth_time, **auth_response.dict())

        insert_stmt = sa.insert(sa.UserToken)

        query = insert_stmt.on_duplicate_key_update(
            **preserve_fields(
                insert_stmt,
                "token_type",
                "expires_in",
                "auth_time",
                "access_token",
                "refresh_token",
                "scope",
                "username",
                "nickname",
                "usergroup",
            ),
        )

        await db.execute(
            query,
            {
                "user_id": user.user_id,
                "token_type": user.token_type,
                "expires_in": user.expires_in,
                "auth_time": user.auth_time,
                "access_token": user.access_token,
                "refresh_token": user.refresh_token,
                "scope": auth_response.scope or "",
                "username": user_info.username,
                "nickname": user_info.nickname,
                "usergroup": user_info.usergroup.value,
            },
        )

        session = await new_session(user_id=auth_response.user_id, redis=redis)
        response = ORJSONResponse({"api_key": session.api_key})
        response.set_cookie(cookie_scheme.model.name, session.api_key)
        return response

    except aiohttp.ServerTimeoutError:
        return ORJSONResponse(
            content={"detail": "connect to bgm.tv timeout"},
            status_code=HTTP_503_SERVICE_UNAVAILABLE,
        )

    except (
        json.decoder.JSONDecodeError,
        ValidationError,
        ConnectionError,
        aiohttp.ServerConnectionError,
    ):
        return redirect_response


class RefreshResponse(_RefreshResponse):
    auth_time: int


@router.post(
    "/bgm.tv_refresh",
    description="bgm.tv OAuth Refresh, for UserScript",
    response_model=RefreshResponse,
)
async def refresh_token(
    db: Database = Depends(get_db),
    current_user: sa.UserToken = Depends(get_current_user),
    aio_client: aiohttp.ClientSession = Depends(aiohttp_session),
    logger: Logger = Depends(get_logger),
):
    try:
        async with aio_client.post(
            "https://bgm.tv/oauth/access_token",
            data={
                "grant_type": "refresh_token",
                "refresh_token": current_user.refresh_token,
                "client_id": config.BgmTvAutoTracker.APP_ID,
                "redirect_uri": config.BgmTvAutoTracker.callback_url,
                "client_secret": config.BgmTvAutoTracker.APP_SECRET,
            },
        ) as resp:
            auth_time = dateutil.parser.parse(resp.headers["Date"]).timestamp()
            refresh_resp = RefreshResponse(auth_time=auth_time, **await resp.json())
        query = sa.update(
            sa.UserToken,
            sa.UserToken.user_id == current_user.user_id,
            values={
                "token_type": refresh_resp.token_type,
                "scope": refresh_resp.scope or "",
                "auth_time": auth_time,
                "expires_in": refresh_resp.expires_in,
                "access_token": refresh_resp.access_token,
                "refresh_token": refresh_resp.refresh_token,
            },
        )
        await db.execute(query)

    except (
        aiohttp.ServerTimeoutError,
        json.decoder.JSONDecodeError,
        ValidationError,
    ):
        raise HTTPException(HTTP_502_BAD_GATEWAY, detail="refresh user token failure")

    try:
        async with aio_client.get(
            f"https://mirror.api.bgm.rin.cat/user/{current_user.user_id}"
        ) as user_info_resp:
            user_info = UserInfo.parse_raw(await user_info_resp.read())
        query = sa.update(
            sa.UserToken,
            sa.UserToken.user_id == current_user.user_id,
            values={
                "username": user_info.username,
                "nickname": user_info.nickname,
                "usergroup": user_info.usergroup.value,
            },
        )
        await db.execute(query)
    except (
        aiohttp.ServerTimeoutError,
        json.decoder.JSONDecodeError,
        ValidationError,
    ) as e:
        logger.exception(e)
    return refresh_resp


class Me(AuthResponse, RefreshResponse):
    pass


@router.get(
    "/me", response_model=Me, include_in_schema=config.DEBUG,
)
async def get_my_user_info(user: sa.UserToken = Depends(get_current_user)):
    return user.dict()
