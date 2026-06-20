from django.db import models
from django.conf import settings
import uuid


class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    restaurant = models.ForeignKey(
        'users.RestaurantProfile',
        on_delete=models.CASCADE,
        related_name='orders',
    )
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders',
        help_text='Required when is_indoor=False (delivery). Optional for dine-in.',
    )
    is_indoor = models.BooleanField(
        default=True,
        help_text='True = dine-in (no customer required). False = delivery (customer required).',
    )
    status = models.CharField(
        max_length=20,
        choices=(
            ('pending', 'Pending'),
            ('preparing', 'Preparing'),
            ('done', 'Done'),
        ),
        default='pending',
    )
    special_flag = models.BooleanField(
        default=False,
        help_text='VIP order — sorted by ID before normal orders.',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        ordering = ['-created_at']

    @property
    def total_quantity(self):
        return sum(item.quantity for item in self.order_items.all())

    @property
    def total_prep_time(self):
        return sum(item.menu_item.prep_time * item.quantity for item in self.order_items.all())

    @property
    def total_cost(self):
        return sum(float(item.menu_item.price) * item.quantity for item in self.order_items.all())

    @property
    def priority_score(self):
        from apps.orders.helpers.priority_calculator import PriorityCalculator
        return PriorityCalculator.compute_score(self)

    def __str__(self):
        return f"Order #{self.id} — {self.restaurant.restaurant_name} [{self.status}]"


class OrderItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='order_items',
    )
    menu_item = models.ForeignKey(
        'restaurants.MenuItem',
        on_delete=models.PROTECT,
        related_name='order_items',
    )
    quantity = models.PositiveIntegerField()

    class Meta:
        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'

    @property
    def total_prep_time(self):
        return self.menu_item.prep_time * self.quantity

    @property
    def total_price(self):
        return float(self.menu_item.price) * self.quantity

    def __str__(self):
        return f"{self.quantity}x {self.menu_item.name} (Order #{self.order_id})"
