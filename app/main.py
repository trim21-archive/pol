import base64
import json
import binascii
import functools
from datetime import date
from flask import Flask, request, make_response
import sdu_bkjws

import make_ics

app = Flask(__name__)


def parserAuth(fn):
    @functools.wraps(fn)
    def wrapper():
        try:
            auth = request.args.get('auth', None)
            if auth:
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


@app.route('/exam-result')
@parserAuth
def examResult(s: sdu_bkjws.SduBkjws):
    return json.dumps(s.get_now_score(), ensure_ascii=False,
                      sort_keys=True)


@app.route('/curriculum')
@parserAuth
def manyUser(s: sdu_bkjws.SduBkjws):
    x = make_ics.from_lesson_to_ics(s.get_lesson())
    resp = make_response(x)
    resp.headers['Content-Type'] = "text/calendar;charset=UTF-8"
    return resp


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
