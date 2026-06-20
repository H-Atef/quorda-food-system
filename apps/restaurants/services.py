from rest_framework.exceptions import NotFound
from apps.restaurants.models import Category, MenuItem, Criteria, RestaurantCalculationParams
from apps.users.models.restaurant_profile import RestaurantProfile
import uuid


class CategoryService:

    @staticmethod
    def list_for_restaurant(restaurant_profile):
        return Category.objects.filter(restaurant=restaurant_profile)

    @staticmethod
    def get_by_id(category_id, restaurant_profile):
        if isinstance(category_id, str):
            category_id = uuid.UUID(category_id)
        try:
            return Category.objects.get(pk=category_id, restaurant=restaurant_profile)
        except Category.DoesNotExist:
            raise NotFound(f'Category {category_id} not found.')

    @staticmethod
    def create(restaurant_profile, validated_data):
        return Category.objects.create(restaurant=restaurant_profile, **validated_data)

    @staticmethod
    def update(category, validated_data, partial=False):
        for attr, value in validated_data.items():
            setattr(category, attr, value)
        category.save()
        return category

    @staticmethod
    def delete(category):
        category.delete()


class MenuItemService:

    @staticmethod
    def list_for_restaurant(restaurant_profile):
        return MenuItem.objects.filter(restaurant=restaurant_profile).select_related('category')

    @staticmethod
    def get_by_id(item_id, restaurant_profile):
        if isinstance(item_id, str):
            item_id = uuid.UUID(item_id)
        try:
            return MenuItem.objects.get(pk=item_id, restaurant=restaurant_profile)
        except MenuItem.DoesNotExist:
            raise NotFound(f'MenuItem {item_id} not found.')

    @staticmethod
    def create(restaurant_profile, validated_data):
        return MenuItem.objects.create(restaurant=restaurant_profile, **validated_data)

    @staticmethod
    def update(item, validated_data, partial=False):
        for attr, value in validated_data.items():
            setattr(item, attr, value)
        item.save()
        return item

    @staticmethod
    def delete(item):
        item.delete()


class CriteriaService:

    @staticmethod
    def get_or_none(restaurant_profile):
        return getattr(restaurant_profile, 'criteria', None)

    @staticmethod
    def create_or_update(restaurant_profile, validated_data):
        criteria, created = Criteria.objects.update_or_create(
            restaurant=restaurant_profile,
            defaults=validated_data,
        )
        return criteria, created


class CalculationParamsService:

    @staticmethod
    def list_for_restaurant(restaurant_profile):
        return RestaurantCalculationParams.objects.filter(restaurant=restaurant_profile)

    @staticmethod
    def get_by_id(params_id, restaurant_profile):
        if isinstance(params_id, str):
            params_id = uuid.UUID(params_id)
        try:
            return RestaurantCalculationParams.objects.get(pk=params_id, restaurant=restaurant_profile)
        except RestaurantCalculationParams.DoesNotExist:
            raise NotFound(f'CalculationParams {params_id} not found.')

    @staticmethod
    def create(restaurant_profile, validated_data):
        return RestaurantCalculationParams.objects.create(restaurant=restaurant_profile, **validated_data)

    @staticmethod
    def update(params_obj, validated_data, partial=False):
        for attr, value in validated_data.items():
            setattr(params_obj, attr, value)
        params_obj.save()
        return params_obj

    @staticmethod
    def delete(params_obj):
        params_obj.delete()
        




class PublicRestaurantsService:
    @staticmethod
    def list_active_restaurants():
        return RestaurantProfile.objects.filter(is_active=True)

    @staticmethod
    def get_active_restaurant(restaurant_id):
        try:
            return RestaurantProfile.objects.get(pk=restaurant_id, is_active=True)
        except RestaurantProfile.DoesNotExist:
            raise NotFound('Restaurant not found.')

    @staticmethod
    def list_menu_items(restaurant_id):
        restaurant = PublicRestaurantsService.get_active_restaurant(restaurant_id)
        # MenuItemService expects a RestaurantProfile instance
        return MenuItemService.list_for_restaurant(restaurant)

