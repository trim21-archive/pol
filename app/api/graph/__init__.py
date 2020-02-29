"""GraphQL support

see <https://graphql.org/learn/serving-over-http/>_

"""

import graphql as gq
from fastapi import Body, Depends, APIRouter
from databases import Database
from starlette import requests

from app.db.depends import get_db
from app.api.graph.schema import schema

router = APIRouter()


@router.get('/graphql')
async def graphql_get(query: str, db: Database = Depends(get_db)):
    result: gq.ExecutionResult = await gq.graphql(
        schema, query, context_value={'db': db}
    )
    return await handle_result(result)


@router.post('/graphql/raw')
async def graphql_raw_post(req: requests.Request, db: Database = Depends(get_db)):
    body = (await req.body()).decode()
    result: gq.ExecutionResult = await gq.graphql(
        schema, body, context_value={'db': db}
    )
    return await handle_result(result)


@router.post('/graphql')
async def graphql_json(
    query: str = Body(..., ),
    operation_name: str = Body(None, alias='operationName'),
    variable_values: dict = Body(None, alias='variables'),
    db: Database = Depends(get_db)
):
    result = await gq.graphql(
        schema,
        query,
        operation_name=operation_name,
        variable_values=variable_values,
        context_value={'db': db}
    )
    return await handle_result(result)


async def handle_result(result: gq.ExecutionResult):
    if result.errors:
        return {'data': result.data, 'errors': [x.message for x in result.errors]}

    return {'data': result.data}
