import re
from datetime import date, timedelta, time, datetime
from bs4 import BeautifulSoup, element
import requests
from ics import Calendar, Event


def get_lessen_html(student_ID: str, password: str):
    s = requests.session()
    s.get('http://bkjws.sdu.edu.cn')
    data = {
        'j_username': student_ID,
        'j_password': password
    }
    r6 = s.post('http://bkjws.sdu.edu.cn/b/ajaxLogin', data=data)
    if r6.text == '"success"':
        requests.utils.add_dict_to_cookiejar(s.cookies, data)
        r3 = s.get('http://bkjws.sdu.edu.cn/f/xk/xs/bxqkb')
        return r3.text
    else:
        return False


config = {
    "firstMonday": date(2017, 2, 20),
    "end": date(2017, 6, 26)
}

holiday_list = list()
holiday_list += [date(2017, 4, x) for x in range(2, 5)]
holiday_list += [date(2017, 5, x) for x in range(28, 31)]
holiday_list.append(date(2017, 5, 1))


def tr_parser(tr: element.Tag) -> dict:
    td_box = tr.find_all('td')
    return {"lesson_num_long": td_box[1].text,
            "lesson_name": td_box[2].text,
            "lesson_num_short": td_box[3].text,
            "credit": td_box[4].text,
            "school": td_box[6].text,
            "teacher": td_box[7].text,
            "weeks": td_box[8].text,
            "days": td_box[9].text,
            "times": td_box[10].text,
            "place": td_box[11].text}


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
    # ======================== 人工干预
    # if calendar_time == date(2016, 10, 6):
    #     calendar_time = date(2016, 10, 8)
    # elif calendar_time == date(2016, 10, 7):
    #     calendar_time = date(2016, 10, 9)
    # ========================
    calendar_time.strftime('%m/%d/%Y')
    if calendar_time < date(2016, 10, 1) and calendar_time > date(2016, 5, 3):
        if_summer = True
    else:
        if_summer = False
    if_holiday = True if calendar_time in holiday_list else False
    if_term = True if calendar_time < config['end'] else False
    return (calendar_time, if_summer, if_holiday, if_term)


def makeDict(lesson, start_date, if_summer):
    start_time, end_time = times_wrapper(
        lesson['times'], summer=if_summer)
    begin = datetime.fromtimestamp((datetime.combine(start_date, start_time) - timedelta(hours=8)).timestamp())
    end = datetime.fromtimestamp((datetime.combine(start_date, end_time) - timedelta(hours=8)).timestamp())
    return {"name": lesson["lesson_name"],
            'begin': begin,
            'end': end,
            "location": lesson["place"], }


def lesson_to_calendar(lesson: dict) -> list:
    events_box = list()
    holiday = 0
    for i in (i for i in range(len(lesson['weeks'])) if lesson['weeks'][i] == '1'):
        start_date, if_summer, if_holiday, if_term = days_wrapper(i, lesson[
            'days'])
        if if_holiday:
            holiday += 1
        elif if_term:
            events_box.append(makeDict(lesson, start_date, if_summer))
    weeks = lesson['weeks']
    while holiday > 0:
        holiday -= 1
        if not re.search('111', weeks):
            week = re.search('100+', weeks).start() + 2
            weeks = weeks[0:week] + '1' + weeks[week + 1:-1]
            start_date, if_summer, if_holiday, if_term = days_wrapper(
                week, lesson['days'])
            if if_holiday:
                holiday += 1
            elif if_term:
                events_box.append(makeDict(lesson, start_date, if_summer))
        else:
            week = re.search('100+', weeks).start() + 2
            weeks = weeks[0:week] + '1' + weeks[week - 1:-1]
            start_date, if_summer, if_holiday, if_term = days_wrapper(
                week, lesson['days'])
            if if_holiday:
                holiday += 1
            elif if_term:
                events_box.append(makeDict(lesson, start_date, if_summer))

    tmp = list()
    # print(events_box)
    for event in events_box:
        e = Event()
        e.name = event['name']
        e.begin = event['begin']
        e.end = event['end']
        e.location = event['location']
        print(event)
        print(e.begin, e.end, e.duration)
        tmp.append(e)
    return tmp


def makeiCs(stuid, passwd):
    stuid = str(stuid)
    passwd = str(passwd)

    r = get_lessen_html(stuid, passwd)
    if r:
        try:
            soup = BeautifulSoup(r, "html.parser")
            s = soup.find('table',
                          attrs={"class": "table table-striped table-bordered table-hover",
                                 "id": "ysjddDataTableId"})
            tr_box = s.find_all('tr')
            c = Calendar()

            for les in tr_box[1:]:
                # print(les)
                for event in lesson_to_calendar(tr_parser(les)):
                    c.events.append(event)

            # with open('my.ics', 'w', encoding='utf-8') as f:
            #     f.writelines(c)
            return str(c)
        except:
            return False
    else:
        return False
