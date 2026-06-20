from rest_framework.permissions import BasePermission
from apps.users.helpers.constants import UserRole  


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == UserRole.ADMIN

class IsRestaurant(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == UserRole.RESTAURANT

class IsCustomer(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == UserRole.CUSTOMER

class IsAdminOrRestaurant(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role in (UserRole.ADMIN, UserRole.RESTAURANT)
