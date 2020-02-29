from graphql import (
    GraphQLInt, GraphQLField, GraphQLString, GraphQLNonNull, GraphQLArgument,
    GraphQLObjectType, GraphQLResolveInfo
)

from app import curd
from app.db_models import sa
from app.api.graph.schema import utils


async def id_resolve(root: sa.Subject, _info) -> int:
    return root.id


async def name_resolve(obj: sa.Subject, _info):
    return obj.name_cn or obj.name


async def get_by_id(root, _info: GraphQLResolveInfo, id):
    db = utils.get_db(_info)
    row = await curd.subject.get_by_id(db, id)
    return row


ep_type = GraphQLObjectType('Ep', fields={})
subject_type = GraphQLObjectType(
    name='Subject',
    fields={
        'id': GraphQLField(
            GraphQLNonNull(GraphQLString),
            description='The id of the human.',
            resolve=id_resolve
        ),
        'name': GraphQLField(
            GraphQLString, description='The name of the human.', resolve=name_resolve
        ),
    },
    description='A bgm.tv subject'
)

subject_args = {
    'id': GraphQLArgument(GraphQLNonNull(GraphQLInt), description='id of subject')
}

subject_field = GraphQLField(subject_type, args=subject_args, resolve=get_by_id)
