import graphene
from graphene import relay
from graphene_django.types import DjangoObjectType
from .models import CustomUser
from graphene_django.filter import DjangoFilterConnectionField

# from graphql_jwt.decorators import login_required


class CustomUserNode(DjangoObjectType):
    class Meta:
        model = CustomUser
        filter_fields = {}
        interfaces = (relay.Node,)


class CustomUserRegistrationRelay(relay.ClientIDMutation):
    class Input:
        username = graphene.String(required=True)
        password = graphene.String(required=True)
        email = graphene.String(required=True)

    user = graphene.Field(CustomUserNode)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **kwargs):
        user = CustomUser.objects.create_user(**kwargs)
        return CustomUserRegistrationRelay(user=user)


class Query(graphene.ObjectType):
    all_users = DjangoFilterConnectionField(CustomUserNode)


class Mutation(graphene.ObjectType):
    register = CustomUserRegistrationRelay.Field()
