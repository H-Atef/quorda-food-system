from django.db import models
from django.conf import settings
import uuid


class RestaurantProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='restaurant_profile',
    )
    restaurant_name = models.CharField(max_length=200, unique=True)
    address = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    logo_url = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Restaurant Profile'
        verbose_name_plural = 'Restaurant Profiles'

    def __str__(self):
        return f"{self.restaurant_name} ({self.user.username})"
