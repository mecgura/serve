"""
MecGuraServe - Customer URLs
"""

from django.urls import path
from orders import views
from dashboard import staff_views

urlpatterns = [
    # Main menu page (QR scan lands here)
    path('', views.customer_menu, name='customer_menu'),
    
    # Customer details
    path('details/', views.customer_details, name='customer_details'),
    
    # API endpoints
    path('api/apply-coupon/', views.apply_coupon, name='apply_coupon'),
    path('api/remove-coupon/', views.remove_coupon, name='remove_coupon'),
    path('api/place-order/', views.place_order, name='place_order'),
    
    # Order tracking
    path('tracking/<int:order_id>/', views.order_tracking, name='order_tracking'),
    path('thank-you/<int:order_id>/', views.order_thank_you, name='order_thank_you'),
    
    # Order complete with engagement
    path('order-complete/', staff_views.order_complete, name='order_complete'),
]
