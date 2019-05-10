from datetime import datetime

import pytz

import icalendar
from flask import make_response, request

UTC_TZ = pytz.timezone('UTC')


def calendar(auth):
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

    response = make_response(calc.to_ical())
    if request.user_agent.string.find('Mozilla') != -1:
        response.headers['Content-Type'] = 'text/plain;charset=UTF-8'
    else:
        response.headers['Content-Type'] = 'text/calendar;charset=UTF-8'
    return response, 200
