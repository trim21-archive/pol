import base64
import binascii
import datetime
import functools
import json
from itertools import combinations

import flask
import flask_login
import requests
import sdu_bkjws
from flask import Flask, request, make_response, render_template, redirect
from flask_login import LoginManager

import make_ics
from config import ppoi_secret, workload
import models

app = Flask(__name__)
app.config.from_object('config.Configuration')

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(auth):
    return models.User.get(auth)


@login_manager.unauthorized_handler
def unauthorized():
    # do stuff
    return render_template('unlogin.html')


@app.context_processor
def context():
    return dict(workload=workload)


def parser_auth(fn):
    @functools.wraps(fn)
    def wrapper(auth=None):
        username = flask_login.current_user.username
        password = flask_login.current_user.password

        s = sdu_bkjws.SduBkjws(username, password)
        if s:
            return fn(s)
        else:
            return 'password or username error', 401

    return wrapper


@app.route('/logout')
@flask_login.login_required
def logout():
    flask_login.logout_user()
    r = make_response(redirect('https://www.trim21.cn/'))
    # r.set_cookie('auth', '')
    return r


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        return redirect('https://www.trim21.cn/')
    student_id = request.form.get('student_id', None)
    password = request.form.get('password', None)
    token = request.form.get('projectpoi-captcha-token', None)
    # token = True
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
                auth = base64.b64encode(json.dumps({'username': student_id, 'password': password}).encode()).decode()

                u = models.User(auth)

                u = flask_login.login_user(u, True)

                resp = make_response(redirect('https://www.trim21.cn/menu'))
                return resp
            else:
                # return redirect('/')
                return render_template('index.html', message='不要投机取巧哦')
        except Exception as e:
            return str(e)


@app.route('/menu', methods=['GET', ])
@flask_login.login_required
def menu():
    return render_template('menu.html')


@app.route('/exam-result')
@flask_login.login_required
@parser_auth
def exam_result(s: sdu_bkjws.SduBkjws):
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
@flask_login.login_required
def calendar_menu():
    auth = flask_login.current_user.auth
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
def calendar(auth):
    try:
        user = models.User(auth)
        s = sdu_bkjws.SduBkjws(user.username, user.password)
        r = make_ics.calendar(s)
        r = make_response(r)

        if request.user_agent.string.find('Mozilla') != -1:
            r.headers['Content-Type'] = "text/plain;charset=UTF-8"
        else:
            r.headers['Content-Type'] = "text/calendar;charset=UTF-8"
        return r, 200
    except Exception as e:
        resp = make_response(
            json.dumps({'error': str(e)}))
        return resp, 401


@app.errorhandler(404)
def page_not_found(error):
    return 'This page does not exist', 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=800)
