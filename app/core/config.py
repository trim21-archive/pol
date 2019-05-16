import os
import secrets


def getenv_boolean(var_name, default_value=False):
    result = default_value
    env_value = os.getenv(var_name)
    if env_value is not None:
        result = env_value.upper() in ('TRUE', '1')
    return result


API_V1_STR = '/api/v1'
SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY:
    SECRET_KEY = secrets.token_hex(32)

ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 8  # 60 minutes * 24 hours * 8 days = 8 days

SERVER_NAME = os.getenv('SERVER_NAME')
SERVER_HOST = os.getenv('SERVER_HOST')
BACKEND_CORS_ORIGINS = os.getenv(
    'BACKEND_CORS_ORIGINS'
)  # a string of origins separated by commas, e.g: "http://localhost, http://localhost:4200, http://localhost:3000, http://localhost:8080, http://local.dockertoolbox.tiangolo.com"
PROJECT_NAME = os.getenv('PROJECT_NAME')
SENTRY_DSN = os.getenv('SENTRY_DSN')

MYSQL_HOST = os.getenv('MYSQL_HOST')
MYSQL_USER = os.getenv('MYSQL_USER')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD')
MYSQL_DB = os.getenv('MYSQL_DB')
SQLALCHEMY_DATABASE_URI = (
    f'mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DB}'
)
