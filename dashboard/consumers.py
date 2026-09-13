"""
MecGuraServe - WebSocket Consumers for Real-Time Updates
"""

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


class KitchenConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for kitchen display"""
    
    async def connect(self):
        self.tenant_slug = self.scope['url_route']['kwargs']['tenant_slug']
        self.group_name = f"kitchen_{self.tenant_slug}"
        
        # Join kitchen group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        # Leave kitchen group
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type', '')
        
        if message_type == 'update_status':
            # Handle status update from kitchen
            order_id = data.get('order_id')
            new_status = data.get('status')
            
            # Broadcast to group
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'order_status_update',
                    'order_id': order_id,
                    'status': new_status,
                }
            )
    
    async def new_order(self, event):
        """Send new order notification to kitchen"""
        await self.send(text_data=json.dumps({
            'type': 'new_order',
            'order': event['order'],
        }))
    
    async def order_status_update(self, event):
        """Send order status update"""
        await self.send(text_data=json.dumps({
            'type': 'status_update',
            'order_id': event['order_id'],
            'status': event['status'],
        }))


class CustomerOrderConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for customer order tracking"""
    
    async def connect(self):
        self.order_id = self.scope['url_route']['kwargs']['order_id']
        self.group_name = f"order_{self.order_id}"
        
        # Join order group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        # Leave order group
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
    
    async def order_update(self, event):
        """Send order status update to customer"""
        await self.send(text_data=json.dumps({
            'type': 'order_update',
            'status': event['status'],
            'estimated_time': event.get('estimated_time'),
        }))


# Helper functions to send notifications
def notify_kitchen(tenant_slug, order):
    """Notify kitchen about new order"""
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"kitchen_{tenant_slug}",
        {
            'type': 'new_order',
            'order': {
                'id': order.id,
                'order_number': order.order_number,
                'table_number': order.table.table_number if order.table else 'N/A',
                'customer_name': order.customer.name if order.customer else 'Guest',
                'items': [
                    {
                        'name': item.menu_item.name,
                        'quantity': item.quantity,
                        'instructions': item.special_instructions,
                    }
                    for item in order.items.all()
                ],
                'total': str(order.total),
                'created_at': order.created_at.strftime('%H:%M'),
                'estimated_time': order.estimated_time,
            }
        }
    )


def notify_status_update(tenant_slug, order):
    """Notify about order status update"""
    channel_layer = get_channel_layer()
    
    # Notify kitchen
    async_to_sync(channel_layer.group_send)(
        f"kitchen_{tenant_slug}",
        {
            'type': 'order_status_update',
            'order_id': order.id,
            'status': order.status,
        }
    )
    
    # Notify customer
    async_to_sync(channel_layer.group_send)(
        f"order_{order.id}",
        {
            'type': 'order_update',
            'status': order.status,
            'estimated_time': order.estimated_time,
        }
    )
