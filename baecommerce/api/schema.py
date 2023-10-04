import graphene
from graphene import relay
from graphene_django.types import DjangoObjectType
from .models import Product, Category, CartItem, Cart
import graphql_jwt
from graphene_django.filter import DjangoFilterConnectionField
from graphql_relay import from_global_id


class CartNode(DjangoObjectType):
    class Meta:
        model = Cart
        filter_fields = {
            "status": [
                "exact",
            ],
        }
        interfaces = (relay.Node,)


class CartItemNode(DjangoObjectType):
    class Meta:
        model = CartItem
        filter_fields = {}
        interfaces = (relay.Node,)


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


class CartStatusUpdateMutaionRelay(relay.ClientIDMutation):
    class Input:
        status = graphene.Int(required=True)
        id = graphene.ID(required=True)

    cart = graphene.Field(CartNode)

    @classmethod
    def mutate_and_get_payload(cls, root, info, id, status):
        cart = Cart.objects.get(pk=from_global_id(id)[1])

        cart.status = status
        cart.save()

        return CartStatusUpdateMutaionRelay(cart=cart)


class Query(graphene.ObjectType):
    all_products = DjangoFilterConnectionField(ProductNode)
    all_categories = DjangoFilterConnectionField(CategoryNode)
    all_carts = DjangoFilterConnectionField(CartNode)
    all_cart_items = DjangoFilterConnectionField(CartItemNode)

    my_cart_items = graphene.List(CartItemNode)
    my_cart = graphene.Field(CartNode)

    def resolve_my_cart(self, info):
        user = info.context.user
        if user.is_authenticated:
            cart = Cart.objects.filter(user=user, status=0).first()
            if not cart:
                cart = Cart.objects.create(user=user, status=0)
            return cart
        return None

    def resolve_my_cart_items(self, info):
        user = info.context.user
        if user.is_authenticated:
            cart = Cart.objects.filter(user=user, status=0).first()
            cart_items = CartItem.objects.filter(cart=cart).all()
            return cart_items
        return None


class Mutation:
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()

    create_product = ProductCreateMutaionRelay.Field()
    update_product = ProductUpdateMutaionRelay.Field()
    delete_product = ProductDeleteMutaionRelay.Field()

    update_cart_status = CartStatusUpdateMutaionRelay.Field()
