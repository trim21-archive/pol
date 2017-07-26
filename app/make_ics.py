from datetime import date, timedelta, time, datetime
import uuid
import re
import pytz
from ics import Calendar, Event
from icalendar import Calendar as iCalendar
import icalendar
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


def make_dict(lesson, start_date, if_summer):
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


def lesson_to_event(lesson: dict) -> list:
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
            events_box.append(make_dict(lesson, start_date, if_summer))

    tmp = list()
    for event in events_box:
        e = Event()
        e.name = event['name']
        e.begin = event['begin']
        e.end = event['end']
        e.location = event['location']
        tmp.append(e)
    return tmp


def from_lesson_to_ics(lessons: list):
    event_box = list()
    for lesson in lessons:
        for event in lesson_to_event(lesson):
            event_box.append(event)
    return event_list_to_ics(event_box, '山大课表')


def exam_to_event(exam: dict):
    sjsj_regex = re.compile(r"(\d*)年(\d*)月(\d*)日(.*)-(.*)")
    time_regex = re.compile(r"(\d*):(\d*)")
    year, month, day, start_time, end_time = sjsj_regex.findall(exam['sjsj'])[0]
    start_hour, start_minute = time_regex.findall(start_time)[0]
    end_hour, end_minute = time_regex.findall(end_time)[0]
    year = int(year)
    month = int(month)
    day = int(day)
    start_hour = int(start_hour)
    start_minute = int(start_minute)
    end_hour = int(end_hour)
    end_minute = int(end_minute)
    start_time = datetime(year, month, day, start_hour, start_minute, tzinfo=pytz.timezone('Asia/Shanghai'))
    end_time = datetime(year, month, day, end_hour, end_minute, tzinfo=pytz.timezone('Asia/Shanghai'))
    e = icalendar.Event()
    e['dtstart'] = icalendar.vDatetime(start_time).to_ical()
    e['dtend'] = icalendar.vDatetime(end_time).to_ical()
    e['summary'] = exam['kcm']
    e['location'] = exam['xqmc'] + exam['jxljs']
    e['description'] = '{} {} {}  {} {}  {} {}  {}'.format(exam['kcm'], exam['sjsj'],
                                                           exam['xqmc'], exam['jxlm'], exam['jxljs'],
                                                           exam['ksfsmc'], exam['ksffmc'],
                                                           '' if not exam['ksbz'] else exam['ksbz'])
    e['uid'] = uuid.uuid4()
    return e


def from_exam_to_ics(exams: list) -> str:
    c = icalendar.Calendar()
    c['summary'] = '考试安排'
    c['prodid'] = 'Trim21'
    c['version'] = '2.0'
    c['X-WR-CALNAME'] = '考试安排'
    for exam in exams:
        c.add_component(exam_to_event(exam))
    return c.to_ical()


def event_list_to_ics(events: list, ics_name: str):
    c = Calendar(events=events, creator='Trim21')
    s = str(c)
    cal = iCalendar.from_ical(s.replace('\n', '\r\n'))
    cal['X-WR-CALNAME'] = ics_name
    return cal.to_ical()
