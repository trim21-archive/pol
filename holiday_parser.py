import requests
import icalendar
from datetime import datetime
from glob import glob


def get_calendar_text():
    if not glob('./ics'):
        with open('./ics', 'w+', encoding='utf8') as f:
            ics_text = requests.get('https://p42-calendars.icloud.com/published/2'
                                    '/nbjx744gis1ym0gytzefog4u4wifrcfg81sdjqajtlbifmccal2rlbq'
                                    '-tx2tslz3aw2fzkrds2idpbiiuv2r1fzfhnilocaqegcxoktavua').text
            f.write(ics_text)
    else:
        with open('./ics', 'r', encoding='utf8') as f:
            ics_text = f.read()
    return ics_text


def is_holiday(dt: datetime.date):
    ic = icalendar.Calendar.from_ical(get_calendar_text())
    print(dt)
    for event in ic.subcomponents:
        if str(event['summary']).find('假期') != -1:
            start = event['dtstart'].dt
            end = event['dtend'].dt
            if start <= dt < end:
                return True
    return False
