from django.contrib import admin
from .models import (
    Tenant, RestaurantTable, Staff, TableReservation,
    AdvancePayment, ComplimentaryService, TableLayout
)


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'plan', 'is_active', 'created_at')
    list_filter = ('is_active', 'plan')
    search_fields = ('name', 'slug', 'email')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Basic Info', {
            'fields': ('slug', 'name', 'tagline', 'phone', 'email', 'address')
        }),
        ('Branding', {
            'fields': ('logo', 'favicon', 'background_image', 'banner_image', 'primary_color', 'secondary_color', 'welcome_message', 'footer_text')
        }),
        ('Settings', {
            'fields': ('tax_percent', 'service_charge_percent', 'min_order_amount', 'estimated_prep_time', 'reservation_advance')
        }),
        ('Payment', {
            'fields': ('razorpay_key_id', 'razorpay_key_secret')
        }),
        ('WhatsApp', {
            'fields': ('whatsapp_api_token', 'whatsapp_phone_number_id')
        }),
        ('Subscription', {
            'fields': ('plan', 'plan_expiry', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(RestaurantTable)
class RestaurantTableAdmin(admin.ModelAdmin):
    list_display = ('table_number', 'tenant', 'capacity', 'status', 'assigned_waiter', 'is_active')
    list_filter = ('tenant', 'status', 'is_active')
    search_fields = ('table_number',)
    list_editable = ('status',)


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ('user', 'tenant', 'role', 'phone', 'is_active')
    list_filter = ('tenant', 'role', 'is_active')


@admin.register(TableReservation)
class TableReservationAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'table', 'reservation_date', 'start_time', 'end_time', 'party_size', 'advance_status', 'status')
    list_filter = ('tenant', 'status', 'advance_status', 'reservation_date')
    search_fields = ('customer_name', 'customer_phone')
    readonly_fields = ('created_at', 'confirmed_at')


@admin.register(AdvancePayment)
class AdvancePaymentAdmin(admin.ModelAdmin):
    list_display = ('amount', 'payment_method', 'customer_name', 'reference_number', 'recorded_by', 'created_at')
    list_filter = ('tenant', 'payment_method')
    search_fields = ('customer_name', 'customer_phone', 'reference_number')


@admin.register(ComplimentaryService)
class ComplimentaryServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'tenant', 'value', 'min_order_amount', 'is_active', 'used_count')
    list_filter = ('tenant', 'is_active')
    search_fields = ('name',)


@admin.register(TableLayout)
class TableLayoutAdmin(admin.ModelAdmin):
    list_display = ('name', 'tenant', 'width', 'height')
    list_filter = ('tenant',)
