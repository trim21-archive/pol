import base64
import json
import datetime

import pytz
from peewee import *

# from app import db

tz = pytz.timezone('Asia/Shanghai')


#
# class User(db.Model):
#     id = PrimaryKeyField()
#     username = TextField()
#     password = TextField()
#     placeHolder = TextField(null=True)
#     mined = TextField()
#     created_date = DateTimeField(default=lambda: datetime.datetime.now(tz))
#     ppoi_token = TextField()
#
#     last_login = DateTimeField(default=lambda: datetime.datetime.now(tz))
#
#     # User information
#     is_enabled = BooleanField(null=False, default=False)
#
#     def is_active(self):
#         return self.is_enabled
#
#         # def create_tables():
#         #     all_tables = [User, ]
#         #     for table in all_tables:  # type: db.Model
#         #         if not table.table_exists():
#         #             table.create_table()
#
#         # Point.create_table()
#         # Tag.create_table()
#         # PointTag.create_table()
#         # LogPoint.create_table()
#         # User.create_table()
#         # UserPoint.create_table()


class User(object):
    is_authenticated = True
    is_active = True
    is_anonymous = False
    auth = ''

    def get_id(self):
        return self.auth

    def __init__(self, auth):
        auth_string = auth

        if auth:
            auth = auth.replace('@', '=')
            auth = base64.b64decode(auth).decode()
            auth = json.loads(auth)
            auth['auth'] = auth_string
            self.username = auth['username']
            self.password = auth['password']
            self.auth = auth_string
            # self.s = s
        else:
            raise ValueError('you must input a auth')

    @classmethod
    def get(cls, auth):
        try:
            user = cls(auth)
            return user
        except:
            return
