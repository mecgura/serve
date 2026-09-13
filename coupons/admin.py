from django.contrib import admin
from .models import Coupon, HappyHour, Offer


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'tenant', 'discount_type', 'discount_value', 'is_active', 'used_count', 'valid_until')
    list_filter = ('tenant', 'is_active', 'discount_type')
    search_fields = ('code', 'description')


@admin.register(HappyHour)
class HappyHourAdmin(admin.ModelAdmin):
    list_display = ('name', 'tenant', 'start_time', 'end_time', 'discount_percent', 'is_active')
    list_filter = ('tenant', 'is_active')


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ('title', 'tenant', 'offer_type', 'is_active', 'valid_from', 'valid_until')
    list_filter = ('tenant', 'is_active', 'offer_type')
