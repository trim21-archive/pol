import peewee_async

from app.core import config

db = peewee_async.PooledMySQLDatabase(
    config.MYSQL_DB,
    host=config.MYSQL_HOST,
    user=config.MYSQL_USER,
    password=config.MYSQL_PASSWORD,
    charset='utf8mb4',
)
db.set_allow_sync(False)

objects = peewee_async.Manager(db)
