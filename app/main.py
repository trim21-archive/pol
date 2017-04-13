from flask import Flask, request, redirect, make_response
from utils.calendar import makeiCs

app = Flask(__name__)


@app.route('/')
def index():
    return redirect('https://github.com/Trim21/sdu2ics')


@app.route('/ics')
def manyUser():
    try:
        username = request.args.get('username')
        password = request.args.get('password')
        x = makeiCs(username, password)
        resp = make_response(x)
        resp.headers['Content-Type:'] = "text/calendar;charset=UTF-8"
        if x:
            return resp
        else:
            return '密码错误'
    except:
        return 'url错误'


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False, port=800)
