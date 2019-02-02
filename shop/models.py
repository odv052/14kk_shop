# 15:26 - 19:30
from django.db import models, transaction, connection
from django.db.models import F
from django.db.models.expressions import CombinedExpression, Combinable


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

    @classmethod
    def from_db(cls, db, field_names, values):
        return super().from_db(db, field_names, values)

    def save(self, *args, **kwargs):
        # update total_price by changing delivery_price
        if not self._state.adding:
            if isinstance(self.total_price, Combinable):
                self.total_price = self.total_price - F('delivery_price') + self.delivery_price
            else:
                self.total_price = F('total_price') - F('delivery_price') + self.delivery_price
            super().save(*args, **kwargs)
            self.refresh_from_db(fields=('total_price', )) # possible to use deferred field instead
        else:
            self.total_price = self.delivery_price
            super().save(*args, **kwargs)


class OrderItem(models.Model):
    created = models.DateField(auto_now_add=True)
    order = models.ForeignKey('Order', models.PROTECT)
    product = models.ForeignKey('Product', models.PROTECT)
    price = models.IntegerField()

    class Meta:
        unique_together = ('order', 'product')

    def save(self, *args, **kwargs):
        if not self._state.adding:
            with transaction.atomic():
                with connection.cursor() as cursor:
                    cursor.execute(
                        'UPDATE {order_table} O '
                        'SET total_price = O.total_price + %s - '
                        '(SELECT price FROM {orderitem_table} I WHERE I.id = %s) WHERE O.id = %s'.format(
                            order_table=Order._meta.db_table,
                            orderitem_table=self._meta.db_table,
                        ),
                        [self.price, self.pk, self.product_id]
                    )
                super().save()
        else:
            with transaction.atomic():
                super().save()
                self.order.total_price = F('total_price') + self.price
                self.order.save()


class Product(models.Model):
    sku = models.TextField(unique=True)
    price = models.IntegerField()
    manufacturer = models.ForeignKey('Manufacturer', models.PROTECT)


class Manufacturer(models.Model):
    name = models.TextField(unique=True)
