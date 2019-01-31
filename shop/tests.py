from django.db.models import Avg, F
from django.test import TestCase
from django.urls import reverse
from shop.models import User, StatusGroup, OrderStatus, Order, OrderItem, Product, Manufacturer
from shop.factories import ManufacturerFactory, ProductFactory, OrderFactory, OrderItemFactory
from shop.serializers import OrderSerializer


class ShopAbstractTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('shop:order')

        st_group_in_process = StatusGroup.objects.create(name='in process')
        st_group_finished = StatusGroup.objects.create(name='finished')

        OrderStatus.objects.create(name='new', group=st_group_in_process)
        OrderStatus.objects.create(name='in work', group=st_group_in_process)
        OrderStatus.objects.create(name='closed', group=st_group_finished)

        ManufacturerFactory.create_batch(10)
        ProductFactory.create_batch(30)
        OrderFactory.create_batch(15)

        cls.user = User.objects.create()
        cls.user.allowed_groups.add(st_group_in_process)
        cls.user.favorite_manufactures.set(Manufacturer.objects.all()[:5])


class OrderViewTestCase(ShopAbstractTestCase):
    def test_favorite_m_filter(self):
        response = self.client.get(self.url, {
            'user': self.user.id,
            'favorite_m': True,
        })
        count = Order.objects.filter(
            status__group__in=self.user.allowed_groups.values('id'),
            orderitem__product__manufacturer__in=self.user.favorite_manufactures.values('id')
        ).count()
        self.assertEqual(len(response.data['results']), count)

    def test_fast_total_price_lte_filter(self):
        avg_total_price = Order.objects.aggregate(avg=Avg('total_price'))['avg']
        response = self.client.get(self.url, {
            'user': self.user.id,
            'fast_total_price__lte': avg_total_price,
        })
        count = Order.objects.filter(
            status__group__in=self.user.allowed_groups.values('id'),
            total_price__lte=avg_total_price,
        ).count()
        self.assertEqual(len(response.data['results']), count)

    def test_fast_total_price_gte_filter(self):
        avg_total_price = Order.objects.aggregate(avg=Avg('total_price'))['avg']
        response = self.client.get(self.url, {
            'user': self.user.id,
            'fast_total_price__gte': avg_total_price,
        })
        count = Order.objects.filter(
            status__group__in=self.user.allowed_groups.values('id'),
            total_price__gte=avg_total_price,
        ).count()
        self.assertEqual(len(response.data['results']), count)

    def test_slow_total_price_lte_filter(self):
        avg_total_price = Order.objects.aggregate(avg=Avg('total_price'))['avg']
        response = self.client.get(self.url, {
            'user': self.user.id,
            'slow_total_price__lte': avg_total_price,
        })
        count = Order.objects.filter(
            status__group__in=self.user.allowed_groups.values('id'),
            total_price__lte=avg_total_price,
        ).count()
        self.assertEqual(len(response.data['results']), count)

    def test_slow_total_price_gte_filter(self):
        avg_total_price = Order.objects.aggregate(avg=Avg('total_price'))['avg']
        response = self.client.get(self.url, {
            'user': self.user.id,
            'slow_total_price__gte': avg_total_price,
        })
        count = Order.objects.filter(
            status__group__in=self.user.allowed_groups.values('id'),
            total_price__gte=avg_total_price,
        ).count()
        self.assertEqual(len(response.data['results']), count)

    def test_product_filter(self):
        product_id = Product.objects.filter(
            orderitem__order__status__group__in=self.user.allowed_groups.values('id')
        ).first().id
        response = self.client.get(self.url, {
            'user': self.user.id,
            'product': product_id,
        })
        count = Order.objects.filter(
            status__group__in=self.user.allowed_groups.values('id'),
            orderitem__product=product_id,
        ).count()
        self.assertEqual(len(response.data['results']), count)

    def test_status_filter(self):
        status_id = OrderStatus.objects.filter(
            group__in=self.user.allowed_groups.values('id')
        ).first().id
        response = self.client.get(self.url, {
            'user': self.user.id,
            'status': status_id,
        })
        count = Order.objects.filter(
            status__group__in=self.user.allowed_groups.values('id'),
            status=status_id,
        ).count()
        self.assertEqual(len(response.data['results']), count)

    def test_price_differ_filter(self):
        self.user.allowed_groups.set(StatusGroup.objects.all())

        item = OrderItem.objects.first()
        item.price = item.product.price + 10
        item.save()

        response = self.client.get(self.url, {
            'user': self.user.id,
            'price_differ': True,
        })
        count = Order.objects.exclude(orderitem__price=F('orderitem__product__price')).distinct('id').count()
        self.assertEqual(len(response.data['results']), count)

    def test_default_created_desc_ordering(self):
        response = self.client.get(self.url, {
            'user': self.user.id,
        })
        first_id = Order.objects.filter(
            status__group__in=self.user.allowed_groups.values('id'),
        ).order_by('-created').first().id
        self.assertEqual(response.data['results'][0]['id'], first_id)

    def test_created_asc_ordering(self):
        response = self.client.get(self.url, {
            'user': self.user.id,
            'ordering': 'created'
        })
        first_id = Order.objects.filter(
            status__group__in=self.user.allowed_groups.values('id'),
        ).order_by('created').first().id
        self.assertEqual(response.data['results'][0]['id'], first_id)

    def test_total_price_desc_ordering(self):
        response = self.client.get(self.url, {
            'user': self.user.id,
            'ordering': '-total_price'
        })
        first_id = Order.objects.filter(
            status__group__in=self.user.allowed_groups.values('id'),
        ).order_by('-total_price').first().id
        self.assertEqual(response.data['results'][0]['id'], first_id)

    def test_total_price_asc_ordering(self):
        response = self.client.get(self.url, {
            'user': self.user.id,
            'ordering': 'total_price'
        })
        first_id = Order.objects.filter(
            status__group__in=self.user.allowed_groups.values('id'),
        ).order_by('total_price').first().id
        self.assertEqual(response.data['results'][0]['id'], first_id)

    def test_slow_total_price_desc_ordering(self):
        response = self.client.get(self.url, {
            'user': self.user.id,
            'ordering': '-slow_total_price'
        })
        first_id = Order.objects.filter(
            status__group__in=self.user.allowed_groups.values('id'),
        ).order_by('-total_price').first().id
        self.assertEqual(response.data['results'][0]['id'], first_id)

    def test_slow_total_price_asc_ordering(self):
        response = self.client.get(self.url, {
            'user': self.user.id,
            'ordering': 'slow_total_price'
        })
        first_id = Order.objects.filter(
            status__group__in=self.user.allowed_groups.values('id'),
        ).order_by('total_price').first().id
        self.assertEqual(response.data['results'][0]['id'], first_id)


class OrderSaveModelTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        ManufacturerFactory.create()
        ProductFactory.create()
        OrderStatus.objects.create(name='', group=StatusGroup.objects.create(name=''))

    def test_update_delivery_price(self):
        order = OrderFactory(gen_order_items=False, set_total_price=False, delivery_price=30)
        self.assertEqual(order.total_price, order.delivery_price)
        price = 40
        order.delivery_price = price
        order.save()
        self.assertEqual(order.total_price, 40)
        order.refresh_from_db()
        self.assertEqual(order.total_price, 40)


class OrderItemSaveModelTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        ManufacturerFactory.create_batch(3)
        ProductFactory.create_batch(3)
        OrderStatus.objects.create(name='', group=StatusGroup.objects.create(name=''))
        cls.order = OrderFactory.create(gen_order_items=False, set_total_price=False)

    def setUp(self):
        self.order.refresh_from_db()

    def test_item_creation_update_product(self):
        old_price = self.order.total_price
        item = OrderItemFactory.build(order=self.order)
        item.save()
        self.order.refresh_from_db()
        self.assertEqual(self.order.total_price, old_price + item.price)

    def test_item_change_price_update_product(self):
        old_price = self.order.total_price
        item = OrderItemFactory.build(order=self.order)
        item.save()
        self.order.refresh_from_db()
        self.assertEqual(self.order.total_price, old_price + item.price)
        item.price += 10
        item.save()
        self.order.refresh_from_db()
        self.assertEqual(self.order.total_price, old_price + item.price)


class OrderSerializerTestCase(ShopAbstractTestCase):
    def test_serializer(self):
        order = Order.objects.first()
        serializer = OrderSerializer(instance=order)
        serializer.data