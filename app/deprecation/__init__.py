from app.deprecation.make_ics import calendar
from flask import Flask


def bind_deprecated_path(app: Flask):
    app.route('/calendar/<auth>')(calendar)
