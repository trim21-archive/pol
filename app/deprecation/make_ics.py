from datetime import datetime, timedelta

import pytz
import icalendar
from fastapi import APIRouter

from app.responses import CalendarResponse

router = APIRouter()
UTC_TZ = pytz.timezone('UTC')


@router.get(
    '/calendar/{auth}',
    response_class=CalendarResponse,
    deprecated=True,
)
async def calendar():
    calc = icalendar.Calendar()
    calc['prodid'] = 'Trim21'
    calc['version'] = '2.0'
    calc['X-WR-CALNAME'] = '课表'
    today = datetime.today()
    for i in range(-1, 3):
        event = icalendar.Event()
        event['name'] = '课表日历停止维护提醒'
        event['dtstart'] = icalendar.vDatetime(
            datetime(
                year=today.year,
                month=today.month,
                day=today.day,
                hour=0,
            ).astimezone(UTC_TZ) + timedelta(days=i)
        ).to_ical()
        event['dtend'] = icalendar.vDatetime(
            datetime(
                year=today.year,
                month=today.month,
                day=today.day,
                hour=23,
            ).astimezone(UTC_TZ) + timedelta(days=i)
        ).to_ical()
        event['description'] = '本项目不再维护，请取消订阅本日历'
        calc.add_component(event)
    return calc.to_ical()
