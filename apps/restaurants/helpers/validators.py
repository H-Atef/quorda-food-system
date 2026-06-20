from rest_framework.exceptions import ValidationError
from apps.restaurants.models import Category


def validate_category_owner(category_id, restaurant_profile):
    """Ensure the category belongs to the requesting restaurant."""
    try:
        category = Category.objects.get(pk=category_id)
    except Category.DoesNotExist:
        raise ValidationError({'category': 'Category not found.'})
    if category.restaurant_id != restaurant_profile.id:
        raise ValidationError({'category': 'This category does not belong to your restaurant.'})
    return category


def validate_priority(value):
    if not (1 <= value <= 5):
        raise ValidationError({'priority': 'Priority must be between 1 and 5.'})
