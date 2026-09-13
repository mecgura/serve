"""
MecGuraServe - Coupons & Offers Models
"""

from django.db import models
from django.utils import timezone


class Coupon(models.Model):
    """Discount Coupons"""
    
    DISCOUNT_TYPE_CHOICES = [
        ('percentage', 'Percentage Off'),
        ('fixed', 'Fixed Amount Off'),
        ('free_item', 'Free Item'),
    ]

    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='coupons')
    code = models.CharField(max_length=50)
    description = models.TextField(blank=True, default='')
    
    # Discount Details
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPE_CHOICES)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    max_discount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    min_order_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Validity
    valid_from = models.DateTimeField(default=timezone.now)
    valid_until = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    # Usage Limits
    max_uses = models.PositiveIntegerField(blank=True, null=True, help_text="Total times can be used (null = unlimited)")
    used_count = models.PositiveIntegerField(default=0)
    max_per_customer = models.PositiveIntegerField(default=1)
    
    # Applicable items (NULL = all items)
    applicable_categories = models.JSONField(blank=True, null=True, help_text="List of category IDs or NULL for all")
    applicable_items = models.JSONField(blank=True, null=True, help_text="List of item IDs or NULL for all")
    
    # Meta
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Coupon"
        verbose_name_plural = "Coupons"
        unique_together = ['tenant', 'code']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.code} - {self.get_discount_display()} ({self.tenant.name})"

    @property
    def is_valid(self):
        """Check if coupon is currently valid"""
        now = timezone.now()
        if not self.is_active:
            return False
        if self.valid_from and now < self.valid_from:
            return False
        if self.valid_until and now > self.valid_until:
            return False
        if self.max_uses and self.used_count >= self.max_uses:
            return False
        return True

    @property
    def get_discount_display(self):
        if self.discount_type == 'percentage':
            return f"{self.discount_value}% Off"
        elif self.discount_type == 'fixed':
            return f"₹{self.discount_value} Off"
        return "Free Item"

    def calculate_discount(self, subtotal):
        """Calculate discount amount for given subtotal"""
        if not self.is_valid:
            return 0
        
        if subtotal < self.min_order_amount:
            return 0
        
        if self.discount_type == 'percentage':
            discount = (subtotal * self.discount_value) / 100
            if self.max_discount:
                discount = min(discount, self.max_discount)
            return discount
        elif self.discount_type == 'fixed':
            return min(self.discount_value, subtotal)
        
        return 0


class HappyHour(models.Model):
    """Time-based discounts"""
    
    DAY_CHOICES = [
        (0, 'Sunday'),
        (1, 'Monday'),
        (2, 'Tuesday'),
        (3, 'Wednesday'),
        (4, 'Thursday'),
        (5, 'Friday'),
        (6, 'Saturday'),
    ]

    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='happy_hours')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, default='')
    
    # Schedule
    days_of_week = models.JSONField(default=list, help_text="List of day numbers (0=Sunday)")
    start_time = models.TimeField()
    end_time = models.TimeField()
    
    # Discount
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2)
    applicable_categories = models.JSONField(blank=True, null=True)
    
    # Meta
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Happy Hour"
        verbose_name_plural = "Happy Hours"
        ordering = ['start_time']

    def __str__(self):
        return f"{self.name} ({self.discount_percent}% off) - {self.tenant.name}"

    @property
    def is_active_now(self):
        """Check if happy hour is active right now"""
        if not self.is_active:
            return False
        
        now = timezone.localtime(timezone.now())
        current_day = now.weekday()
        current_time = now.time()
        
        if current_day not in self.days_of_week:
            return False
        
        if self.start_time <= self.end_time:
            return self.start_time <= current_time <= self.end_time
        else:
            # Overnight happy hour (e.g., 10 PM to 2 AM)
            return current_time >= self.start_time or current_time <= self.end_time


class Offer(models.Model):
    """Special Offers / Promotions"""
    
    OFFER_TYPE_CHOICES = [
        ('banner', 'Banner Offer'),
        ('item', 'Item Special'),
        ('combo', 'Combo Deal'),
        ('festival', 'Festival Offer'),
    ]

    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='offers')
    title = models.CharField(max_length=200)
    description = models.TextField()
    offer_type = models.CharField(max_length=20, choices=OFFER_TYPE_CHOICES)
    
    # Discount
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    # Image
    image = models.ImageField(upload_to='offers/', blank=True, null=True)
    
    # Validity
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    
    # Items in combo (if offer_type is 'combo')
    combo_items = models.JSONField(blank=True, null=True, help_text="List of item IDs")
    combo_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    # Meta
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Offer"
        verbose_name_plural = "Offers"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.tenant.name}"

    @property
    def is_valid(self):
        now = timezone.now()
        return self.is_active and self.valid_from <= now <= self.valid_until
