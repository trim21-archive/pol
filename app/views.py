# pylint: disable=C0103
import os

from flask import Flask, flash, render_template

import sentry_sdk
from app.api import app as api
from app.deprecation import bind_deprecated_path
from app.md2bbc import Markdown2BBcode
from sentry_sdk.integrations.flask import FlaskIntegration

SENTRY_DSN = os.getenv('DSN')
if SENTRY_DSN:
    sentry_sdk.init(dsn=os.getenv('DSN'), integrations=[FlaskIntegration()])

app = Flask(__name__)
app.config.from_object('app.config.Configuration')
app.register_blueprint(api, url_prefix='/api.v1')
bind_deprecated_path(app)
app.add_url_rule('/md2bbc', view_func=Markdown2BBcode.as_view('md2bbc'))


@app.route('/')
def index():
    return render_template('index.html')


@app.errorhandler(404)
def page_not_found(error):
    flash('Page Not Found')
    return render_template('index.html'), 404
