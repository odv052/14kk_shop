from django.db.models import F
from rest_framework.generics import ListAPIView
from django_filters import rest_framework as filters
from rest_framework.pagination import PageNumberPagination
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


class OrderFilter(filters.FilterSet):
    favorite_m = filters.BooleanFilter(method='favorite_m_filter')
    price_differ = filters.BooleanFilter(method='price_differ_filter')
    manufacturer = filters.NumberFilter('orderitem__product__manufacturer')
    product = filters.NumberFilter('orderitem__product')

    class Meta:
        model = Order
        fields = {
            'total_price': ['lte', 'gte'],
            'status': ['exact'],
        }

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
            ids = queryset.order_by('id').exclude(
                orderitem__price=F('orderitem__product__price')
            ).distinct('id').values('id')
            return queryset.filter(id__in=ids)


class OrderView(ListAPIView):
    queryset = Order.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = OrderFilter
    serializer_class = OrderSerializer
    pagination_class = PageNumberPagination

    def perform_authentication(self, request):
        request.user = User.objects.get(id=request.query_params['user'])

    def get_queryset(self):
        queryset = super().get_queryset()
        user_allowed_statuses = OrderStatus.objects.filter(group__user=self.request.user).values('id')
        if 'ordering' in self.request.query_params:
            assert self.request.query_params['ordering'].strip('-') in ('created', 'total_price')
            order = self.request.query_params['ordering']
        else:
            order = '-created'
        return queryset.filter(status__in=user_allowed_statuses)\
            .order_by(order)\
            .prefetch_related('orderitem_set', 'status')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
