import re
from datetime import date, timedelta, time, datetime

from ics import Calendar, Event
from icalendar import Calendar as iCalendar
from sdu_bkjws import SduBkjws
from holiday_parser import is_holiday


config = {
    "firstMonday": date(2017, 9, 11),
    "end": date(2018, 1, 15)
}

holiday_list = list()
holiday_list += [date(2017, 1, x) for x in range(1, 8)]
holiday_list.append(date(2018, 1, 1))


def times_wrapper(x: str, summer=False):
    if summer:
        time_dict = {'1': (time(8, 0), time(9, 50)),
                     '2': (time(10, 10), time(12)),
                     '3': (time(14), time(15, 50)),
                     '4': (time(16), time(17, 50)),
                     '5': (time(19), time(20, 50))}
    else:
        time_dict = {'1': (time(8, 0), time(9, 50)),
                     '2': (time(10, 10), time(12)),
                     '3': (time(13, 30), time(15, 20)),
                     '4': (time(15, 30), time(17, 20)),
                     '5': (time(18, 30), time(20, 20))}
    return time_dict[x]


def days_wrapper(week: int, days: str) -> tuple:
    days = int(days) - 1
    calendar_time = config["firstMonday"] + timedelta(weeks=week, days=days)
    # calendar_time.strftime('%m/%d/%Y')
    if date(2017, 5, 1) < calendar_time < date(2017, 10, 1):
        if_summer = True
    else:
        if_summer = False
    if_holiday = is_holiday(calendar_time)
    if_term = calendar_time < config['end']
    return calendar_time, if_summer, if_holiday, if_term


def makeDict(lesson, start_date, if_summer):
    start_time, end_time = times_wrapper(
        lesson['times'], summer=if_summer)
    begin = datetime.fromtimestamp(
        (datetime.combine(start_date, start_time) - timedelta(hours=8)).timestamp())
    end = datetime.fromtimestamp(
        (datetime.combine(start_date, end_time) - timedelta(hours=8)).timestamp())
    return {"name": lesson["lesson_name"],
            'begin': begin,
            'end': end,
            "location": lesson["place"], }


def lesson_to_calendar(lesson: dict) -> list:
    events_box = list()
    week = list(lesson['weeks'])
    for index, value in enumerate(week):
        start_date, if_summer, if_holiday, if_term = days_wrapper(index, lesson['days'])
        if if_holiday:
            week[index] = False
        elif not if_term:
            week[index] = False
        elif value:
            week[index] = True
        else:
            week[index] = True
        if week[index]:
            events_box.append(makeDict(lesson, start_date, if_summer))

    tmp = list()
    for event in events_box:
        e = Event()
        e.name = event['name']
        e.begin = event['begin']
        e.end = event['end']
        e.location = event['location']
        tmp.append(e)
    return tmp


def makeICS(s: SduBkjws):
    lessons = s.get_lesson()
    if lessons:
        c = Calendar()
        for lesson in lessons:
            for event in lesson_to_calendar(lesson):
                c.events.append(event)
        c.creator = 'Trim21'
        s = str(c)
        cal = iCalendar.from_ical(s.replace('\n', '\r\n'))
        cal['X-WR-CALNAME'] = '山大课表'
        return cal.to_ical()
    else:
        return False
