import graphene
from graphene import relay
from graphene_django.types import DjangoObjectType
from .models import Product, Category, CartItem, Cart, Order
import graphql_jwt
from graphene_django.filter import DjangoFilterConnectionField
from graphql_relay import from_global_id
from enum import Enum


class CartStatus(Enum):
    ACTIVE = 0
    INACTIVE = 1
    ARCHIVED = 2


class OrderStatus(Enum):
    PENDING = 0
    CHECKOUT = 1
    SHIPPED = 2
    DELIVERED = 3


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


class OrderNode(DjangoObjectType):
    class Meta:
        model = Order
        filter_fields = {
            "status": [
                "exact",
            ],
            "total": [
                "gt",
                "lt",
            ],
        }
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


class ProductCreateRelay(relay.ClientIDMutation):
    class Input:
        title = graphene.String(required=True)
        price = graphene.Float(required=True)
        description = graphene.String()
        image = graphene.String()
        category_id = graphene.ID()

    product = graphene.Field(ProductNode)

    @classmethod
    def mutate_and_get_payload(cls, root, info, category_id, **kwargs):
        if category_id:
            category = Category.objects.get(pk=from_global_id(category_id)[1])
        product = Product.objects.create(**kwargs)

        product.category = category if category_id else None
        product.save()
        return ProductCreateRelay(product=product)


class ProductUpdateRelay(relay.ClientIDMutation):
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
        return ProductUpdateRelay(product=product)


class ProductDeleteRelay(relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)

    product = graphene.Field(ProductNode)

    @classmethod
    def mutate_and_get_payload(cls, root, info, id):
        product = Product.objects.get(pk=from_global_id(id)[1])
        product.delete()
        return ProductDeleteRelay(product=None)


class CartStatusUpdateRelay(relay.ClientIDMutation):
    class Input:
        status = graphene.Int(required=True)
        id = graphene.ID(required=True)

    cart = graphene.Field(CartNode)

    @classmethod
    def mutate_and_get_payload(cls, root, info, id, status):
        cart = Cart.objects.get(pk=from_global_id(id)[1])

        cart.status = status
        cart.save()

        return CartStatusUpdateRelay(cart=cart)


class CheckoutRelay(relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)

    order = graphene.Field(OrderNode)

    @classmethod
    def mutate_and_get_payload(cls, root, info, id):
        order = Order.objects.get(pk=from_global_id(id)[1])

        order.status = OrderStatus.CHECKOUT.value
        order.cart.status = CartStatus.ARCHIVED.value
        order.cart.save()
        order.save()

        return CheckoutRelay(order=order)


class OrderStatusUpdateRelay(relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        status = graphene.Int(required=True)

    order = graphene.Field(OrderNode)

    @classmethod
    def mutate_and_get_payload(cls, root, info, id, status):
        order = Order.objects.get(pk=from_global_id(id)[1])

        order.status = status
        order.save()

        return OrderStatusUpdateRelay(order=order)


class Query(graphene.ObjectType):
    product = relay.Node.Field(ProductNode)
    all_products = DjangoFilterConnectionField(ProductNode)
    category = relay.Node.Field(CategoryNode)
    all_categories = DjangoFilterConnectionField(CategoryNode)
    all_carts = DjangoFilterConnectionField(CartNode)
    all_cart_items = DjangoFilterConnectionField(CartItemNode)
    all_orders = DjangoFilterConnectionField(OrderNode)

    my_cart_items = graphene.List(CartItemNode)
    my_cart = graphene.Field(CartNode)
    my_orders = graphene.List(OrderNode)

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

    def resolve_my_orders(self, info):
        user = info.context.user
        if user.is_authenticated:
            orders = Order.objects.filter(cart__user=user)
            return orders
        return None


class Mutation:
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()

    create_product = ProductCreateRelay.Field()
    update_product = ProductUpdateRelay.Field()
    delete_product = ProductDeleteRelay.Field()

    update_cart_status = CartStatusUpdateRelay.Field()

    update_order_status = OrderStatusUpdateRelay.Field()
    checkout_order = CheckoutRelay.Field()
