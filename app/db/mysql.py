import peewee as pw
from databases import Database, DatabaseURL
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

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

if config.TESTING:
    database = Database(config.MYSQL_URI, force_rollback=True)
else:
    database = Database(config.MYSQL_URI)

engine = create_engine(
    str(DatabaseURL(config.MYSQL_URI).replace(dialect='mysql+pymysql'))
)
Session = sessionmaker(bind=engine)
