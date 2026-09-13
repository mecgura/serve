from django.urls import path
from . import views

urlpatterns = [
    path('settings/', views.whatsapp_settings, name='whatsapp_settings'),
    path('send-bill/<int:order_id>/', views.send_bill_whatsapp, name='send_bill_whatsapp'),
    path('send-reminder/<int:order_id>/', views.send_payment_reminder, name='send_payment_reminder'),
    path('history/', views.message_history, name='whatsapp_history'),
    path('campaigns/create/', views.create_campaign, name='create_campaign'),
    path('campaigns/', views.campaign_list, name='campaign_list'),
]
