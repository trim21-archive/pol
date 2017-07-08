from flask import Flask, request, make_response
from sdu_bkjws import SduBkjws
import json
app = Flask(__name__)


@app.route('/exam-result')
def manyUser():
    try:
        username = request.args.get('username')
        password = request.args.get('password')
    except:
        return json.dumps({'error': 'username or password required'}), 401
    try:
        s = SduBkjws(username, password)
    except:
        return json.dumps({'error': 'username or password error'}), 401
    s = json.dumps(s.get_now_score(), ensure_ascii=False,
                   indent='  ', sort_keys=True)
    resp = make_response(s)
    resp.headers['Content-Type'] = "application/json;charset=UTF-8"
    return resp


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=800)
