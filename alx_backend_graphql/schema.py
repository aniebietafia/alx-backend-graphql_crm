import graphene

from alx_backend_graphql.crm_query import CRMQuery


class Query(CRMQuery, graphene.ObjectType):
    hello = graphene.String(default_value="Hello, GraphQL!")


schema = graphene.Schema(query=Query)
