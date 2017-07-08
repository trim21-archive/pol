from flask import Flask, request, make_response
from sdu_bkjws import SduBkjws
import json
import base64
app = Flask(__name__)


@app.route('/exam-result')
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
    s = json.dumps(s.get_now_score(), ensure_ascii=False,
                   indent='  ', sort_keys=True)
    resp = make_response(s)
    resp.headers['Content-Type'] = "application/json;charset=UTF-8"
    return resp


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=800)
