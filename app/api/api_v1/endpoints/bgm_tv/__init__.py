# pylint: disable=C0103
import datetime
from collections import defaultdict

from fastapi import APIRouter, HTTPException
from icalendar import Event, Calendar

from app import aio_services
from app.responses import CalendarResponse
from app.models.errors import ErrorDetail

from .view_ip import router as view_ip_router

router = APIRouter()
router.include_router(view_ip_router, prefix='/view_ip')


@router.get(
    '/calendar/bgm.tv/{user_id}',
    summary='iCalendar for watching bangumi',
    response_class=CalendarResponse,
    responses={
        502: {'model': ErrorDetail},
        404: {'model': ErrorDetail},
    }
)
async def bgm_calendar(user_id: str):
    try:
        res = await aio_services.bgm_api.get_user_watching_subjects(user_id)
    except aio_services.ServerConnectionError:
        raise HTTPException(502, 'connect to bgm.tv error')
    if res is None:
        raise HTTPException(404, "username doesn't exists")

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

    weekday = datetime.datetime.now().weekday()
    for i, k in enumerate(range(weekday, weekday + 7)):
        if k % 7 in bangumi:
            for item in bangumi[k % 7]:
                event = Event()
                event.add('summary', item.name)
                event.add(
                    'dtstart',
                    datetime.datetime.now().date() + datetime.timedelta(i - 1)
                )
                event.add(
                    'dtend',
                    datetime.datetime.now().date() + datetime.timedelta(i - 1)
                )
                cal.add_component(event)

    return cal.to_ical().decode('utf8')
