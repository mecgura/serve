from django.contrib import admin
from .models import Customer, Order, OrderItem, OrderStatusLog


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'tenant', 'total_orders', 'total_spent')
    list_filter = ('tenant',)
    search_fields = ('name', 'phone')


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('total_price',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'tenant', 'table', 'customer', 'status', 'payment_status', 'total', 'created_at')
    list_filter = ('tenant', 'status', 'payment_status')
    search_fields = ('order_number', 'customer__name', 'customer__phone')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'menu_item', 'quantity', 'unit_price', 'total_price')
    list_filter = ('order__tenant',)


@admin.register(OrderStatusLog)
class OrderStatusLogAdmin(admin.ModelAdmin):
    list_display = ('order', 'old_status', 'new_status', 'created_at')
    list_filter = ('order__tenant',)
