from flask import Flask

from app.deprecation.make_ics import calendar


def bind_deprecated_path(app: Flask):
    app.route('/calendar/<auth>')(calendar)
