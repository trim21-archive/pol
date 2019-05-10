"""
configuration for project
"""
import datetime
import secrets


class Configuration:
    """
    flask config
    """
    DEBUG = False
    TEMPLATES_AUTO_RELOAD = True

    SECRET_KEY = secrets.token_hex(32)

    # flask-login
    REMEMBER_COOKIE_SECURE = True

    REMEMBER_COOKIE_DURATION = datetime.timedelta(minutes=30)
