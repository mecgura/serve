"""
MecGuraServe - QR Generator URLs
"""

from django.urls import path
from qr_generator import views

urlpatterns = [
    path('table/<int:table_id>/', views.get_table_qr, name='get_table_qr'),
    path('download/<str:tenant_slug>/', views.download_all_qr, name='download_all_qr'),
]
