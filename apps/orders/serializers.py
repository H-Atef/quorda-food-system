from rest_framework import serializers
from apps.orders.models import Order, OrderItem


class OrderItemWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['menu_item', 'quantity']

    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError('quantity must be at least 1.')
        return value


class OrderItemReadSerializer(serializers.ModelSerializer):
    menu_item_name = serializers.CharField(source='menu_item.name', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'menu_item', 'menu_item_name', 'quantity']


class OrderSerializer(serializers.ModelSerializer):
    """Read serializer."""
    order_items = OrderItemReadSerializer(many=True, read_only=True)
    total_quantity = serializers.ReadOnlyField()
    total_prep_time = serializers.ReadOnlyField()
    total_cost = serializers.ReadOnlyField()

    class Meta:
        model = Order
        fields = [
            'id', 'restaurant', 'customer', 'is_indoor', 'status',
            'special_flag', 'priority_score', 'order_items',
            'total_quantity', 'total_prep_time', 'total_cost',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'priority_score', 'created_at', 'updated_at']


class OrderWriteSerializer(serializers.ModelSerializer):
    """Create/update serializer with nested order_items."""
    order_items = OrderItemWriteSerializer(many=True)

    class Meta:
        model = Order
        fields = ['id', 'customer', 'is_indoor', 'status', 'special_flag', 'order_items']
        read_only_fields = ['id']

    def validate(self, attrs):
        if not attrs.get('is_indoor', True) and not attrs.get('customer'):
            raise serializers.ValidationError('customer is required for delivery orders.')
        return attrs

    def create(self, validated_data):
        items_data = validated_data.pop('order_items')
        restaurant = self.context['request'].user.restaurant_profile
        order = Order.objects.create(restaurant=restaurant, **validated_data)
        OrderItem.objects.bulk_create([
            OrderItem(order=order, **item) for item in items_data
        ])
        order.recalculate_priority_score()
        return order

    def update(self, instance, validated_data):
        items_data = validated_data.pop('order_items', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if items_data is not None:
            instance.order_items.all().delete()
            OrderItem.objects.bulk_create([
                OrderItem(order=instance, **item) for item in items_data
            ])
            instance.recalculate_priority_score()

        return instance