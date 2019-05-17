# pylint: disable=C0103
import datetime
from datetime import datetime

import icalendar
import pytz
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
    event = icalendar.Event()
    event['name'] = '课表日历停止维护提醒'
    event['dtstart'] = icalendar.vDatetime(
        datetime.today().replace(hour=0).astimezone(UTC_TZ)
    ).to_ical()
    event['dtend'] = icalendar.vDatetime(
        datetime.today().replace(hour=23).astimezone(UTC_TZ)
    ).to_ical()
    event['description'] = '由于本人已经毕业，所以本项目不再维护，请取消订阅本日历，或从github获取代码自己部署'
    calc.add_component(event)

    return calc.to_ical()
