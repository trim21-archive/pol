from fastapi import APIRouter

from app.api import bgm_tv_auto_tracker

api_router = APIRouter()
api_router.include_router(
    bgm_tv_auto_tracker.router,
    prefix='/bgm_tv_auto_tracker',
    tags=['bgm_tv_spider-tv-auto-tracker', 'unstable'],
)
