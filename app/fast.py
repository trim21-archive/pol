from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import RedirectResponse

from app.api.api_v1.api import api_router
from app.db.session import Session
from app.deprecation import bind_deprecated_path
from app.md2bbc import router as md2bbc_router

app = FastAPI(title='personal website', openapi_url='/api/v1/openapi.json')
bind_deprecated_path(app)


@app.middleware('http')
async def db_session_middleware(request: Request, call_next):
    request.state.db = Session()
    response = await call_next(request)
    request.state.db.close()
    return response


@app.get('/', include_in_schema=False)
def redirect():
    return RedirectResponse('/docs')


app.include_router(api_router, prefix='/api.v1')
app.include_router(md2bbc_router)
