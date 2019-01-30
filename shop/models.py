# 15:26 - 19:30
from django.db import models


class User(models.Model):
    allowed_groups = models.ManyToManyField('StatusGroup')
    favorite_manufactures = models.ManyToManyField('Manufacturer')


class StatusGroup(models.Model):
    name = models.TextField(unique=True)


class OrderStatus(models.Model):
    name = models.TextField(unique=True)
    group = models.ForeignKey('StatusGroup', models.CASCADE)


class Order(models.Model):
    created = models.DateField(auto_now_add=True, db_index=True)
    number = models.TextField(unique=True)
    delivery_price = models.IntegerField(default=0)
    status = models.ForeignKey('OrderStatus', models.PROTECT)
    total_price = models.IntegerField(default=0, db_index=True)


class OrderItem(models.Model):
    created = models.DateField(auto_now_add=True)
    order = models.ForeignKey('Order', models.PROTECT)
    product = models.ForeignKey('Product', models.PROTECT)
    price = models.IntegerField()

    class Meta:
        unique_together = ('order', 'product')


class Product(models.Model):
    sku = models.TextField(unique=True)
    price = models.IntegerField()
    manufacturer = models.ForeignKey('Manufacturer', models.PROTECT)


class Manufacturer(models.Model):
    name = models.TextField(unique=True)
