import graphene
from graphene import relay
from graphene_django.types import DjangoObjectType
from .models import Product, Category
import graphql_jwt
from graphene_django.filter import DjangoFilterConnectionField
from graphql_relay import from_global_id


class CategoryNode(DjangoObjectType):
    class Meta:
        model = Category
        filter_fields = {
            "name": [
                "exact",
                "icontains",
                "istartswith",
            ],
        }
        interfaces = (relay.Node,)


class ProductNode(DjangoObjectType):
    class Meta:
        model = Product
        filter_fields = {
            "title": [
                "exact",
                "icontains",
                "istartswith",
            ],
            "price": [
                "exact",
            ],
        }
        interfaces = (relay.Node,)


class ProductCreateMutaionRelay(relay.ClientIDMutation):
    class Input:
        title = graphene.String(required=True)
        price = graphene.Float(required=True)
        description = graphene.String()
        image = graphene.String()
        category_id = graphene.ID()

    product = graphene.Field(ProductNode)

    @classmethod
    def mutate_and_get_payload(cls, root, info, category_id, **kwargs):
        product = Product.objects.create(**kwargs)

        if category_id:
            category = Category.objects.get(pk=from_global_id(category_id)[1])
            product.category = category
        product.save()
        return ProductCreateMutaionRelay(product=product)


class ProductUpdateMutaionRelay(relay.ClientIDMutation):
    class Input:
        title = graphene.String()
        price = graphene.Float()
        description = graphene.String()
        image = graphene.String()
        category_id = graphene.ID()
        id = graphene.ID(required=True)

    product = graphene.Field(ProductNode)

    @classmethod
    def mutate_and_get_payload(cls, root, info, id, **kwargs):
        product = Product.objects.get(pk=from_global_id(id)[1])

        if title := kwargs.get("title"):
            product.title = title
        if price := kwargs.get("price"):
            product.price = price
        if description := kwargs.get("description"):
            product.description = description
        if image := kwargs.get("image"):
            product.image = image
        if category_id := kwargs.get("category_id"):
            category = Category.objects.get(pk=from_global_id(category_id)[1])
            product.category = category

        product.save()
        return ProductUpdateMutaionRelay(product=product)


class ProductDeleteMutaionRelay(relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)

    product = graphene.Field(ProductNode)

    @classmethod
    def mutate_and_get_payload(cls, root, info, id):
        product = Product.objects.get(pk=from_global_id(id)[1])
        product.delete()
        return ProductDeleteMutaionRelay(product=None)


class Query(graphene.ObjectType):
    all_products = DjangoFilterConnectionField(ProductNode)
    all_categories = DjangoFilterConnectionField(CategoryNode)


class Mutation:
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()

    create_product = ProductCreateMutaionRelay.Field()
    update_product = ProductUpdateMutaionRelay.Field()
    delete_product = ProductDeleteMutaionRelay.Field()
