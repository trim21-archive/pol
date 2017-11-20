import base64
import binascii
import functools
import json
from datetime import date
from itertools import combinations

import sdu_bkjws
from flask import Flask, request, make_response, render_template

import make_ics

app = Flask(__name__)


def parserAuth(fn):
    @functools.wraps(fn)
    def wrapper(auth=None):
        try:
            if not auth:
                auth = request.cookies.get('auth', '')
                auth = request.args.get('auth', auth)
            if auth:
                auth = auth.replace('@', '=')
                auth = base64.b64decode(auth).decode()
            else:
                return 'This page does not exist', 404
        except binascii.Error:
            return make_response('error'), 404
        try:
            auth = json.loads(auth)
        except json.JSONDecodeError:
            return make_response('error'), 404
        try:
            print(auth)
            username = auth['username']
            password = auth['password']
            s = sdu_bkjws.SduBkjws(username, password)
            return fn(s)
        except Exception as e:
            resp = make_response(
                json.dumps({'error': str(e)}))
            return resp, 401

    return wrapper


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/menu', methods=['POST', ])
def menu():
    student_id = request.form.get('student_id', None)
    password = request.form.get('password', None)
    if student_id and password:
        try:
            s = sdu_bkjws.SduBkjws(student_id, password)
            resp = make_response(render_template('menu.html'))
            auth = base64.b64encode(json.dumps({'username': student_id, 'password': password}).encode()).decode()

            resp.set_cookie('auth', auth)
            return resp
        except Exception as e:
            return str(e) + '<a href="/"> go back </a>', 401


@app.route('/exam-result')
@parserAuth
def examResult(s: sdu_bkjws.SduBkjws):
    result = s.get_fail_score() + s.get_now_score() + s.get_past_score()
    for lesson in result:
        try:
            if float(lesson['kscjView']) < 60.0:
                lesson['pass'] = False
            else:
                lesson['pass'] = True
        except ValueError:
            if lesson['kscjView'] == '不及格':
                lesson['pass'] = False
            else:
                lesson['pass'] = True
    result.reverse()
    for d1, d2 in combinations(result, 2):
        a = list(set(d1.items()) ^ set(d2.items()))
        if len(a) == 0:
            i = result.index(d1)
            result.pop(i)
    result.reverse()
    # result = list(set(result))
    resp = make_response(render_template('scores.html', lessons=result))

    return resp
    # return json.dumps(result, ensure_ascii=False,
    #                   sort_keys=True)


@app.route('/curriculum')
@parserAuth
def manyUser(s: sdu_bkjws.SduBkjws):
    x = make_ics.from_lesson_to_ics(s.get_lesson())
    resp = make_response(x)
    resp.headers['Content-Type'] = "text/calendar;charset=UTF-8"
    return resp


@app.route('/calendar')
def calendar_menu():
    auth = request.cookies.get('auth', False)
    if not auth:
        return render_template('index.html')
    return render_template('calendar.html', auth=auth)


@app.route('/calendar/<auth>')
@parserAuth
def calendar(s):
    try:
        query = {'curriculum': True, 'exam': False}
        r = make_ics.calendar(s, query)
        r = make_response(r)
        if request.user_agent.string.find('Mozilla') != -1:
            r.headers['Content-Type'] = "text/plain;charset=UTF-8"
        else:
            r.headers['Content-Type'] = "text/calendar;charset=UTF-8"
        return r, 200
    except Exception as e:
        resp = make_response(
            json.dumps({'error': 233}))
        return resp, 401


@app.route('/exam-arrangement')
@parserAuth
def exam(s: sdu_bkjws.SduBkjws):
    today = date.today()
    if today.month <= 2:
        xq = 1
        year = today.year - 1
    elif 2 < today.month < 8:
        xq = 2
        year = today.year - 1
    else:
        xq = 1
        year = today.year
    xnxq = '{}-{}-{}'.format(year, year + 1, xq)
    e = s.get_exam_time(xnxq)
    ics = make_ics.from_exam_to_ics(e)
    resp = make_response(ics)
    resp.headers['Content-Type'] = "text/calendar;charset=UTF-8"
    return resp


@app.errorhandler(404)
def page_not_found(error):
    return 'This page does not exist', 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=800)
