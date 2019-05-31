from collections import defaultdict
from typing import Union

from twisted.enterprise import adbapi

from bgm_tv_spider import settings
from bgm_tv_spider.items import EpItem, RelationItem, SubjectItem, TagItem
from bgm_tv_spider.models import Ep, Relation, Subject, Tag


class MysqlPipeline:
    item_container = defaultdict(list)

    def open_spider(self, spider):
        self.dbpool = adbapi.ConnectionPool(
            # "MySQLdb",
            'pymysql',
            db=settings.MYSQL_DBNAME,
            host=settings.MYSQL_HOST,
            user=settings.MYSQL_USER,
            password=settings.MYSQL_PASSWORD,
            charset='utf8mb4',
        )

    # @inlineCallbacks
    def process_item(
        self,
        item: Union[SubjectItem, RelationItem, TagItem, EpItem],
        spider,
    ):
        append_result = self.append(item)
        if append_result:
            query = self.dbpool.runInteraction(
                self.do_insert,
                item,
                self.item_container[item.__class__.__name__],
            )
            # 处理异常
            query.addErrback(self.handle_error, item, spider)
        return item

    @staticmethod
    def handle_error(failure, item, spider):
        # 处理异步插入的异常
        print(item)
        print(failure)

    def append(self, item):
        item_class_name = item.__class__.__name__

        if isinstance(item, SubjectItem):
            if not item['name']:
                item['name'] = item['name_cn']
            self.item_container[item_class_name].append(dict(**item))
            return len(self.item_container[item_class_name]) >= 20
        elif isinstance(item, RelationItem):
            self.item_container[item_class_name].append(
                dict(id=f'{item["source"]}-{item["target"]}', **item)
            )
            # return len(self.item_container[item_class_name]) >= 100
        elif isinstance(item, TagItem):
            self.item_container[item_class_name].append(dict(**item))
            # return len(self.item_container[item_class_name]) >= 100
        elif isinstance(item, EpItem):
            self.item_container[item_class_name].append(dict(**item))
            # return len(self.item_container[item_class_name]) >= 100
        else:
            return
        return len(self.item_container[item_class_name]) >= 50

    def do_insert(self, cursor, item, container):
        item_class_name = item.__class__.__name__

        insert_sql = do_bulk_upsert(
            item_class_name,
            container=self.item_container[item_class_name],
        )
        if insert_sql:
            cursor.execute(*insert_sql)
        self.item_container[item_class_name] = list()

    def close_spider(self, spider):
        for key, container in self.item_container.items():
            insert_sql = do_bulk_upsert(key, container)
            if insert_sql:
                self.dbpool.runQuery(*insert_sql)


def do_bulk_upsert(item_class_name, container: list):
    if not container:
        return
    if item_class_name == SubjectItem.__name__:
        return Subject.insert_many(container).on_conflict(
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
    if item_class_name == RelationItem.__name__:
        return Relation.insert_many(container).on_conflict(
            preserve=(Relation.relation, ),
        ).sql()
    if item_class_name == TagItem.__name__:
        return Tag.insert_many(container).on_conflict(preserve=(Tag.count,
                                                                ), ).sql()
    if item_class_name == EpItem.__name__:
        return Ep.insert_many(container).on_conflict(
            preserve=(Ep.subject_id, Ep.name, Ep.episode)
        ).sql()
