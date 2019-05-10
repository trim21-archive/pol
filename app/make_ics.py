from datetime import date, datetime

import icalendar
import pytz

UTC_TZ = pytz.timezone('UTC')


def calendar() -> str:
    c = icalendar.Calendar()
    c['prodid'] = 'Trim21'
    c['version'] = '2.0'
    c['X-WR-CALNAME'] = '课表'
    event = icalendar.Event()
    event['name'] = '课表日历停止维护提醒'
    event['dtstart'] = icalendar.vDatetime(
        datetime.today().replace(hour=0).astimezone(UTC_TZ)
    ).to_ical()
    event['dtend'] = icalendar.vDatetime(
        datetime.today().replace(hour=23).astimezone(UTC_TZ)
    ).to_ical()
    event['description'] = '由于本人已经毕业，所以本项目不再维护，请取消订阅本日历，或从github获取代码自己部署'
    c.add_component(event)
    return c.to_ical()
