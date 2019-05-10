import flask
from flask import make_response, render_template, request
import md2bbc

import make_ics
from app import app


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/calendar/<auth>')
def calendar(auth):
    r = make_ics.calendar()
    r = make_response(r)
    if request.user_agent.string.find('Mozilla') != -1:
        r.headers['Content-Type'] = "text/plain;charset=UTF-8"
    else:
        r.headers['Content-Type'] = "text/calendar;charset=UTF-8"
    return r, 200


@app.errorhandler(404)
def page_not_found(error):
    flask.flash('Page Not Found')
    return render_template('index.html'), 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=800)
