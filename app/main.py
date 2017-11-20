import base64
import functools
import json
from itertools import combinations

import flask_login
import requests
import sdu_bkjws
import flask
from flask import request, make_response, render_template, redirect, url_for
from flask_login import LoginManager

import make_ics
import models
from app import app
from config import ppoi_secret, workload, hostname


login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(auth):
    return models.User.get(auth)


@login_manager.unauthorized_handler
def unauthorized():
    flask.flash('需要先登录')
    return redirect('{}/'.format(hostname))


@app.context_processor
def context():
    return dict(workload=workload)


def parser_auth(fn):
    @functools.wraps(fn)
    def wrapper():
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
    r = make_response(redirect('{}/'.format(hostname)))
    return r


@app.route('/')
def index():
    if flask_login.current_user.is_active:
        return render_template('menu.html')
    return render_template('index.html')


@app.route('/login', methods=['POST'])
def login():
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
        except requests.ConnectionError:
            flask.flash('验证码暂时无法验证,请联系我')
            return redirect('{}/'.format(hostname))
        try:
            if r['success']:
                s = sdu_bkjws.SduBkjws(student_id, password)
                auth = base64.b64encode(json.dumps({'username': student_id, 'password': password}).encode()).decode()

                u = models.User(auth)

                flask_login.login_user(u)
                flask.flash('login success')
                return redirect('{}/menu'.format(hostname))
            else:
                flask.flash('不要投机取巧哦')
                return redirect('{}/'.format(hostname))
        except requests.ConnectionError:
            flask.flash('可能是校外暂时无法访问教务系统,用手机流量试试,如果可以访问请联系我')
        except sdu_bkjws.AuthFailure as v:
            flask.flash(str(v))
        except Exception as e:
            flask.flash(str(e))
        finally:
            return redirect("{}/".format(hostname))
    else:
        flask.flash('请点击验证码通过验证')
        return redirect('{}/'.format(hostname))


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
    resp = make_response(render_template('scores.html', lessons=result))

    return resp


@app.route('/calendar')
@flask_login.login_required
def calendar_menu():
    auth = flask_login.current_user.auth
    auth = auth.replace('@', '=')
    return render_template('calendar.html', auth=auth)


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
    flask.flash('Page Not Found')
    return render_template('index.html'), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=800)
