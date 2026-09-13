"""
MecGuraServe - Order Models
"""

import uuid
from django.db import models
from django.utils import timezone


class Customer(models.Model):
    """Customer information"""
    
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='customers')
    name = models.CharField(max_length=100, blank=True, default='')
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True, default='')
    
    # Stats
    total_orders = models.PositiveIntegerField(default=0)
    total_spent = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Meta
    created_at = models.DateTimeField(auto_now_add=True)
    last_order_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = "Customer"
        verbose_name_plural = "Customers"
        unique_together = ['tenant', 'phone']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name or 'Guest'} ({self.phone}) - {self.tenant.name}"


class Order(models.Model):
    """Customer Order"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('preparing', 'Preparing'),
        ('ready', 'Ready'),
        ('served', 'Served'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('razorpay', 'Online Payment'),
        ('cash_counter', 'Cash at Counter'),
        ('card_counter', 'Card at Counter'),
        ('upi_counter', 'UPI at Counter'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]

    # Order Info
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='orders')
    order_number = models.CharField(max_length=20, unique=True)
    table = models.ForeignKey('tenants.RestaurantTable', on_delete=models.SET_NULL, null=True, related_name='orders')
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Pricing
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2)
    service_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Payment
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='razorpay')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    razorpay_order_id = models.CharField(max_length=100, blank=True, default='')
    razorpay_payment_id = models.CharField(max_length=100, blank=True, default='')
    
    # Coupon
    coupon = models.ForeignKey('coupons.Coupon', on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    coupon_code = models.CharField(max_length=50, blank=True, default='')
    
    # Notes
    special_instructions = models.TextField(blank=True, default='')
    
    # Timing
    estimated_time = models.IntegerField(default=20, help_text="Estimated time in minutes")
    actual_time = models.IntegerField(blank=True, null=True, help_text="Actual time in minutes")
    
    # Meta
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    confirmed_at = models.DateTimeField(blank=True, null=True)
    preparing_at = models.DateTimeField(blank=True, null=True)
    ready_at = models.DateTimeField(blank=True, null=True)
    served_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.order_number} - {self.tenant.name} - ₹{self.total}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = f"ORD-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    @property
    def time_since_order(self):
        """Returns minutes since order was placed"""
        delta = timezone.now() - self.created_at
        return int(delta.total_seconds() / 60)

    @property
    def status_color(self):
        """Returns color for dashboard display"""
        colors = {
            'pending': '#FFA500',
            'confirmed': '#2196F3',
            'preparing': '#9C27B0',
            'ready': '#4CAF50',
            'served': '#00BCD4',
            'completed': '#8BC34A',
            'cancelled': '#F44336',
        }
        return colors.get(self.status, '#757575')


class OrderItem(models.Model):
    """Individual items in an order"""
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    menu_item = models.ForeignKey('menu.MenuItem', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    special_instructions = models.TextField(blank=True, default='')
    
    # Customizations (JSON for flexibility)
    customizations = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = "Order Item"
        verbose_name_plural = "Order Items"
        ordering = ['id']

    def __str__(self):
        return f"{self.quantity}x {self.menu_item.name} - ₹{self.total_price}"

    def save(self, *args, **kwargs):
        if not self.total_price:
            self.total_price = self.unit_price * self.quantity
        super().save(*args, **kwargs)


class OrderStatusLog(models.Model):
    """Track order status changes"""
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='status_logs')
    old_status = models.CharField(max_length=20)
    new_status = models.CharField(max_length=20)
    changed_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True)
    note = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Order Status Log"
        verbose_name_plural = "Order Status Logs"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.order.order_number}: {self.old_status} → {self.new_status}"
