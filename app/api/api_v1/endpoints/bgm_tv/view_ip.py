from fastapi import Depends, APIRouter, HTTPException
from databases import Database
from starlette.responses import JSONResponse

from app import curd
from app.core import config
from app.db.redis import PickleRedis
from app.db.depends import get_db, get_redis
from app.models.map import Map
from app.models.subject import Subject
from app.curd.exceptions import NotFoundError

router = APIRouter()


@router.get(
    '/meta/subject/{subject_id}',
    response_model=Subject,
    include_in_schema=config.DEBUG,
)
async def bgm_calendar(subject_id: int, db: Database = Depends(get_db)):
    try:
        s = await curd.subject.get_by_id(db, subject_id)
    except NotFoundError:
        raise HTTPException(404)
    return s.__dict__


@router.get('/subject/{subject_id}', response_model=Map)
async def bgm_ip_map(
    subject_id: int,
    db: Database = Depends(get_db),
    redis: PickleRedis = Depends(get_redis),
):
    r = await redis.get(f'pol:view-ip:map:subject:1:{subject_id}')
    if r:
        return r

    try:
        nodes, edges = await curd.map.get_by_subject_id(db, subject_id)
    except NotFoundError:
        return JSONResponse({'detail': 'subject not found'}, 404)

    rd = format_data(nodes, edges)
    await redis.set(f'map-subject-{subject_id}', rd, expire=60 * 60 * 2)
    return rd


def format_data(nodes, edges):
    r_nodes = {}
    r_edges = []
    for index, item in enumerate(nodes):
        item['subject_id'] = item['id']
        item['image'] = (
            'https://' + item.get('image', 'lain.bgm.tv/img/no_icon_subject.png')
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
