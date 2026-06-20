from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError

from apps.users.models import RestaurantProfile
from apps.users.helpers.constants import UserRole


class RestaurantProfileService:

    @staticmethod
    def list_profiles(requesting_user):
        if requesting_user.role == UserRole.ADMIN:
            return RestaurantProfile.objects.all().select_related('user')
        return RestaurantProfile.objects.filter(user=requesting_user).select_related('user')

    @staticmethod
    def get_profile_by_user_id(user_id, requesting_user):
        """
        - RESTAURANT: returns the requesting user's restaurant profile (ignores user_id).
        - ADMIN: expects user_id of the user whose restaurant profile to fetch.
        """
        queryset = RestaurantProfile.objects.select_related('user')
        if requesting_user.role == UserRole.ADMIN:
            queryset = queryset.filter(user_id=user_id)
        else:
            queryset = queryset.filter(user=requesting_user)

        try:
            return queryset.get()
        except RestaurantProfile.DoesNotExist:
            raise NotFound(f'RestaurantProfile for user_id={user_id} not found.')

    @staticmethod
    def create_profile(user, validated_data):
        if user.role != UserRole.RESTAURANT:
            raise PermissionDenied('Only restaurant users can create a restaurant profile.')
        if hasattr(user, 'restaurant_profile'):
            raise ValidationError({'restaurant_name': ['A restaurant profile already exists for this user.']})
        return RestaurantProfile.objects.create(user=user, **validated_data)

    @staticmethod
    def get_profile(profile_id, requesting_user):
        queryset = RestaurantProfile.objects.select_related('user')
        if requesting_user.role != UserRole.ADMIN:
            queryset = queryset.filter(user=requesting_user)
        try:
            return queryset.get(pk=profile_id)
        except RestaurantProfile.DoesNotExist:
            raise NotFound(f'RestaurantProfile {profile_id} not found.')

    @staticmethod
    def update_profile(profile, validated_data, partial=False, requesting_user=None):
        if requesting_user and requesting_user.role != UserRole.ADMIN:
            RestaurantProfileService._ensure_owned_by_user(profile, requesting_user)
        for attr, value in validated_data.items():
            setattr(profile, attr, value)
        profile.save()
        return profile

    @staticmethod
    def delete_profile(profile, requesting_user=None):
        if requesting_user and requesting_user.role != UserRole.ADMIN:
            RestaurantProfileService._ensure_owned_by_user(profile, requesting_user)
        profile.delete()

    @staticmethod
    def _ensure_owned_by_user(profile, user):
        if profile.user_id != user.id:
            raise PermissionDenied('You can only manage your own restaurant profile.')
