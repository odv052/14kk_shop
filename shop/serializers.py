from rest_framework import serializers

from shop.models import User, StatusGroup, OrderStatus, Order, OrderItem, Product, Manufacturer


class OrderStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderStatus
        fields = ('name', 'group')


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ('created', 'order', 'product', 'price')


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ('id', 'created', 'number', 'delivery_price', 'status', 'total_price', 'items')

    items = OrderItemSerializer(many=True, source='orderitem_set')
