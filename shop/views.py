from django.db.models import F, Sum, Q
from rest_framework.filters import OrderingFilter
from rest_framework.generics import ListAPIView
from django_filters import rest_framework as filters
from rest_framework.pagination import PageNumberPagination, CursorPagination
from rest_framework.response import Response

from shop.models import User, StatusGroup, OrderStatus, Order, OrderItem, Product, Manufacturer

# Написать Viewset, который отображает список заказов.
# Заказы должны быть отфильтрованы по группе статусов заказов, с которыми работает этот пользователь.

# Опциональные фильтры:
# 1. Фильтр по общей стоимости заказа, включая цену доставки. Больше\меньше и одновременно использование
# 2. Фильтр заказов только по тем поставщикам, которые пользователь добавил в favorites
# 3. Фильтр по поставщику
# 4. Фильтр по продукту
# 5. Фильтр по заказам, в которых цена продажи не совпадает с ценой продукта
# 6. Фильтр по статусу

# Сортировка.
# 1. По умолчанию отображать сначала самые новые заказы.
# 2. Дать возможность сортировки по времени создания заказа и по общей сумме.

# В ответа должна быть выведена  структура заказа со вложенными объектами,
# как в базе - OrderItem, OrderStatus
from shop.serializers import OrderSerializer


def annotate_queryset_with_slow_total_price(queryset):
    if 'slow_total_price' not in queryset.query.annotations:
        return queryset.annotate(slow_total_price=Sum('orderitem__price') + F('delivery_price'))


class OrderFilter(filters.FilterSet):
    favorite_m = filters.BooleanFilter(method='favorite_m_filter')
    price_differ = filters.BooleanFilter(method='price_differ_filter')
    manufacturer = filters.NumberFilter('orderitem__product__manufacturer')
    product = filters.NumberFilter('orderitem__product')
    fast_total_price__lte = filters.NumberFilter('total_price', lookup_expr='lte')
    fast_total_price__gte = filters.NumberFilter('total_price', lookup_expr='gte')
    slow_total_price__lte = filters.NumberFilter(method='slow_total_price_filter')
    slow_total_price__gte = filters.NumberFilter(method='slow_total_price_filter')

    class Meta:
        model = Order
        fields = ('status', )

    def favorite_m_filter(self, queryset, name, value):
        if value is False:
            return queryset
        else:
            return queryset.filter(
                orderitem__product__manufacturer__in=
                self.request.user.favorite_manufactures.values('id')
            )

    def price_differ_filter(self, queryset, name, value):
        if value is False:
            return queryset
        else:
            ids = queryset.order_by('id').filter(
                ~Q(orderitem__price=F('orderitem__product__price'))
            ).distinct('id').values('id')
            return queryset.filter(id__in=ids)

    def slow_total_price_filter(self, queryset, name, value):
        queryset = annotate_queryset_with_slow_total_price(queryset)
        return queryset.filter(**{name: value})


class OrderView(ListAPIView):
    queryset = Order.objects.all()
    filter_backends = (filters.DjangoFilterBackend, OrderingFilter)
    filterset_class = OrderFilter
    serializer_class = OrderSerializer
    ordering_fields = ('created', 'total_price', 'slow_total_price')
    ordering = ('-created',)
    pagination_class = CursorPagination
    pagination_class.page_size_query_param = 'page_size'

    def perform_authentication(self, request):
        request.user = User.objects.get(id=request.query_params['user'])

    def get_queryset(self):
        queryset = super().get_queryset()
        user_allowed_statuses = OrderStatus.objects.filter(group__user=self.request.user).values('id')

        if self.request.query_params.get('ordering', '').endswith('slow_total_price'):
            queryset = annotate_queryset_with_slow_total_price(queryset)

        return queryset.filter(status__in=user_allowed_statuses)\
            .select_related('status')\
            .prefetch_related('orderitem_set')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
