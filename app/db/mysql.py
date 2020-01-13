import peewee as pw
from databases import Database

from app.core import config

if ':' in config.MYSQL_HOST:
    host, port = config.MYSQL_HOST.split(':')
else:
    host, port = config.MYSQL_HOST, 3306

db = pw.MySQLDatabase(
    config.MYSQL_DB,
    host=host,
    port=int(port),
    user=config.MYSQL_USER,
    password=config.MYSQL_PASSWORD,
    charset='utf8mb4',
)

database = Database(config.MYSQL_URI)
