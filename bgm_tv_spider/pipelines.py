from typing import Union
from collections import defaultdict

import twisted.python.failure
from twisted.enterprise import adbapi

from bgm_tv_spider import settings
from bgm_tv_spider.items import EpItem, TagItem, SubjectItem, RelationItem
from bgm_tv_spider.models import Ep, Tag, Subject, Relation


def do_insert(cursor: adbapi.Transaction, container):
    # 会从dbpool取出cursor
    # 执行具体的插入
    cursor._connection.ping(reconnect=True)
    for key, value in container.items():
        sql = get_insert_sql(key, value)
        cursor.execute(*sql)


def handle_error(failure: twisted.python.failure.Failure, container):
    # 处理异步插入的异常
    print(container)
    print(failure, type(failure))
    print(failure.value)


class MysqlPipeline:
    def open_spider(self, spider):
        self.dbpool = adbapi.ConnectionPool(
            'pymysql',
            db=settings.MYSQL_DB,
            host=settings.MYSQL_HOST,
            user=settings.MYSQL_USER,
            password=settings.MYSQL_PASSWORD,
            charset='utf8mb4',
            cp_reconnect=True,
        )
        self.container = defaultdict(list)

    def process_item(
        self,
        item: Union[SubjectItem, RelationItem, TagItem, EpItem],
        spider,
    ):
        item_type = get_item_type(item)
        self.container[item_type].append(dict(**item))
        if isinstance(item, SubjectItem):
            # insert all items to db
            self.dbpool.runInteraction(
                do_insert,
                self.container,
            ).addErrback(handle_error, self.container)
            self.container = defaultdict(list)

        return item


def get_item_type(item):
    return type(item).__name__


def get_insert_sql(type_name, items):
    if type_name == 'SubjectItem':
        return Subject.insert_many(items).on_conflict(
            preserve=(
                Subject.name_cn,
                Subject.name,
                Subject.image,
                Subject.tags,
                Subject.locked,
                Subject.info,
                Subject.score_details,
                Subject.score,
                Subject.wishes,
                Subject.done,
                Subject.doings,
                Subject.on_hold,
                Subject.dropped,
            ),
        ).sql()
    elif type_name == 'TagItem':
        return Tag.insert_many(items).on_conflict(preserve=(Tag.count, )).sql()
    elif type_name == 'RelationItem':
        return Relation.insert_many([
            dict(id=f'{item["source"]}-{item["target"]}', **item) for item in items
        ]).on_conflict(preserve=(Relation.relation, )).sql()
    elif type_name == 'EpItem':
        return Ep.insert_many(items).on_conflict(
            preserve=(Ep.subject_id, Ep.name, Ep.episode)
        ).sql()
    else:
        raise ValueError(f'can\'t get sql from {type_name}')
