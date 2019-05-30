from fastapi import APIRouter

from . import app_v0, app_v1

router = APIRouter()
router.include_router(app_v0.router, prefix='/api.v0')
router.include_router(app_v1.router, prefix='/api.v1')
