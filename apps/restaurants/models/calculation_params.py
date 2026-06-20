from django.db import models
import uuid


class RestaurantCalculationParams(models.Model):
    """
    Stores calculation parameters for a restaurant.
    One-to-many with RestaurantProfile — a restaurant can have multiple sets of params.
    These params are used by PriorityCalculator instead of hard-coded weights.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    restaurant = models.ForeignKey(
        'users.RestaurantProfile',
        on_delete=models.CASCADE,
        related_name='calculation_params',
    )
    time_weight = models.FloatField(
        default=0.4,
        help_text='Weight for time inverse score (e.g. 0.4)',
    )
    quantity_weight = models.FloatField(
        default=0.4,
        help_text='Weight for quantity inverse score (e.g. 0.4)',
    )
    category_weight = models.FloatField(
        default=0.2,
        help_text='Weight for category priority boost score (e.g. 0.2)',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Restaurant Calculation Params'
        verbose_name_plural = 'Restaurant Calculation Params'
        ordering = ['-created_at']

    def __str__(self):
        return (
            f"CalculationParams for {self.restaurant.restaurant_name} "
            f"(time={self.time_weight}, qty={self.quantity_weight}, cat={self.category_weight})"
        )
