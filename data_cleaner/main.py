import copy
import types
from collections import defaultdict
from typing import Dict

import peewee as pw
import tqdm

from bgm_tv_spider.models import Relation, Subject, db

SUBJECT_ID_START = 1
SUBJECT_ID_END = Subject.select(pw.fn.MAX(Subject.id)).scalar()
# SUBJECT_ID_END = 6000
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


def remove_relation(source, target, rebuild=True):
    source = int(source)
    target = int(target)
    Relation.update(removed=True).where((Relation.id == f'{source}-{target}')
                                        | (Relation.id == f'{target}-{source}'))


def rebuild_map(map_id=None, item_id=None):
    if item_id:
        map_id = Subject.get_by_id(item_id).map

    if map_id:
        Subject.update(map=None).where(Subject.map == map_id).execute()
        Relation.update(map=None).where(Relation.map == map_id).execute()


def remove_nodes(node_id, rebuild=True):
    Subject.delete_by_id(node_id)
    Relation.delete().where((Relation.source == node_id)
                            | (Relation.target == node_id)).execute()


def nodes_need_to_remove(*node_ids):
    for node in node_ids:
        assert isinstance(node, int)
    Subject.update(locked=True).where(Subject.id.in_(node_ids)).execute()
    Relation.update(
        removed=True
    ).where(Relation.source.in_(node_ids)
            | Relation.target.in_(node_ids)).execute()


def relations_need_to_remove(kwargs):
    for id_1, id_2 in kwargs:
        Relation.update(
            removed=True
        ).where(((Relation.source == id_1) & (Relation.target == id_2))
                | ((Relation.source == id_2)
                   & (Relation.target == id_1))).execute()


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
            x.id
            for x in Subject.select(Subject.id).where(Subject.map.is_null())
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
            j = yield_job.pop()
            do(j)
        elif start_job:
            j = start_job.pop()
            do(j)
        else:
            break
        i += 1


def pre_remove():
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
    Relation.update(removed=1).where(
        Relation.source.in_(id_to_remove)
        | Relation.target.in_(id_to_remove)
    ).execute()

    for chunk in chunk_iter_list(list(range(SUBJECT_ID_START, SUBJECT_ID_END))):
        db_data = list(
            Subject.select(Subject.id, Subject.subject_type,
                           Subject.locked).where(
                               Subject.id.in_(chunk)
                               & (Subject.subject_type != 'Music')
                               & (Subject.locked == 0)
                           )
        )
        for s in db_data:
            assert s.subject_type != 'Music'
            assert s.locked == 0
        non_exists_ids = list(set(chunk) - {x.id for x in db_data})
        Relation.update(removed=1).where(
            Relation.source.in_(non_exists_ids)
            | Relation.target.in_(non_exists_ids)
        ).execute()

    for i in tqdm.tqdm(range(SUBJECT_ID_START, SUBJECT_ID_END, CHUNK_SIZE)):
        relation_id_need_to_remove = set()
        source_to_target = defaultdict(dict)
        sources = Relation.select().where((
            ((Relation.source >= i) & (Relation.source < i + CHUNK_SIZE))
            | ((Relation.target >= i) & (Relation.target < i + CHUNK_SIZE))
        )
                                          & (Relation.removed == 0))

        sources = list(sources)

        for edge in sources:
            source_to_target[edge.source][edge.target] = True

        for edge in sources:
            if not source_to_target[edge.target].get(edge.source):
                relation_id_need_to_remove.add(edge.id)

        for i, chunk in enumerate(
            chunk_iter_list(list(relation_id_need_to_remove))
        ):
            Relation.update(removed=1).where(Relation.id.in_(chunk)).execute()
    print('finish pre remove')


def first_run():
    subjects = {}  # type: Dict[int, Subject]
    for i in tqdm.tqdm(range(SUBJECT_ID_START, SUBJECT_ID_END, CHUNK_SIZE)):
        for s in Subject.select().where((Subject.id >= i)
                                        & (Subject.id < i + CHUNK_SIZE)
                                        & (Subject.locked == 0)
                                        & (Subject.subject_type != 'Music')):
            assert s.subject_type != 'Music'
            assert s.locked == 0
            s.map = 0
            subjects[s.id] = s
    print('total', len(subjects), 'subjects')
    relation_from_id = defaultdict(set)
    edge_count = 0
    for i in range(SUBJECT_ID_START, SUBJECT_ID_END, CHUNK_SIZE):
        for edge in Relation.select().where((Relation.source >= i)
                                            &
                                            (Relation.source < i + CHUNK_SIZE)
                                            & (Relation.removed == 0)):
            assert i <= edge.source < i + CHUNK_SIZE
            assert subjects[edge.target]
            assert subjects[edge.source]
            edge_count += 1
            edge.map = 0
            relation_from_id[edge.source].add(edge)
            relation_from_id[edge.target].add(edge)
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
            for s in subjects.values():
                maps[s.map].append(s.id)

            for map_id, ids in tqdm.tqdm(maps.items(), total=len(maps.keys())):
                Subject.update(map=map_id).where(Subject.id.in_(ids)).execute()
            maps = defaultdict(set)

            for source, edges in relation_from_id.items():
                s = subjects[source]
                [maps[s.map].add(x.id) for x in edges]
            for map_id, ids in tqdm.tqdm(maps.items(), total=len(maps.keys())):
                for chunk in chunk_iter_list(list(ids)):
                    Relation.update(map=map_id).where(
                        Relation.id.in_(chunk)
                    ).execute()
        except Exception as e:
            txn.rollback()
            raise e

    print('finish save to db')


if __name__ == '__main__':
    try:
        print('finish module init, start job')
        print('remove all map')
        Relation.update(removed=0, map=0).execute()
        Subject.update(map=0).execute()
        print('finish remove all map')
        with db.atomic() as txn:
            try:
                pre_remove()
            except Exception as e:
                txn.rollback()
                raise e
        first_run()
    except KeyboardInterrupt:
        exit(1)
