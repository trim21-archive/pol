# pylint: disable=C0103
from app.deprecation import bind_deprecated_path
from app.md2bbc import Markdown2BBcode
from flask import Flask, flash, render_template

app = Flask(__name__)
app.config.from_object('app.config.Configuration')
bind_deprecated_path(app)

app.add_url_rule('/md2bbc', view_func=Markdown2BBcode.as_view('md2bbc'))


@app.route('/')
def index():
    return render_template('index.html')


@app.errorhandler(404)
def page_not_found(error):
    flash('Page Not Found')
    return render_template('index.html'), 404
