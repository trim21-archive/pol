from fastapi import APIRouter
from fastapi.responses import RedirectResponse

from app.res import response
from .view_ip import router as view_ip_router

router = APIRouter()
router.include_router(view_ip_router, prefix="/view_ip")


@router.get(
    "/calendar/bgm.tv/{user_id}",
    description="go to <https://bgm.tv/group/topic/355388>",
    deprecated=True,
    status_code=307,
    responses={307: response(description="redirect to new api address")},
)
async def bgm_calendar(user_id: str):
    return RedirectResponse(f"https://api.bgm38.com/bgm.tv/v1/calendar/{user_id}")
