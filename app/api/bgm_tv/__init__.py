# pylint: disable=C0103
import datetime
from collections import defaultdict
import requests
from icalendar import Calendar, Event


def bgm_calendar(user_id):
    res = requests.get(
        f'https://mirror.api.bgm.rin.cat/user/{user_id}/collection',
        {
            'cat': 'watching',
        },
    ).json()
    if 'code' in res:
        return "username doesn't exists", 404

    cal = Calendar()
    cal.add('prodid', '-//trim21//www.trim21.cn//')
    cal.add('version', '2.0')
    cal.add('name', 'Followed Bangumi Calendar')
    cal.add('description', 'Followed Bangumi Calendar')
    cal.add('X-WR-CALNAM', 'Followed Bangumi Calendar')
    cal.add('X-WR-CALDESC', 'Followed Bangumi Calendar')
    bangumi = defaultdict(list)
    for item in res:
        bangumi[item['subject']['air_weekday']].append(item)

    weekday = datetime.datetime.now().weekday()
    for i, k in enumerate(range(weekday, weekday + 7)):
        if k % 7 in bangumi:
            for item in bangumi[k % 7]:
                event = Event()
                event.add('summary', item['name'])
                event.add(
                    'dtstart',
                    datetime.datetime.now().date() + datetime.timedelta(i - 1)
                )
                event.add(
                    'dtend',
                    datetime.datetime.now().date() + datetime.timedelta(i - 1)
                )
                cal.add_component(event)
    return cal.to_ical().decode('utf8'), 200, {
        'content-type': 'text/calendar; charset=utf-8',
    }
