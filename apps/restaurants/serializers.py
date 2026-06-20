from rest_framework import serializers
from apps.restaurants.models import Category, MenuItem, Criteria, RestaurantCalculationParams
from apps.users.models import RestaurantProfile
import uuid


class PublicRestaurantProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = RestaurantProfile
        fields = ('id', 'restaurant_name', 'address', 'description', 'logo_url', 'is_active', 'created_at')


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'restaurant', 'name', 'priority', 'created_at')
        read_only_fields = ('id', 'restaurant', 'created_at')

    def validate_priority(self, value):
        if not (1 <= value <= 5):
            raise serializers.ValidationError('Priority must be between 1 and 5.')
        return value


class MenuItemSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_priority = serializers.IntegerField(source='category.priority', read_only=True)

    class Meta:
        model = MenuItem
        fields = (
            'id', 'restaurant', 'category', 'category_name', 'category_priority',
            'name', 'prep_time', 'price', 'is_available',
            'created_at', 'updated_at',
        )
        read_only_fields = ('id', 'category_name', 'category_priority', 'created_at', 'updated_at')

    def validate_category(self, category):
        if category is None:
            return None
        request = self.context.get('request')
        if request and hasattr(request.user, 'restaurant_profile'):
            if category.restaurant_id != request.user.restaurant_profile.id:
                raise serializers.ValidationError(
                    'This category does not belong to your restaurant.'
                )
        return category

    def validate(self, data):
        request = self.context.get('request')
        if request and hasattr(request.user, 'restaurant_profile'):
            if 'restaurant' not in data or data['restaurant'] is None:
                data['restaurant'] = request.user.restaurant_profile
        return data


class CriteriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Criteria
        fields = ('id', 'restaurant', 'max_quantity', 'min_category_priority', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')

    def validate_min_category_priority(self, value):
        if not (1 <= value <= 5):
            raise serializers.ValidationError('min_category_priority must be between 1 and 5.')
        return value

    def validate(self, data):
        request = self.context.get('request')
        if request and hasattr(request.user, 'restaurant_profile'):
            if 'restaurant' not in data or data['restaurant'] is None:
                data['restaurant'] = request.user.restaurant_profile
        return data


class CalculationParamsSerializer(serializers.ModelSerializer):
    class Meta:
        model = RestaurantCalculationParams
        fields = ('id', 'restaurant', 'time_weight', 'quantity_weight', 'category_weight', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')

    def validate(self, data):
        request = self.context.get('request')
        if request and hasattr(request.user, 'restaurant_profile'):
            if 'restaurant' not in data or data['restaurant'] is None:
                data['restaurant'] = request.user.restaurant_profile
        return data
