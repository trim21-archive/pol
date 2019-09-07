from fastapi import APIRouter

from app.api.bgm_tv_auto_tracker.api_v1 import auth, user_submit

from . import api_v1

router = APIRouter()
router.include_router(api_v1.router, prefix='/api.v1', tags=['bgm-tv-auto-tracker'])
router.include_router(
    user_submit.router,
    prefix='/api.v1',
    tags=['bgm-tv-auto-tracker-userscript'],
)
router.include_router(
    auth.router,
    prefix='/api.v1',
    tags=['bgm-tv-auto-tracker-userscript'],
)
