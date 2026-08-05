from django.contrib import admin

from apps.orders.models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ['menu_item', 'quantity']
    raw_id_fields = ['menu_item']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'restaurant', 'customer', 'is_indoor', 'status',
        'special_flag', 'priority_score', 'total_quantity', 'total_cost',
        'created_at',
    ]
    list_filter = ['status', 'is_indoor', 'special_flag', 'restaurant']
    search_fields = ['id', 'restaurant__restaurant_name', 'customer__username', 'customer__email']
    readonly_fields = ['id', 'priority_score', 'created_at', 'updated_at']
    raw_id_fields = ['restaurant', 'customer']
    inlines = [OrderItemInline]
    list_select_related = ['restaurant', 'customer']

    @admin.display(description='Total qty')
    def total_quantity(self, obj):
        return obj.total_quantity

    @admin.display(description='Total cost')
    def total_cost(self, obj):
        return obj.total_cost


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'menu_item', 'quantity']
    search_fields = ['id', 'order__id', 'menu_item__name']
    raw_id_fields = ['order', 'menu_item']
    list_select_related = ['order', 'menu_item']