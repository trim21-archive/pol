from fastapi import APIRouter
from starlette.responses import HTMLResponse

router = APIRouter()


@router.get(
    '/md2bbc',
    deprecated=True,
    description="go to <https://bgm.tv/group/topic/355388>",
    response_class=HTMLResponse,
)
async def md2bbc():
    url = 'https://bgm.tv/group/topic/355388'
    return f"<a href={url}>{url}</a>"
