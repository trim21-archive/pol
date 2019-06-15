from typing import Union

from twisted.enterprise import adbapi

from bgm_tv_spider import settings
from bgm_tv_spider.items import EpItem, TagItem, SubjectItem, RelationItem
from bgm_tv_spider.models import Ep, Tag, Subject, Relation


class MysqlPipeline:
    def open_spider(self, spider):
        self.dbpool = adbapi.ConnectionPool(
            'pymysql',
            db=settings.MYSQL_DB,
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
        query = self.dbpool.runInteraction(self.do_insert, item)
        # 处理异常
        query.addErrback(self.handle_error, item, spider)
        return item

    def handle_error(self, failure, item, spider):
        # 处理异步插入的异常
        print(failure, type(failure))

    def do_insert(self, cursor, item):
        # 会从dbpool取出cursor
        # 执行具体的插入
        if isinstance(item, SubjectItem):
            if not item['name']:
                item['name'] = item['name_cn']
            # if not item['name_cn']:
            #     item['name_cn'] = item['name']
            insert_sql = Subject.insert(**item).on_conflict(
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
        elif isinstance(item, RelationItem):
            insert_sql = Relation.insert(
                id=f'{item["source"]}-{item["target"]}', **item
            ).on_conflict(preserve=(Relation.relation, ), ).sql()
        elif isinstance(item, TagItem):
            insert_sql = Tag.insert(
                **item
            ).on_conflict(preserve=(Tag.count, ), ).sql()
        elif isinstance(item, EpItem):
            insert_sql = Ep.insert(**item).on_conflict(
                preserve=(Ep.subject_id, Ep.name, Ep.episode)
            ).sql()
        else:
            return
        cursor.execute(*insert_sql)
