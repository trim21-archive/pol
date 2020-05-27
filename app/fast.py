import os
import threading

import aiohttp
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from starlette.middleware import cors

from app.api import auth, bgm_tv
from app.log import logger
from app.core import config
from app.md2bbc import router as md2bbc_router
from app.db.mysql import database
from app.db.redis import setup_redis_pool
from app.deprecation import bind_deprecated_path
from app.api.api_v1.api import api_router
from app.middlewares.log import LogExceptionMiddleware
from app.middlewares.http import setup_http_middleware
from app.middlewares.sentry import setup_sentry

template = f"""出于兴趣写的一些api，源码见[GitHub](https://github.com/Trim21/pol)

当前版本[{config.COMMIT_REF}](https://github.com/Trim21/pol/tree/{config.COMMIT_REF})

[其他说明](https://github.com/Trim21/pol/tree/{config.COMMIT_REF}/docs)
"""

app = FastAPI(
    debug=config.DEBUG,
    title=config.APP_NAME,
    version=config.COMMIT_REF,
    docs_url=None,
    redoc_url=None,
    swagger_ui_oauth2_redirect_url=None,
    openapi_url="/openapi.json",
    description=template,
)

setup_sentry(app)
app.add_middleware(cors.CORSMiddleware, allow_origins="*")
setup_http_middleware(app)
app.add_middleware(LogExceptionMiddleware)
app.include_router(auth.router, prefix="/auth", tags=["auth"])
bind_deprecated_path(app)
app.include_router(api_router, prefix="/api.v1")
app.include_router(md2bbc_router)
app.include_router(bgm_tv.router, prefix="/bgm.tv", tags=["bgm.tv"])


@app.on_event("startup")
async def startup():
    app.state.db = database
    await database.connect()
    app.state.client_session = aiohttp.ClientSession(
        headers={"user-agent": config.REQUEST_SERVICE_USER_AGENT}
    )
    app.state.redis_pool = await setup_redis_pool()
    app.state.logger = logger
    app.state.logger.bind(
        event="startup", kwargs={"pid": os.getpid(), "thread": threading.get_ident(),},
    ).info(
        "server start at pid {}, tid {}", os.getpid(), threading.get_ident(),
    )


@app.on_event("shutdown")
async def shutdown():
    await app.state.db.disconnect()
    app.state.redis_pool.close()
    await app.state.redis_pool.wait_closed()
    await app.state.client_session.close()


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def doc():
    return """
    <!DOCTYPE html>
    <html lang=zh-cmn-Hans>
    <head>
    <link type="text/css" rel="stylesheet"
        href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@3/swagger-ui.css">
    <link rel="shortcut icon" href="https://blog.trim21.cn/favicon.ico">
    <title>Pol server - Swagger UI</title>
    </head>
    <body>
    <div id="swagger-ui"></div>
    <hr>
    <div class='wrapper'' style='text-align: center'>
        <a href="http://beian.miit.gov.cn/">鲁ICP备16017566号-1</a>
    </div>
    <script
        src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@3/swagger-ui-bundle.js">
    </script>
    <!-- `SwaggerUIBundle` is now available on the page -->
    <script>
    const ui = SwaggerUIBundle({
        url: '/openapi.json',

        dom_id: '#swagger-ui',
        presets: [
        SwaggerUIBundle.presets.apis,
        SwaggerUIBundle.SwaggerUIStandalonePreset
        ],
        layout: "BaseLayout",
        deepLinking: true
    })
    </script>
    </body>
    </html>
    """
