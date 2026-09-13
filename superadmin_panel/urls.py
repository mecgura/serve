"""
MecGuraServe - Superadmin URLs
"""

from django.urls import path
from superadmin_panel import views

urlpatterns = [
    # Login/Logout
    path('superadmin/login/', views.superadmin_login, name='superadmin_login'),
    path('superadmin/logout/', views.superadmin_logout, name='superadmin_logout'),
    
    # Dashboard
    path('superadmin/', views.superadmin_dashboard, name='superadmin_dashboard'),
    
    # Tenant Management
    path('superadmin/tenants/', views.manage_tenants, name='manage_tenants'),
    path('superadmin/tenants/add/', views.add_tenant, name='add_tenant'),
    path('superadmin/tenants/<int:tenant_id>/edit/', views.edit_tenant, name='edit_tenant'),
    path('superadmin/tenants/<int:tenant_id>/toggle/', views.toggle_tenant, name='toggle_tenant'),
    path('superadmin/tenants/<int:tenant_id>/orders/', views.tenant_orders, name='tenant_orders'),
]
