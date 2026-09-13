"""
MecGuraServe - WhatsApp Integration Models
WhatsApp Business API integration for bill sending, payment reminders, marketing
"""

from django.db import models
from tenants.models import Tenant


class WhatsAppConfig(models.Model):
    """WhatsApp Business API configuration per tenant"""
    tenant = models.OneToOneField(Tenant, on_delete=models.CASCADE, related_name='whatsapp_config')
    
    # WhatsApp Business API credentials
    phone_number_id = models.CharField(max_length=100, blank=True)
    access_token = models.TextField(blank=True)
    business_account_id = models.CharField(max_length=100, blank=True)
    
    # Webhook verification
    verify_token = models.CharField(max_length=100, blank=True)
    
    # Settings
    is_active = models.BooleanField(default=False)
    auto_send_bill = models.BooleanField(default=True)
    auto_send_reminder = models.BooleanField(default=True)
    reminder_interval_hours = models.IntegerField(default=2)
    
    # Message templates
    bill_message = models.TextField(default="Hi {customer_name}! 🧾\n\nYour bill at {restaurant_name}:\n\n{bill_items}\n\nTotal: ₹{total}\n\nThank you for dining with us! 🙏\n\n- {restaurant_name}")
    payment_reminder = models.TextField(default="Hi {customer_name}! 💰\n\nFriendly reminder: Your bill of ₹{total} at {restaurant_name} is pending.\n\nPlease complete the payment at your convenience.\n\nThank you! 🙏")
    order_confirmation = models.TextField(default="Hi {customer_name}! ✅\n\nYour order #{order_id} has been received!\n\nItems:\n{order_items}\n\nEstimated time: {prep_time} mins\n\nWe'll notify you when it's ready! 🍽️")
    order_ready = models.TextField(default="Hi {customer_name}! 🎉\n\nYour order #{order_id} is READY!\n\nPlease collect from the counter.\n\nEnjoy your meal! 😋")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"WhatsApp Config - {self.tenant.name}"


class WhatsAppMessage(models.Model):
    """Track all WhatsApp messages sent"""
    MESSAGE_TYPES = [
        ('bill', 'Bill'),
        ('payment_reminder', 'Payment Reminder'),
        ('order_confirmation', 'Order Confirmation'),
        ('order_ready', 'Order Ready'),
        ('marketing', 'Marketing'),
        ('custom', 'Custom'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('read', 'Read'),
        ('failed', 'Failed'),
    ]
    
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='whatsapp_messages')
    order = models.ForeignKey('orders.Order', on_delete=models.SET_NULL, null=True, blank=True, related_name='whatsapp_messages')
    
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES)
    phone_number = models.CharField(max_length=20)
    message_content = models.TextField()
    
    # WhatsApp API response
    message_id = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Tracking
    sent_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.message_type} to {self.phone_number} - {self.status}"


class WhatsAppCampaign(models.Model):
    """Marketing campaigns via WhatsApp"""
    CAMPAIGN_TYPES = [
        ('promo', 'Promotion'),
        ('event', 'Event'),
        ('feedback', 'Feedback'),
        ('loyalty', 'Loyalty'),
    ]
    
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='whatsapp_campaigns')
    
    name = models.CharField(max_length=200)
    campaign_type = models.CharField(max_length=20, choices=CAMPAIGN_TYPES)
    message = models.TextField()
    
    # Target audience
    send_to_all = models.BooleanField(default=False)
    send_to_inactive = models.BooleanField(default=False)
    send_to_vip = models.BooleanField(default=False)
    
    # Schedule
    scheduled_at = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    
    # Stats
    total_sent = models.IntegerField(default=0)
    total_delivered = models.IntegerField(default=0)
    total_read = models.IntegerField(default=0)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.tenant.name}"
