import graphene
from baecommerce.api.schema import Query as ProductQuery
from baecommerce.api.schema import Mutation as ProductMutation


class Query(ProductQuery, graphene.ObjectType):
    pass


class Mutation(ProductMutation, graphene.ObjectType):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)
