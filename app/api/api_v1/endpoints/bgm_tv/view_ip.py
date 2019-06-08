from fastapi import APIRouter, Depends
from peewee import DoesNotExist
from peewee_async import Manager
from starlette.responses import JSONResponse

from app import curd
from app.db.depends import get_db
from app.models.map import Map
from app.models.subject import Subject

router = APIRouter()


@router.get(
    '/meta/subject/{subject_id}',
    response_model=Subject,
    include_in_schema=False,
)
async def bgm_calendar(subject_id: int, db: Manager = Depends(get_db)):
    s = await curd.subject.get_by_id(db, subject_id)
    return s.dict()


@router.get('/subject/{subject_id}', response_model=Map)
async def bgm_ip_map(
    subject_id: int,
    db: Manager = Depends(get_db),
    # redis: Redis = Depends(get_redis),
):
    try:
        # r = await redis.get(f'map-subject-{subject_id}')
        # if r:
        #     return r
        nodes, edges = await curd.map.get_by_subject_id(db, subject_id)
        print(nodes, edges)
        rd = format_data(
            [x.dict() for x in nodes],
            [x.dict() for x in edges],
        )
        # await redis.set(f'map-subject-{subject_id}', rd, expire=60 * 60 * 2)
        return rd

    except DoesNotExist:
        return JSONResponse({'detail': 'subject not found'}, 404)


def format_data(nodes, edges):
    r_nodes = {}
    r_edges = []
    for index, item in enumerate(nodes):
        item['subject_id'] = item['id']
        item['image'] = 'https://' + item.get(
            'image', 'lain.bgm_tv_spider.tv/img/no_icon_subject.png'
        )
        r_nodes[item['id']] = index
    for edge in edges:
        if edge['source'] in r_nodes and edge['target'] in r_nodes:
            edge['source'] = r_nodes[edge['source']]
            edge['target'] = r_nodes[edge['target']]
            r_edges.append(edge)
    for index, item in enumerate(nodes):
        item['id'] = index
    return {'nodes': nodes, 'edges': r_edges}
