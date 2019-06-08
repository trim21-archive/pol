import pymysql

from app.core import config
from app.db import database
from app.db_models import Relation, Subject

if __name__ == '__main__':
    connect = pymysql.Connect(
        host=config.MYSQL_HOST,
        user=config.MYSQL_USER,
        password=config.MYSQL_PASSWORD,
        charset='utf8mb4'
    )

    with connect.cursor() as cur:
        cur.execute(
            'CREATE DATABASE IF NOT EXISTS bgm_ip_viewer '
            'DEFAULT CHARSET utf8mb4 '
            'COLLATE utf8mb4_general_ci;'
        )

        with database.db.allow_sync():
            Relation.create_table()
            Subject.create_table()
        with open('./tests_data/dump.sql', 'r', encoding='utf-8') as f:
            sql = f.read()
        cur.execute(sql)
