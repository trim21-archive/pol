import peewee_async

from app.core import config


class AsyncMySQLConnection(peewee_async.AsyncMySQLConnection):
    """Asynchronous database connection pool.
    """
    def __init__(self, *, database=None, loop=None, timeout=None, **kwargs):
        self.pool = None
        self.loop = loop
        self.database = database
        self.timeout = timeout
        kwargs.setdefault('pool_recycle', 360)
        self.connect_params = kwargs


if ':' in config.MYSQL_HOST:
    host, port = config.MYSQL_HOST.split(':')
else:
    host, port = config.MYSQL_HOST, 3306
db = peewee_async.PooledMySQLDatabase(
    config.MYSQL_DB,
    host=host,
    port=int(port),
    user=config.MYSQL_USER,
    password=config.MYSQL_PASSWORD,
    charset='utf8mb4',
    async_conn=AsyncMySQLConnection,
)

db.set_allow_sync(False)

objects = peewee_async.Manager(db)
