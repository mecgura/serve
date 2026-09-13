from django.contrib import admin
from .models import MenuCategory, MenuItem, MenuCustomization


@admin.register(MenuCategory)
class MenuCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'tenant', 'sort_order', 'is_active')
    list_filter = ('tenant', 'is_active')
    search_fields = ('name',)


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'tenant', 'category', 'price', 'is_available', 'is_vegetarian', 'is_bestseller')
    list_filter = ('tenant', 'category', 'is_available', 'is_vegetarian', 'is_bestseller', 'is_spicy')
    search_fields = ('name', 'description')
    list_editable = ('price', 'is_available', 'is_vegetarian', 'is_bestseller')


@admin.register(MenuCustomization)
class MenuCustomizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'item', 'price_modifier', 'is_required')
    list_filter = ('item__tenant',)
