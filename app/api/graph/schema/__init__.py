from graphql import GraphQLSchema, GraphQLObjectType

from app.api.graph.schema.subject import subject_field

schema = GraphQLSchema(
    query=GraphQLObjectType(
        name='Query',
        fields={'Subject': subject_field},
    )
)
