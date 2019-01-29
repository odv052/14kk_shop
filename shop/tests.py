from django.db.models import Avg, F, Q
from django.test import TestCase
from django.urls import reverse
from shop.models import User, StatusGroup, OrderStatus, Order, OrderItem, Product, Manufacturer
from shop.factories import UserFactory, ManufacturerFactory, ProductFactory, OrderItemFactory, OrderFactory
from shop.serializers import OrderSerializer


class ShopAbstractTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.url = reverse('shop:order')

        st_group_in_process = StatusGroup.objects.create(name='in process')
        st_group_finished = StatusGroup.objects.create(name='finished')

        OrderStatus.objects.create(name='new', group=st_group_in_process)
        OrderStatus.objects.create(name='in work', group=st_group_in_process)
        OrderStatus.objects.create(name='closed', group=st_group_finished)

        ManufacturerFactory.create_batch(10)
        UserFactory.create_batch(10)
        ProductFactory.create_batch(30)
        OrderFactory.create_batch(15)


class OrderViewTestCase(ShopAbstractTestCase):
    def test_favorite_m_filter(self):
        user = User.objects.first()
        response = self.client.get(self.url, {
            'user': user.id,
            'favorite_m': True,
        })
        count = Order.objects.filter(
            status__group__in=user.allowed_groups.values('id'),
            orderitem__product__manufacturer__in=user.favorite_manufactures.values('id')
        ).count()
        self.assertEqual(response.data['count'], count)

    def test_total_price_lte_filter(self):
        avg_total_price = Order.objects.aggregate(avg=Avg('total_price'))['avg']
        user = User.objects.first()
        response = self.client.get(self.url,{
            'user': user.id,
            'total_price__lte': avg_total_price,
        })
        count = Order.objects.filter(
            status__group__in=user.allowed_groups.values('id'),
            total_price__lte=avg_total_price,
        ).count()
        self.assertEqual(response.data['count'], count)

    def test_total_price_gte_filter(self):
        avg_total_price = Order.objects.aggregate(avg=Avg('total_price'))['avg']
        user = User.objects.first()
        response = self.client.get(self.url,{
            'user': user.id,
            'total_price__gte': avg_total_price,
        })
        count = Order.objects.filter(
            status__group__in=user.allowed_groups.values('id'),
            total_price__gte=avg_total_price,
        ).count()
        self.assertEqual(response.data['count'], count)

    def test_product_filter(self):
        user = User.objects.first()
        product_id = Product.objects.filter(
            orderitem__order__status__group__in=user.allowed_groups.values('id')
        ).first().id
        response = self.client.get(self.url, {
            'user': user.id,
            'product': product_id,
        })
        count = Order.objects.filter(
            status__group__in=user.allowed_groups.values('id'),
            orderitem__product=product_id,
        ).count()
        self.assertEqual(response.data['count'], count)

    def test_status_filter(self):
        user = User.objects.first()
        status_id = OrderStatus.objects.filter(
            group__in=user.allowed_groups.values('id')
        ).first().id
        response = self.client.get(self.url, {
            'user': user.id,
            'status': status_id,
        })
        count = Order.objects.filter(
            status__group__in=user.allowed_groups.values('id'),
            status=status_id,
        ).count()
        self.assertEqual(response.data['count'], count)

    def test_price_differ_filter(self):
        user = User.objects.first()
        user.allowed_groups.set(StatusGroup.objects.all())

        item = OrderItem.objects.first()
        item.price = item.product.price + 10
        item.save()

        response = self.client.get(self.url, {
            'user': user.id,
            'price_differ': True,
        })
        count = Order.objects.exclude(orderitem__price=F('orderitem__product__price')).distinct('id').count()
        self.assertEqual(response.data['count'], count)

    def test_default_created_desc_ordering(self):
        user = User.objects.first()
        response = self.client.get(self.url, {
            'user': user.id,
        })
        first_id = Order.objects.filter(
            status__group__in=user.allowed_groups.values('id'),
        ).order_by('-created').first().id
        self.assertEqual(response.data['results'][0]['id'], first_id)

    def test_created_asc_ordering(self):
        user = User.objects.first()
        response = self.client.get(self.url, {
            'user': user.id,
            'ordering': 'created'
        })
        first_id = Order.objects.filter(
            status__group__in=user.allowed_groups.values('id'),
        ).order_by('created').first().id
        self.assertEqual(response.data['results'][0]['id'], first_id)

    def test_total_price_desc_ordering(self):
        user = User.objects.first()
        response = self.client.get(self.url, {
            'user': user.id,
            'ordering': '-total_price'
        })
        first_id = Order.objects.filter(
            status__group__in=user.allowed_groups.values('id'),
        ).order_by('-total_price').first().id
        self.assertEqual(response.data['results'][0]['id'], first_id)

    def test_total_price_asc_ordering(self):
        user = User.objects.first()
        response = self.client.get(self.url, {
            'user': user.id,
            'ordering': 'total_price'
        })
        first_id = Order.objects.filter(
            status__group__in=user.allowed_groups.values('id'),
        ).order_by('total_price').first().id
        self.assertEqual(response.data['results'][0]['id'], first_id)


class OrderSerializerTestCase(ShopAbstractTestCase):
    def test_serializer(self):
        order = Order.objects.first()
        serializer = OrderSerializer(instance=order)
        serializer.data