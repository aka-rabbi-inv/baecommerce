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
        first_name = graphene.String()
        last_name = graphene.String()
        phone = graphene.String()

    user = graphene.Field(CustomUserNode)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **kwargs):
        user = CustomUser.objects.create_user(**kwargs)
        return CustomUserRegistrationRelay(user=user)


class MeUpdateRelay(relay.ClientIDMutation):
    class Input:
        username = graphene.String()
        password = graphene.String()
        email = graphene.String()

    user = graphene.Field(CustomUserNode)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **kwargs):
        user = info.context.user
        user.username = kwargs.get("username", user.username)
        user.password = kwargs.get("password", user.password)
        user.email = kwargs.get("email", user.email)
        user.save()
        return MeUpdateRelay(user=user)


class Query(graphene.ObjectType):
    all_users = DjangoFilterConnectionField(CustomUserNode)
    me_query = graphene.Field(CustomUserNode)

    def resolve_me_query(self, info):
        user = info.context.user
        if user.is_authenticated:
            return user
        return None


class Mutation(graphene.ObjectType):
    register = CustomUserRegistrationRelay.Field()
    me_update = MeUpdateRelay.Field()
