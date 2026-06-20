from rest_framework import serializers
from apps.orders.models import Order, OrderItem
from apps.restaurants.models import MenuItem
from apps.users.helpers.constants import UserRole


class OrderItemSerializer(serializers.ModelSerializer):
    menu_item_name = serializers.CharField(source='menu_item.name', read_only=True)
    menu_item_price = serializers.DecimalField(
        source='menu_item.price', max_digits=8, decimal_places=2, read_only=True
    )
    total_price = serializers.SerializerMethodField()
    total_prep_time = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = (
            'id', 'menu_item', 'menu_item_name', 'menu_item_price',
            'quantity', 'total_price', 'total_prep_time',
        )
        read_only_fields = ('id', 'menu_item_name', 'menu_item_price', 'total_price', 'total_prep_time')

    def get_total_price(self, obj) -> float:
        return obj.total_price

    def get_total_prep_time(self, obj) -> int:
        return obj.total_prep_time


class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True)
    total_cost = serializers.SerializerMethodField()
    total_quantity = serializers.SerializerMethodField()
    total_prep_time = serializers.SerializerMethodField()
    priority_score = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = (
            'id', 'restaurant', 'customer', 'is_indoor', 'status', 'special_flag',
            'order_items',
            'total_cost', 'total_quantity', 'total_prep_time', 'priority_score',
            'created_at', 'updated_at',
        )
        read_only_fields = (
            'id', 'restaurant',
            'total_cost', 'total_quantity', 'total_prep_time', 'priority_score',
            'created_at', 'updated_at',
        )

    def get_total_cost(self, obj) -> float:
        return obj.total_cost

    def get_total_quantity(self, obj) -> int:
        return obj.total_quantity

    def get_total_prep_time(self, obj) -> int:
        return obj.total_prep_time

    def get_priority_score(self, obj) -> float:
        return obj.priority_score

    def validate(self, data):
        """If is_indoor=False (delivery), customer is required."""
        is_indoor = data.get('is_indoor', True)
        customer = data.get('customer')
        if not is_indoor and not customer:
            raise serializers.ValidationError(
                {'customer': 'customer is required for delivery orders (is_indoor=False).'}
            )
        return data

    def create(self, validated_data):
        items_data = validated_data.pop('order_items')
        order = Order.objects.create(**validated_data)
        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)
        return order

    def update(self, instance, validated_data):
        items_data = validated_data.pop('order_items', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if items_data is not None:
            instance.order_items.all().delete()
            for item_data in items_data:
                OrderItem.objects.create(order=instance, **item_data)
        return instance


class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    """Lightweight serializer for updating status only."""
    class Meta:
        model = Order
        fields = ('status',)
