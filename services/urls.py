"""
MecGuraServe - Service URLs
"""

from django.urls import path
from . import views

urlpatterns = [
    path('', views.service_catalog, name='service_catalog'),
    path('<slug:slug>/', views.service_detail, name='service_detail'),
    path('<slug:slug>/activate/', views.activate_service, name='activate_service'),
    path('<slug:slug>/deactivate/', views.deactivate_service, name='deactivate_service'),
    path('<slug:slug>/settings/', views.service_settings, name='service_settings'),
    path('<slug:slug>/manual/', views.service_manual, name='service_manual'),
]
