import base64
import json

from flask import Flask, request, make_response
from sdu_bkjws import SduBkjws

from my_calendar import makeICS

app = Flask(__name__)


@app.route('/exam-result')
def examResult():
    try:
        auth = request.args.get('auth')
        auth = base64.b64decode(auth).decode()
        auth = json.loads(auth)
        print(auth)
        username = auth['username']
        password = auth['password']
        s = SduBkjws(username, password)
    except:
        resp = make_response(json.dumps(
            {'error': 'username or password error'}))
        return resp, 401
    s = json.dumps(s.get_now_score(), ensure_ascii=False,
                   indent='  ', sort_keys=True)
    resp = make_response(s)
    resp.headers['Content-Type'] = "application/json;charset=UTF-8"
    return resp


@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        auth = request.args.get('auth')
        auth = base64.b64decode(auth).decode()
        auth = json.loads(auth)
        print(auth)
        username = auth['username']
        password = auth['password']
        s = SduBkjws(username, password)
    except:
        resp = make_response(json.dumps(
            {'error': 'username or password error'}))
        return resp, 401

    x = makeICS(username, password)
    resp = make_response(x)
    resp.headers['Content-Type'] = "text/calendar;charset=UTF-8"
    return resp


@app.route('/ics')
def manyUser():
    try:
        auth = request.args.get('auth')
        auth = base64.b64decode(auth).decode()
        auth = json.loads(auth)
        print(auth)
        username = auth['username']
        password = auth['password']
        s = SduBkjws(username, password)
    except:
        resp = make_response(json.dumps(
            {'error': 'username or password error'}))
        return resp, 401

    x = makeICS(username, password)
    resp = make_response(x)
    resp.headers['Content-Type'] = "text/calendar;charset=UTF-8"
    return resp


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=800)
