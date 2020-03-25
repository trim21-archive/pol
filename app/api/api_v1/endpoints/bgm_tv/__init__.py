from datetime import datetime, timedelta
from collections import defaultdict

import async_bgm_api.models
import async_bgm_api.exceptions
from fastapi import APIRouter, HTTPException
from icalendar import Event, Calendar

from app import aio_services
from app.res import CalendarResponse, response
from app.models.errors import ErrorDetail

from .view_ip import router as view_ip_router

router = APIRouter()
router.include_router(view_ip_router, prefix='/view_ip')


@router.get(
    '/calendar/bgm.tv/{user_id}',
    summary='iCalendar for watching bangumi',
    response_class=CalendarResponse,
    responses={
        404: response(model=ErrorDetail, description='user not existing'),
        502: response(
            model=ErrorDetail, description='bgm.tv mirror site not reachable'
        ),
    }
)
async def bgm_calendar(user_id: str):
    try:
        res = await aio_services.bgm_api_mirror.get_user_collection(
            user_id, async_bgm_api.models.CollectionCat.watching
        )
    except async_bgm_api.exceptions.RecordNotFound:
        raise HTTPException(404, "username doesn't exists")
    except async_bgm_api.exceptions.ServerConnectionError:
        raise HTTPException(502, 'could not fetch user data from bgm.tv')

    cal = Calendar()
    cal.add('prodid', '-//trim21//www.trim21.cn//')
    cal.add('version', '2.0')
    cal.add('name', 'Followed Bangumi Calendar')
    cal.add('description', 'Followed Bangumi Calendar')
    cal.add('X-WR-CALNAM', 'Followed Bangumi Calendar')
    cal.add('X-WR-CALDESC', 'Followed Bangumi Calendar')
    bangumi = defaultdict(list)
    for item in res:
        bangumi[item.subject.air_weekday].append(item)

    weekday = datetime.now().weekday()
    for i, k in enumerate(range(weekday, weekday + 7)):
        if k % 7 in bangumi:
            for item in bangumi[k % 7]:
                event = Event()
                event.add('summary', item.name)
                event.add('dtstart', datetime.now().date() + timedelta(i - 1))
                event.add('dtend', datetime.now().date() + timedelta(i - 1))
                cal.add_component(event)

    return cal.to_ical().decode('utf8')
