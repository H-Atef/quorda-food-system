from django.contrib import admin
from apps.restaurants.models import Category, MenuItem, Criteria


class MenuItemInline(admin.TabularInline):
    model = MenuItem
    extra = 0
    fields = ('name', 'prep_time', 'price', 'is_available')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'priority', 'restaurant', 'created_at')
    list_filter = ('priority', 'restaurant')
    search_fields = ('name', 'restaurant__restaurant_name')
    inlines = [MenuItemInline]
    readonly_fields = ('created_at',)


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'prep_time', 'price', 'is_available', 'created_at')
    list_filter = ('is_available', 'category__restaurant')
    search_fields = ('name', 'category__name', 'category__restaurant__restaurant_name')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Criteria)
class CriteriaAdmin(admin.ModelAdmin):
    list_display = ('restaurant', 'max_quantity', 'min_category_priority', 'created_at')
    search_fields = ('restaurant__restaurant_name',)
    readonly_fields = ('created_at', 'updated_at')
