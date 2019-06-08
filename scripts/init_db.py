import pymysql

from app.core import config

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

        with open('./tests_data/dump.sql', 'r', encoding='utf-8') as f:
            sql = f.read()
        cur.execute(sql)
