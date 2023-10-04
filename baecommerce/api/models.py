from django.db import models


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
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, blank=True, null=True
    )

    def __str__(self):
        return f"{self.title}"
