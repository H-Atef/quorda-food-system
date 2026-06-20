from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
import uuid


class Criteria(models.Model):
    """
    Simple-order detection criteria for a restaurant.
    One criteria set per restaurant (OneToOneField).
    Mirrors the Criteria dataclass: max_quantity, min_category_priority.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    restaurant = models.OneToOneField(
        'users.RestaurantProfile',
        on_delete=models.CASCADE,
        related_name='criteria',
    )
    max_quantity = models.PositiveIntegerField(
        help_text='Max total quantity for an order to be considered simple',
    )
    min_category_priority = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text='Minimum category priority required for a simple order',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Criteria'
        verbose_name_plural = 'Criteria'

    def __str__(self):
        return (
            f"Criteria for {self.restaurant.restaurant_name} "
            f"(max_qty={self.max_quantity}, min_prio={self.min_category_priority})"
        )
