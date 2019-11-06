import copy
import types
import logging
from typing import Dict
from collections import defaultdict

import tqdm
import peewee as pw

from bgm_tv_spider.models import Subject, Relation, db

CHUNK_SIZE = 5000


class MAP:
    count = 1

    def __init__(self):
        self.id = MAP.count

    @classmethod
    def create(cls):
        cls.count += 1
        return cls()


def chunk_iter_list(raw_list, chunk_size=CHUNK_SIZE):
    ds = copy.copy(raw_list)
    while ds:
        yield ds[:chunk_size]
        ds = ds[chunk_size:]


blank_list = ['角色出演', '片头曲', '片尾曲', '其他', '画集', '原声集']


def remove_relation(source, target):
    source = int(source)
    target = int(target)
    Relation.update(removed=True).where((Relation.id == f'{source}-{target}') |
                                        (Relation.id == f'{target}-{source}'))


def rebuild_map(map_id=None, item_id=None):
    if item_id:
        map_id = Subject.get_by_id(item_id).map

    if map_id:
        Subject.update(map=None).where(Subject.map == map_id).execute()
        Relation.update(map=None).where(Relation.map == map_id).execute()


def remove_nodes(node_id):
    Subject.delete_by_id(node_id)
    Relation.delete().where((Relation.source == node_id) |
                            (Relation.target == node_id)).execute()


def nodes_need_to_remove(*node_ids):
    for node in node_ids:
        assert isinstance(node, int)
    Subject.update(locked=True).where(Subject.id.in_(node_ids)).execute()
    Relation.update(
        removed=True
    ).where(Relation.source.in_(node_ids) | Relation.target.in_(node_ids)).execute()


def relations_need_to_remove(kwargs):
    for id_1, id_2 in kwargs:
        Relation.update(removed=True).where(((Relation.source == id_1) &
                                             (Relation.target == id_2)) |
                                            ((Relation.source == id_2) &
                                             (Relation.target == id_1))).execute()


done_id = set()


def pre_remove_relation():
    edge_need_remove = set()
    for edge in Relation.select().where(Relation.relation.in_(blank_list)):
        edge_need_remove.add(edge.id)
    edge_need_remove = list(edge_need_remove)
    for chunk in chunk_iter_list(edge_need_remove, 500):
        Relation.update(removed=True).where(Relation.id.in_(chunk)).execute()


def worker(start_job=None, work_fun=None):
    if not isinstance(work_fun, types.FunctionType):
        raise ValueError('work_fun must be a function')
    yield_job = []
    if start_job is None:
        start_job = [
            x.id for x in Subject.select(Subject.id).where(Subject.map.is_null())
        ]

    def do(j):
        # time.sleep(0.1)
        if j in done_id:
            return
        for node in work_fun(j):
            yield_job.append(node)
        done_id.add(j)

    i = 0
    while True:
        if i % 1000 == 0:
            print(len(yield_job) + len(start_job), end='|')
        if yield_job:
            jj = yield_job.pop()
            do(jj)
        elif start_job:
            jj = start_job.pop()
            do(jj)
        else:
            break
        i += 1


def pre_remove(subject_start, subject_end):
    print('pre remove')
    pre_remove_relation()
    nodes_need_to_remove(91493, 102098, 228714, 231982, 932, 84944, 78546)
    relations_need_to_remove([
        (91493, 8),
        (8108, 35866),
        (446, 123207),
        (123207, 27466),
        (123217, 4294),  # 高达 三国
    ])

    id_to_remove = []
    Subject.update(locked=1).where(Subject.subject_type == 'Music').execute()
    for s in Subject.select(Subject.id).where(Subject.locked == 1):
        id_to_remove.append(s.id)
    Relation.update(
        removed=1
    ).where(Relation.source.in_(id_to_remove) |
            Relation.target.in_(id_to_remove)).execute()

    for chunk in chunk_iter_list(list(range(subject_start, subject_end))):
        db_data = list(
            Subject.select(
                Subject.id,
                Subject.subject_type,
                Subject.locked,
            ).where(
                Subject.id.in_(chunk) & (Subject.subject_type != 'Music') &
                (Subject.locked == 0)
            )
        )
        for s in db_data:
            assert s.subject_type != 'Music'
            assert s.locked == 0
        non_exists_ids = list(set(chunk) - {x.id for x in db_data})
        Relation.update(removed=1).where(
            Relation.source.in_(non_exists_ids) | Relation.target.in_(non_exists_ids)
        ).execute()

    for i in tqdm.tqdm(range(subject_start, subject_end, CHUNK_SIZE)):
        relation_id_need_to_remove = set()
        source_to_target: Dict[int, Dict] = defaultdict(dict)
        sources = Relation.select().where((((Relation.source >= i) &
                                            (Relation.source < i + CHUNK_SIZE)) |
                                           ((Relation.target >= i) &
                                            (Relation.target < i + CHUNK_SIZE))) &
                                          (Relation.removed == 0))

        sources = list(sources)

        for edge in sources:
            source_to_target[edge.source][edge.target] = True

        for edge in sources:
            if not source_to_target[edge.target].get(edge.source):
                relation_id_need_to_remove.add(edge.id)

        for chunk in chunk_iter_list(list(relation_id_need_to_remove)):
            Relation.update(removed=1).where(Relation.id.in_(chunk)).execute()
    print('finish pre remove')


def first_run(subject_start, subject_end):
    subjects = {}  # type: Dict[int, Subject]
    for i in tqdm.tqdm(range(subject_start, subject_end, CHUNK_SIZE)):
        for sub in Subject.select().where((Subject.id >= i) &
                                          (Subject.id < i + CHUNK_SIZE) &
                                          (Subject.locked == 0) &
                                          (Subject.subject_type != 'Music')):
            assert sub.subject_type != 'Music'
            assert sub.locked == 0
            sub.map = 0
            subjects[sub.id] = sub
    print('total', len(subjects), 'subjects')
    relation_from_id = defaultdict(set)
    edge_count = 0
    for i in range(subject_start, subject_end, CHUNK_SIZE):
        for edge_ in Relation.select().where((Relation.source >= i) &
                                             (Relation.source < i + CHUNK_SIZE) &
                                             (Relation.removed == 0)):
            assert i <= edge_.source < i + CHUNK_SIZE
            assert subjects[edge_.target]
            assert subjects[edge_.source]
            edge_count += 1
            edge_.map = 0
            relation_from_id[edge_.source].add(edge_)
            relation_from_id[edge_.target].add(edge_)
    print('total', edge_count, 'edges')

    def deal_with_node(source_id):
        s = subjects.get(source_id)
        if not s:
            return
        edges = relation_from_id[source_id]
        map_id = None
        for edge in edges:
            if edge.map:
                map_id = edge.map
                break
        if not map_id:
            m = MAP.create()
            map_id = m.id
        for edge in edges:
            edge.map = map_id
        s.map = map_id
        done_id.add(source_id)
        for edge in edges:
            yield edge.target

    worker(list(subjects.keys()), deal_with_node)
    print('finish work, start save to db')

    with db.atomic() as txn:
        # if 1:
        try:
            # if 1:
            maps = defaultdict(list)
            for sub in subjects.values():
                maps[sub.map].append(sub.id)

            for map_id, ids in tqdm.tqdm(maps.items(), total=len(maps.keys())):
                Subject.update(map=map_id).where(Subject.id.in_(ids)).execute()
            maps = defaultdict(set)

            for source, edges in relation_from_id.items():
                sub = subjects[source]
                for x in edges:
                    maps[sub.map].add(x.id)
            for map_id, ids in tqdm.tqdm(maps.items(), total=len(maps.keys())):
                for chunk in chunk_iter_list(list(ids)):
                    Relation.update(map=map_id).where(Relation.id.in_(chunk)).execute()
        except Exception as e:
            txn.rollback()
            raise e

    print('finish save to db')


def re_calculate_map():
    print(re_calculate_map.__qualname__, flush=True)
    logger = logging.getLogger(__file__)
    subject_id_min = 1
    subject_id_max = Subject.select(pw.fn.MAX(Subject.id)).scalar()
    logger.info('finish module init, start job')
    logger.info('remove all map')
    Relation.update(removed=0, map=0).execute()
    Subject.update(map=0).execute()
    logger.info('finish remove all map')
    with db.atomic() as txn:
        try:
            pre_remove(subject_id_min, subject_id_max)
        except Exception as e:
            txn.rollback()
            logger.exception(e)
            raise e
    first_run(subject_id_min, subject_id_max)


if __name__ == '__main__':
    re_calculate_map()
