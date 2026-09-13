"""
MecGuraServe - Service Management Views
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from services.models import Service, ServiceCategory, TenantService


@login_required
def service_catalog(request):
    """Browse all available services"""
    tenant = getattr(request, 'tenant', None)
    categories = ServiceCategory.objects.filter(is_active=True)
    services = Service.objects.filter(is_active=True)
    
    # Get activated services
    activated_ids = TenantService.objects.filter(
        tenant=tenant, 
        status='active'
    ).values_list('service_id', flat=True)
    
    context = {
        'categories': categories,
        'services': services,
        'activated_ids': list(activated_ids),
        'tenant': tenant,
    }
    return render(request, 'services/catalog.html', context)


@login_required
def service_detail(request, slug):
    """Service detail with manual"""
    service = get_object_or_404(Service, slug=slug)
    tenant = getattr(request, 'tenant', None)
    
    tenant_service = TenantService.objects.filter(
        tenant=tenant, 
        service=service
    ).first()
    
    context = {
        'service': service,
        'tenant_service': tenant_service,
        'is_active': tenant_service.status == 'active' if tenant_service else False,
    }
    return render(request, 'services/detail.html', context)


@login_required
def activate_service(request, slug):
    """Activate a service"""
    if request.method != 'POST':
        return redirect('service_catalog')
    
    service = get_object_or_404(Service, slug=slug)
    tenant = getattr(request, 'tenant', None)
    
    tenant_service, created = TenantService.objects.get_or_create(
        tenant=tenant,
        service=service,
        defaults={'status': 'active'}
    )
    
    if not created:
        tenant_service.status = 'active'
        tenant_service.save()
    
    messages.success(request, f'{service.name} activated successfully!')
    return redirect('service_catalog')


@login_required
def deactivate_service(request, slug):
    """Deactivate a service"""
    if request.method != 'POST':
        return redirect('service_catalog')
    
    service = get_object_or_404(Service, slug=slug)
    tenant = getattr(request, 'tenant', None)
    
    tenant_service = TenantService.objects.filter(
        tenant=tenant, 
        service=service
    ).first()
    
    if tenant_service:
        tenant_service.status = 'inactive'
        tenant_service.save()
        messages.success(request, f'{service.name} deactivated.')
    
    return redirect('service_catalog')


@login_required
def service_settings(request, slug):
    """Service-specific settings"""
    service = get_object_or_404(Service, slug=slug)
    tenant = getattr(request, 'tenant', None)
    
    tenant_service = TenantService.objects.filter(
        tenant=tenant, 
        service=service
    ).first()
    
    if not tenant_service:
        messages.warning(request, 'Please activate the service first.')
        return redirect('service_catalog')
    
    if request.method == 'POST':
        # Save service-specific settings
        settings = {}
        for key, value in request.POST.items():
            if key.startswith('setting_'):
                settings[key.replace('setting_', '')] = value
        
        tenant_service.settings = settings
        tenant_service.save()
        messages.success(request, 'Settings saved!')
        return redirect('service_settings', slug=slug)
    
    context = {
        'service': service,
        'tenant_service': tenant_service,
    }
    return render(request, 'services/settings.html', context)


@login_required
def service_manual(request, slug):
    """View service manual"""
    service = get_object_or_404(Service, slug=slug)
    
    context = {
        'service': service,
    }
    return render(request, 'services/manual.html', context)
