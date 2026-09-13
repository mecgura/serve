"""
MecGuraServe - Services Model
Add-on features that resorts can activate/deactivate
"""

from django.db import models
from django.utils.text import slugify
import json


class ServiceCategory(models.Model):
    """Service categories"""
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, default='fas fa-cog')
    description = models.TextField(blank=True)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name


class Service(models.Model):
    """Individual service/feature"""
    
    PRICE_TYPE_CHOICES = [
        ('free', 'Free'),
        ('one_time', 'One-Time'),
        ('monthly', 'Monthly'),
        ('per_order', 'Per Order'),
    ]
    
    category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=100)
    short_description = models.CharField(max_length=300)
    full_description = models.TextField()
    icon = models.CharField(max_length=50, default='fas fa-star')
    
    # Pricing
    price_type = models.CharField(max_length=20, choices=PRICE_TYPE_CHOICES, default='free')
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    original_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Original price for showing discount")
    
    # Features included
    features = models.JSONField(default=list, help_text='JSON list of features')
    
    # Manual/Guide
    manual_title = models.CharField(max_length=200, blank=True)
    manual_content = models.TextField(blank=True, help_text='How to use this service')
    setup_guide_url = models.URLField(blank=True, help_text='Video tutorial URL')
    
    # Settings
    is_active = models.BooleanField(default=True)
    is_popular = models.BooleanField(default=False)
    is_beta = models.BooleanField(default=False)
    order = models.IntegerField(default=0)
    
    # Technical
    requires_whatsapp = models.BooleanField(default=False)
    requires_razorpay = models.BooleanField(default=False)
    requires_staff = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['category', 'order', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.get_price_display()})"
    
    def get_price_display(self):
        if self.price_type == 'free':
            return 'FREE'
        elif self.price_type == 'monthly':
            return f'₹{self.price}/mo'
        elif self.price_type == 'one_time':
            return f'₹{self.price}'
        elif self.price_type == 'per_order':
            return f'₹{self.price}/order'
        return str(self.price)


class TenantService(models.Model):
    """Services activated for a tenant"""
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('pending', 'Pending Setup'),
        ('expired', 'Expired'),
    ]
    
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='tenant_services')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='tenant_services')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Activation details
    activated_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(blank=True, null=True)
    
    # Usage tracking
    usage_count = models.IntegerField(default=0)
    last_used = models.DateTimeField(blank=True, null=True)
    
    # Settings (JSON - service specific config)
    settings = models.JSONField(default=dict)
    
    # Notes
    notes = models.TextField(blank=True)
    
    class Meta:
        unique_together = ('tenant', 'service')
        ordering = ['-activated_at']
    
    def __str__(self):
        return f"{self.tenant.name} - {self.service.name} ({self.status})"
    
    def is_available(self):
        if self.status != 'active':
            return False
        if self.expires_at and self.expires_at < models.functions.Now():
            return False
        return True


class ServiceUsageLog(models.Model):
    """Track service usage"""
    tenant_service = models.ForeignKey(TenantService, on_delete=models.CASCADE, related_name='usage_logs')
    action = models.CharField(max_length=100)
    details = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.tenant_service} - {self.action}"
