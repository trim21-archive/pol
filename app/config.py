import datetime
import os
import secrets


class Configuration(object):
    # DATABASE = {
    #     'name': db_path,
    #     'engine': 'peewee.SqliteDatabase',
    #     'check_same_thread': False,
    # }
    DEBUG = False
    TEMPLATES_AUTO_RELOAD = True

    SECRET_KEY = secrets.token_hex(32)

    # flask-login
    REMEMBER_COOKIE_SECURE = True

    REMEMBER_COOKIE_DURATION = datetime.timedelta(minutes=30)


if os.environ.get('DEV', False):
    workload = 256
hostname = 'https://www.trim21.cn'
if os.environ.get('DEV', False):
    hostname = 'http://localhost:800'
