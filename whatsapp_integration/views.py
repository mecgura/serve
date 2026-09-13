"""
MecGuraServe - WhatsApp Integration Views
Views for managing WhatsApp settings, sending bills, and campaigns
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Count, Q

from tenants.models import Tenant
from orders.models import Order
from .models import WhatsAppConfig, WhatsAppMessage, WhatsAppCampaign
from .services import WhatsAppService


@login_required
def whatsapp_settings(request):
    """WhatsApp configuration settings"""
    tenant_slug = request.GET.get('tenant')
    tenant = get_object_or_404(Tenant, slug=tenant_slug)
    
    config, created = WhatsAppConfig.objects.get_or_create(tenant=tenant)
    
    if request.method == 'POST':
        config.phone_number_id = request.POST.get('phone_number_id', '')
        config.access_token = request.POST.get('access_token', '')
        config.business_account_id = request.POST.get('business_account_id', '')
        config.is_active = request.POST.get('is_active') == 'on'
        config.auto_send_bill = request.POST.get('auto_send_bill') == 'on'
        config.auto_send_reminder = request.POST.get('auto_send_reminder') == 'on'
        config.reminder_interval_hours = int(request.POST.get('reminder_interval_hours', 2))
        config.bill_message = request.POST.get('bill_message', config.bill_message)
        config.payment_reminder = request.POST.get('payment_reminder', config.payment_reminder)
        config.order_confirmation = request.POST.get('order_confirmation', config.order_confirmation)
        config.order_ready = request.POST.get('order_ready', config.order_ready)
        config.save()
        
        messages.success(request, 'WhatsApp settings saved successfully!')
        return redirect(f'/dashboard/whatsapp/?tenant={tenant_slug}')
    
    context = {
        'tenant': tenant,
        'config': config,
    }
    return render(request, 'dashboard/whatsapp_settings.html', context)


@login_required
def send_bill_whatsapp(request, order_id):
    """Send bill via WhatsApp"""
    tenant_slug = request.GET.get('tenant')
    tenant = get_object_or_404(Tenant, slug=tenant_slug)
    order = get_object_or_404(Order, id=order_id, tenant=tenant)
    
    whatsapp_service = WhatsAppService(tenant)
    result = whatsapp_service.send_bill(order)
    
    if result['success']:
        messages.success(request, 'Bill sent successfully via WhatsApp!')
    else:
        messages.error(request, f'Failed to send bill: {result.get("error", "Unknown error")}')
    
    return redirect(f'/dashboard/orders/?tenant={tenant_slug}')


@login_required
def send_payment_reminder(request, order_id):
    """Send payment reminder"""
    tenant_slug = request.GET.get('tenant')
    tenant = get_object_or_404(Tenant, slug=tenant_slug)
    order = get_object_or_404(Order, id=order_id, tenant=tenant)
    
    whatsapp_service = WhatsAppService(tenant)
    result = whatsapp_service.send_payment_reminder(order)
    
    if result['success']:
        messages.success(request, 'Payment reminder sent!')
    else:
        messages.error(request, f'Failed to send reminder: {result.get("error", "Unknown error")}')
    
    return redirect(f'/dashboard/orders/?tenant={tenant_slug}')


@login_required
def message_history(request):
    """View WhatsApp message history"""
    tenant_slug = request.GET.get('tenant')
    tenant = get_object_or_404(Tenant, slug=tenant_slug)
    
    messages_list = WhatsAppMessage.objects.filter(tenant=tenant).select_related('order')[:50]
    
    # Stats
    today = timezone.now().date()
    today_messages = WhatsAppMessage.objects.filter(
        tenant=tenant,
        created_at__date=today
    )
    
    stats = {
        'total_sent': today_messages.filter(status__in=['sent', 'delivered', 'read']).count(),
        'delivered': today_messages.filter(status='delivered').count(),
        'read': today_messages.filter(status='read').count(),
        'failed': today_messages.filter(status='failed').count(),
    }
    
    context = {
        'tenant': tenant,
        'messages': messages_list,
        'stats': stats,
    }
    return render(request, 'dashboard/whatsapp_history.html', context)


@login_required
def create_campaign(request):
    """Create WhatsApp marketing campaign"""
    tenant_slug = request.GET.get('tenant')
    tenant = get_object_or_404(Tenant, slug=tenant_slug)
    
    if request.method == 'POST':
        campaign = WhatsAppCampaign.objects.create(
            tenant=tenant,
            name=request.POST.get('name'),
            campaign_type=request.POST.get('campaign_type'),
            message=request.POST.get('message'),
            send_to_all=request.POST.get('send_to_all') == 'on',
            send_to_inactive=request.POST.get('send_to_inactive') == 'on',
            send_to_vip=request.POST.get('send_to_vip') == 'on',
        )
        
        messages.success(request, f'Campaign "{campaign.name}" created!')
        return redirect(f'/dashboard/whatsapp/campaigns/?tenant={tenant_slug}')
    
    context = {
        'tenant': tenant,
    }
    return render(request, 'dashboard/create_campaign.html', context)


@login_required
def campaign_list(request):
    """List all campaigns"""
    tenant_slug = request.GET.get('tenant')
    tenant = get_object_or_404(Tenant, slug=tenant_slug)
    
    campaigns = WhatsAppCampaign.objects.filter(tenant=tenant).order_by('-created_at')
    
    context = {
        'tenant': tenant,
        'campaigns': campaigns,
    }
    return render(request, 'dashboard/campaign_list.html', context)
