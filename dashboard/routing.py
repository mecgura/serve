"""
MecGuraServe - WebSocket Routing
"""

from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/kitchen/(?P<tenant_slug>\w+)/$', consumers.KitchenConsumer.as_asgi()),
    re_path(r'ws/order/(?P<order_id>\d+)/$', consumers.CustomerOrderConsumer.as_asgi()),
]
