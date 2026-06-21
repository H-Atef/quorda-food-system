from django.db import models
import uuid


class MenuItem(models.Model):
    """
    A menu item belonging to a Category (optional), which is scoped to a restaurant.
    Mirrors the MenuItem dataclass: category (optional), name, prep_time (minutes), price, restaurant.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    restaurant = models.ForeignKey(
        'users.RestaurantProfile',
        on_delete=models.CASCADE,
        related_name='menu_items',
        null=True,
        blank=True,
        help_text='Restaurant that owns this menu item.',
    )
    category = models.ForeignKey(
        'restaurants.Category',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='menu_items',
        help_text='Optional category for this menu item.',
    )
    name = models.CharField(max_length=200)
    prep_time = models.PositiveIntegerField(help_text='Preparation time in minutes')
    price = models.DecimalField(max_digits=8, decimal_places=2)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Menu Item'
        verbose_name_plural = 'Menu Items'
        ordering = ['category__priority', 'name']
        constraints = [
            models.UniqueConstraint(
                fields=['restaurant', 'name'],
                name='unique_menuitem_restaurant_name'
            )
        ]

    def __str__(self):
        cat = self.category.name if self.category else 'no category'
        return f"{self.name} — {cat} (${self.price})"
