import base64
import json
from functools import wraps
from flask import Flask, request, make_response
from sdu_bkjws import SduBkjws

from my_calendar import makeICS

app = Flask(__name__)


def parserAuth(fn):
    @wraps(fn)
    def wrapper():
        try:
            auth = request.args.get('auth')
            auth = base64.b64decode(auth).decode()
            auth = json.loads(auth)
        except Exception as e:
            return make_response('error'), 404
        # try:
        print(auth)
        username = auth['username']
        password = auth['password']
        s = SduBkjws(username, password)
        return fn(s)
        # except Exception as e:
        #     resp = make_response(
        #         json.dumps({'error': str(e)}))
        #     return resp, 401

    return wrapper


@app.route('/exam-result')
@parserAuth
def examResult(s: SduBkjws):
    return json.dumps(s.get_now_score(), ensure_ascii=False,
                      sort_keys=True)


@app.route('/ics')
@parserAuth
def manyUser(s: SduBkjws):
    x = makeICS(s)
    resp = make_response(x)
    resp.headers['Content-Type'] = "text/calendar;charset=UTF-8"
    return resp


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=800)
