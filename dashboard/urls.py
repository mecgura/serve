"""
MecGuraServe - Dashboard URLs
"""

from django.urls import path
from dashboard import views
from dashboard import admin_views
from dashboard import unified_views
from dashboard import staff_views

urlpatterns = [
    # Unified Admin Panel (ALL-IN-ONE)
    path('admin/', unified_views.unified_admin, name='unified_admin'),
    
    # Staff Login & Panel
    path('staff-login/', staff_views.staff_login_page, name='staff_login_page'),
    path('staff-login/api/', staff_views.staff_login, name='staff_login'),
    path('staff-logout/', staff_views.staff_logout, name='staff_logout'),
    path('staff-panel/', staff_views.staff_panel, name='staff_panel'),
    
    # Kitchen Display
    path('kitchen/', views.kitchen_display, name='kitchen_display'),
    path('kitchen-staff/', views.kitchen_display, name='kitchen_staff'),
    
    # Waiter Dashboard
    path('waiter/', views.waiter_dashboard, name='waiter_dashboard'),
    
    # Owner Dashboard
    path('', views.owner_dashboard, name='owner_dashboard'),
    
    # Menu Management
    path('menu/', views.menu_management, name='menu_management'),
    
    # Order Management
    path('orders/', views.order_management, name='order_management'),
    
    # Admin - Table Management
    path('tables/', admin_views.table_management, name='table_management'),
    path('reservations/', admin_views.reservation_management, name='reservation_management'),
    path('advance-payments/', admin_views.advance_payments, name='advance_payments'),
    path('complimentary/', admin_views.complimentary_services, name='complimentary_services'),
    
    # Staff Management
    path('staff/', admin_views.staff_management, name='staff_management'),
    
    # QR Download
    path('qr/<int:table_id>/', admin_views.download_table_qr, name='download_table_qr'),
    path('qr/download-all/', admin_views.download_all_qr_zip, name='download_all_qr'),
    
    # API endpoints
    path('api/update-status/', views.update_order_status, name='update_order_status'),
    path('api/mark-paid/', views.mark_payment_paid, name='mark_payment_paid'),
    path('api/add-table/', admin_views.add_table, name='add_table'),
    path('api/update-table-position/', admin_views.update_table_position, name='update_table_position'),
    path('api/assign-waiter/', admin_views.assign_waiter, name='assign_waiter'),
    path('api/update-table-status/', admin_views.update_table_status, name='update_table_status'),
    path('api/add-reservation/', admin_views.add_reservation, name='add_reservation'),
    path('api/cancel-reservation/', admin_views.cancel_reservation, name='cancel_reservation'),
    path('api/add-advance-payment/', admin_views.add_advance_payment, name='add_advance_payment'),
    path('api/add-complimentary/', admin_views.add_complimentary_service, name='add_complimentary'),
    path('api/toggle-complimentary/', admin_views.toggle_complimentary, name='toggle_complimentary'),
    path('api/add-staff/', admin_views.add_staff, name='add_staff'),
    path('api/toggle-staff/', admin_views.toggle_staff, name='toggle_staff'),
    path('api/remove-staff/', admin_views.remove_staff, name='remove_staff'),
    path('api/update-staff/', admin_views.update_staff, name='update_staff'),
    path('api/add-coupon/', unified_views.add_coupon, name='add_coupon'),
    path('api/toggle-coupon/', unified_views.toggle_coupon, name='toggle_coupon'),
    path('api/send-reminder/', unified_views.send_payment_reminder, name='send_reminder'),
    path('api/send-all-reminders/', unified_views.send_all_payment_reminders, name='send_all_reminders'),
]
