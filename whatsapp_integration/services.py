"""
MecGuraServe - WhatsApp Integration Service
Handles sending WhatsApp messages via Business API
"""

import requests
import json
from django.conf import settings
from django.utils import timezone
from .models import WhatsAppConfig, WhatsAppMessage


class WhatsAppService:
    """Service to handle WhatsApp Business API interactions"""
    
    BASE_URL = "https://graph.facebook.com/v17.0"
    
    def __init__(self, tenant):
        self.tenant = tenant
        try:
            self.config = WhatsAppConfig.objects.get(tenant=tenant, is_active=True)
        except WhatsAppConfig.DoesNotExist:
            self.config = None
    
    def _get_headers(self):
        """Get API headers"""
        return {
            'Authorization': f'Bearer {self.config.access_token}',
            'Content-Type': 'application/json',
        }
    
    def send_message(self, phone_number, message_type, message, order=None):
        """Send a WhatsApp message"""
        if not self.config or not self.config.is_active:
            return {'success': False, 'error': 'WhatsApp not configured'}
        
        # Clean phone number
        phone_number = phone_number.replace('+', '').replace(' ', '').replace('-', '')
        if not phone_number.startswith('91'):
            phone_number = f"91{phone_number}"
        
        # Create message record
        msg = WhatsAppMessage.objects.create(
            tenant=self.tenant,
            order=order,
            message_type=message_type,
            phone_number=phone_number,
            message_content=message,
        )
        
        try:
            # WhatsApp API request
            url = f"{self.BASE_URL}/{self.config.phone_number_id}/messages"
            payload = {
                "messaging_product": "whatsapp",
                "to": phone_number,
                "type": "text",
                "text": {
                    "body": message
                }
            }
            
            response = requests.post(url, headers=self._get_headers(), json=payload)
            result = response.json()
            
            if response.status_code == 200 and 'messages' in result:
                msg.message_id = result['messages'][0]['id']
                msg.status = 'sent'
                msg.sent_at = timezone.now()
                msg.save()
                return {'success': True, 'message_id': msg.message_id}
            else:
                msg.status = 'failed'
                msg.error_message = str(result)
                msg.save()
                return {'success': False, 'error': result}
                
        except Exception as e:
            msg.status = 'failed'
            msg.error_message = str(e)
            msg.save()
            return {'success': False, 'error': str(e)}
    
    def send_order_confirmation(self, order):
        """Send order confirmation message"""
        if not self.config:
            return {'success': False, 'error': 'WhatsApp not configured'}
        
        # Get customer phone from order
        phone = order.customer_phone or (order.customer.phone if order.customer else None)
        if not phone:
            return {'success': False, 'error': 'No phone number'}
        
        # Format order items
        order_items = "\n".join([
            f"• {item.quantity}x {item.menu_item.name} - ₹{item.total_price}"
            for item in order.items.all()
        ])
        
        # Format message
        message = self.config.order_confirmation.format(
            customer_name=order.customer_name or "Guest",
            order_id=order.id,
            order_items=order_items,
            prep_time=self.tenant.estimated_prep_time or 20,
        )
        
        return self.send_message(phone, 'order_confirmation', message, order)
    
    def send_order_ready(self, order):
        """Send order ready notification"""
        if not self.config:
            return {'success': False, 'error': 'WhatsApp not configured'}
        
        phone = order.customer_phone or (order.customer.phone if order.customer else None)
        if not phone:
            return {'success': False, 'error': 'No phone number'}
        
        message = self.config.order_ready.format(
            customer_name=order.customer_name or "Guest",
            order_id=order.id,
        )
        
        return self.send_message(phone, 'order_ready', message, order)
    
    def send_bill(self, order):
        """Send bill via WhatsApp"""
        if not self.config:
            return {'success': False, 'error': 'WhatsApp not configured'}
        
        phone = order.customer_phone or (order.customer.phone if order.customer else None)
        if not phone:
            return {'success': False, 'error': 'No phone number'}
        
        # Format bill items
        bill_items = "\n".join([
            f"• {item.quantity}x {item.menu_item.name} - ₹{item.total_price}"
            for item in order.items.all()
        ])
        
        message = self.config.bill_message.format(
            customer_name=order.customer_name or "Guest",
            restaurant_name=self.tenant.name,
            bill_items=bill_items,
            total=order.grand_total,
        )
        
        return self.send_message(phone, 'bill', message, order)
    
    def send_payment_reminder(self, order):
        """Send payment reminder"""
        if not self.config or not self.config.auto_send_reminder:
            return {'success': False, 'error': 'WhatsApp not configured or reminders disabled'}
        
        phone = order.customer_phone or (order.customer.phone if order.customer else None)
        if not phone:
            return {'success': False, 'error': 'No phone number'}
        
        message = self.config.payment_reminder.format(
            customer_name=order.customer_name or "Guest",
            restaurant_name=self.tenant.name,
            total=order.grand_total,
        )
        
        return self.send_message(phone, 'payment_reminder', message, order)
    
    def send_marketing_message(self, phone_number, message):
        """Send marketing message"""
        if not self.config:
            return {'success': False, 'error': 'WhatsApp not configured'}
        
        return self.send_message(phone_number, 'marketing', message)
