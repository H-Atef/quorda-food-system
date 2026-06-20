from django.contrib import admin
from apps.orders.models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ('menu_item', 'quantity')
    readonly_fields = ()


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'restaurant', 'customer', 'is_indoor', 'status',
        'special_flag', 'created_at',
    )
    list_filter = ('status', 'is_indoor', 'special_flag', 'restaurant')
    search_fields = ('restaurant__restaurant_name', 'customer__username')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'menu_item', 'quantity')
    search_fields = ('menu_item__name', 'order__id')
