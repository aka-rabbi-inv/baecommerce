import graphene
from baecommerce.api.schema import Query as ProductQuery
from baecommerce.api.schema import Mutation as ProductMutation
from users.schema import Query as UserQuery
from users.schema import Mutation as UserMutation


class Query(ProductQuery, UserQuery, graphene.ObjectType):
    pass


class Mutation(ProductMutation, UserMutation, graphene.ObjectType):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)
