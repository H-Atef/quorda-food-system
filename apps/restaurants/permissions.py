from rest_framework.permissions import BasePermission
from apps.users.helpers.constants import UserRole


class IsRestaurantOwner(BasePermission):
    """
    Allows access only to authenticated users with role=RESTAURANT
    who also have a RestaurantProfile attached.
    """
    message = 'Only restaurant accounts with an active profile may access this resource.'

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == UserRole.RESTAURANT
            and hasattr(request.user, 'restaurant_profile')
        )
