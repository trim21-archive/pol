import base64
import binascii
import datetime
import functools
import json
from itertools import combinations

import requests
import sdu_bkjws
from flask import Flask, request, make_response, render_template, redirect
from flask_login import LoginManager

import make_ics
from config import ppoi_secret, workload

lm = LoginManager()

app = Flask(__name__)
app.config.from_object('config.Configuration')

lm.init_app(app)


@lm.user_loader
def load_user(auth):
    try:
        if not auth:
            auth = request.cookies.get('auth', '')
            auth = request.args.get('auth', auth)
        if auth:
            auth = auth.replace('@', '=')
            auth = base64.b64decode(auth).decode()
            auth = json.loads(auth)
        else:
            return 'This page does not exist', 404
    except binascii.Error:
        return
    except json.JSONDecodeError:
        return

    username = auth('username', False)
    password = auth('password', False)
    if username and password:
        return auth
    return


@app.context_processor
def context():
    return dict(workload=workload)


def parser_auth(fn):
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
            if s:
                return fn(s)
            else:
                return fn()
        except Exception as e:
            resp = make_response(
                json.dumps({'error': str(e)}))
            return resp, 401

    return wrapper


@app.route('/logout')
def logout():
    r = make_response(redirect('/'))
    r.set_cookie('auth', '')
    return r


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/menu', methods=['POST', ])
def menu():
    student_id = request.form.get('student_id', None)
    password = request.form.get('password', None)
    token = request.form.get('projectpoi-captcha-token', None)
    if student_id and password and token:
        try:
            r = requests.post('https://api.ppoi.org/token/verify',
                              data={'secret': ppoi_secret,
                                    'token': token,
                                    'hashes': workload})
            r = r.json()
            print(r)
            if r['success']:
                s = sdu_bkjws.SduBkjws(student_id, password)

                resp = make_response(render_template('menu.html'))

                auth = base64.b64encode(json.dumps({'username': student_id, 'password': password}).encode()).decode()

                resp.set_cookie('auth', auth, expires=datetime.datetime.today() + datetime.timedelta(hours=1))
                return resp
            else:
                return render_template('index.html', message='不要投机取巧哦')
        except Exception as e:
            return str(e)


@app.route('/exam-result')
@parser_auth
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


@app.route('/calendar')
# @parser_auth()
def calendar_menu():
    auth = request.cookies.get('auth', '')
    try:
        auth = auth.replace('@', '=')
        j = json.loads(base64.b64decode(auth).decode())
        if j.get('username', False) and j.get('password'):
            return render_template('calendar.html', auth=auth)
        else:
            raise json.JSONDecodeError
    except json.JSONDecodeError:
        r = make_response(render_template('index.html', message=auth))
        return r, 401


@app.route('/calendar/<auth>')
@parser_auth
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


@app.errorhandler(404)
def page_not_found(error):
    return 'This page does not exist', 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=800)
