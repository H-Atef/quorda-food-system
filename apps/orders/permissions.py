from rest_framework.permissions import BasePermission


class IsRestaurantOwner(BasePermission):
    """Restaurant users may only act on their own orders."""

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and hasattr(request.user, 'restaurant_profile')
        )

    def has_object_permission(self, request, view, obj):
        return obj.restaurant_id == request.user.restaurant_profile.id
    
class IsOrderItemOwner(BasePermission):
    """Restaurant users may only act on items belonging to their own orders."""

    def has_object_permission(self, request, view, obj):
        return obj.order.restaurant_id == request.user.restaurant_profile.id