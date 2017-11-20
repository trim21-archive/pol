# config
import datetime
import os

# db_path = os.path.join(os.environ.get('HOME', os.environ.get('USERPROFILE')), 'db', 'example.db')

sec = os.getenv('website_secret')
ppoi_secret = os.getenv('ppoi_key')


class Configuration(object):
    # DATABASE = {
    #     'name': db_path,
    #     'engine': 'peewee.SqliteDatabase',
    #     'check_same_thread': False,
    # }
    DEBUG = False
    SECRET_KEY = sec
    SESSION_COOKIE_SECURE = True
    # REMEMBER_COOKIE_SECURE = True
    REMEMBER_COOKIE_DURATION = datetime.timedelta(minutes=30)
    # TEMPLATES_AUTO_RELOAD = True


workload = 1024 * 2
