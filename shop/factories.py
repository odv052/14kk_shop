from datetime import timedelta, date
from random import randint, choice

import factory.fuzzy
from django.db.models import Sum

from shop.models import User, StatusGroup, OrderStatus, Order, OrderItem, Product, Manufacturer


class UserFactory(factory.DjangoModelFactory):
    class Meta:
        model = User

    @factory.post_generation
    def gen_status_groups_and_favorite_manufacturers(self, *args, **kwargs):
        man_ids = Manufacturer.objects.values_list('id', flat=True)
        self.favorite_manufactures.set([choice(man_ids) for _ in range(randint(1, 10))])

        st_groups_ids = StatusGroup.objects.values_list('id', flat=True)
        self.allowed_groups.set([choice(st_groups_ids) for _ in range(randint(1, 2))])


class ManufacturerFactory(factory.DjangoModelFactory):
    class Meta:
        model = Manufacturer

    name = factory.Faker('name')


class ProductFactory(factory.DjangoModelFactory):
    class Meta:
        model = Product

    sku = factory.fuzzy.FuzzyText()
    price = factory.fuzzy.FuzzyInteger(10, 100)
    manufacturer = factory.Iterator(Manufacturer.objects.all())


class OrderItemFactory(factory.DjangoModelFactory):
    class Meta:
        model = OrderItem

    product = factory.Iterator(Product.objects.all())
    price = factory.fuzzy.FuzzyInteger(10, 100)

    @factory.post_generation
    def fix_price(self, *args, **kwargs):
        if randint(1, 10) == 5:
            return
        self.price = self.product.price


class OrderFactory(factory.DjangoModelFactory):
    class Meta:
        model = Order

    number = factory.fuzzy.FuzzyText()
    delivery_price = factory.fuzzy.FuzzyInteger(10, 50)
    status = factory.Iterator(OrderStatus.objects.all())

    @factory.post_generation
    def gen_order_items(self, create, extracted=True, **kwargs):
        if not extracted:
            return
        for _ in range(randint(3, 10)):
            OrderItemFactory.build(order=self).save()

    @factory.post_generation
    def set_total_price(self, create, extracted=True, **kwargs):
        if not extracted:
            return
        self.total_price = self.delivery_price + \
                           OrderItem.objects.filter(order=self).aggregate(sum=Sum('price'))['sum']

    @factory.post_generation
    def set_update_created_date(self, create, extracted, **kwargs):
        self.created = (self.created or date.today()) - timedelta(days=randint(1, 365))
