"""
MecGuraServe - Main URL Configuration
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Landing Page
    path('', TemplateView.as_view(template_name='landing/home.html'), name='landing'),
    
    # Superadmin Panel (manage all tenants)
    path('', include('superadmin_panel.urls')),
    
    # Customer Flow (QR scan → Menu → Order)
    path('menu/', include('orders.urls_customer')),
    
    # Dashboard (Kitchen + Owner + Staff)
    path('dashboard/', include('dashboard.urls')),
    
    # Payment
    path('payment/', include('payments.urls')),
    
    # QR Code
    path('qr/', include('qr_generator.urls')),
    
    # Services (Add-on features)
    path('services/', include('services.urls')),
    
    # Onboarding (New resort setup)
    path('onboarding/', include('onboarding.urls')),
    
    # WhatsApp Integration
    path('dashboard/whatsapp/', include('whatsapp_integration.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
