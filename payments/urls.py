"""
MecGuraServe - Payment URLs
"""

from django.urls import path
from payments import views

urlpatterns = [
    path('create-order/', views.create_order, name='create_razorpay_order'),
    path('verify/', views.verify_payment_view, name='verify_payment'),
    path('success/<int:order_id>/', views.payment_success, name='payment_success'),
    path('failed/<int:order_id>/', views.payment_failed, name='payment_failed'),
]
