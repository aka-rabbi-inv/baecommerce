from django.db import models
from users.models import CustomUser as User


class Category(models.Model):
    name = models.CharField(max_length=32, blank=False)
    description = models.TextField(blank=True, null=True)
    image = models.CharField(max_length=256, blank=True, null=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return f"{self.name}"


class Product(models.Model):
    title = models.CharField(max_length=32, blank=False)
    price = models.FloatField(default=2000, blank=False)
    description = models.TextField(blank=True)
    image = models.CharField(max_length=256, blank=True)
    stock = models.IntegerField(default=0)
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, blank=True, null=True
    )

    def __str__(self):
        return f"{self.title}"


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.IntegerField(default=0)


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()


class Order(models.Model):
    cart = models.ForeignKey(Cart, related_name="orders", on_delete=models.CASCADE)
    total = models.FloatField(default=0)
    status = models.IntegerField(default=0)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
