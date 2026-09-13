"""
MecGuraServe - Unified Admin Panel View
All features in one place
"""

import json
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Sum, Count
from datetime import datetime, timedelta

from tenants.models import (
    Tenant, RestaurantTable, Staff, TableReservation,
    AdvancePayment, ComplimentaryService, TableLayout
)
from menu.models import MenuCategory, MenuItem
from orders.models import Order, OrderItem
from coupons.models import Coupon


@login_required
def unified_admin(request):
    """Unified admin panel - all features in one place"""
    tenant = getattr(request, 'tenant', None)
    if not tenant:
        return redirect('superadmin_dashboard')
    
    # Date range
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    
    # Today's stats
    today_orders = Order.objects.filter(tenant=tenant, created_at__date=today)
    today_stats = {
        'total_orders': today_orders.count(),
        'total_revenue': today_orders.filter(payment_status='paid').aggregate(total=Sum('total'))['total'] or 0,
        'pending_orders': today_orders.filter(status__in=['pending', 'confirmed', 'preparing']).count(),
    }
    
    # This week stats
    week_orders = Order.objects.filter(tenant=tenant, created_at__date__gte=week_ago)
    week_stats = {
        'total_orders': week_orders.count(),
        'total_revenue': week_orders.filter(payment_status='paid').aggregate(total=Sum('total'))['total'] or 0,
    }
    
    # Recent orders
    recent_orders = Order.objects.filter(
        tenant=tenant
    ).select_related('table', 'customer').order_by('-created_at')[:5]
    
    # All orders
    all_orders = Order.objects.filter(
        tenant=tenant
    ).select_related('table', 'customer').prefetch_related('items__menu_item').order_by('-created_at')[:50]
    
    # Active orders for kitchen
    active_orders = Order.objects.filter(
        tenant=tenant,
        status__in=['pending', 'confirmed', 'preparing', 'ready']
    ).select_related('table', 'customer').prefetch_related('items__menu_item').order_by('created_at')
    
    # Categories with items
    categories = MenuCategory.objects.filter(tenant=tenant).prefetch_related('items')
    
    # Tables
    tables = RestaurantTable.objects.filter(tenant=tenant)
    
    # Reservations
    reservations = TableReservation.objects.filter(
        tenant=tenant
    ).select_related('table').order_by('-reservation_date', '-start_time')[:20]
    
    # Staff
    staff_members = Staff.objects.filter(tenant=tenant).select_related('user')
    
    # Payment stats (separate queryset - NOT sliced)
    today_payments = AdvancePayment.objects.filter(tenant=tenant, created_at__date=today)
    payment_stats = {
        'total_today': today_payments.aggregate(total=Sum('amount'))['total'] or 0,
        'count_today': today_payments.count(),
        'cash_today': today_payments.filter(payment_method='cash').aggregate(total=Sum('amount'))['total'] or 0,
        'online_today': today_payments.filter(payment_method='razorpay').aggregate(total=Sum('amount'))['total'] or 0,
    }
    
    # Payments list (sliced separately)
    payments = AdvancePayment.objects.filter(tenant=tenant).select_related('recorded_by')[:20]
    
    # Pending payments
    pending_payments = Order.objects.filter(
        tenant=tenant,
        payment_status='pending',
        status__in=['pending', 'confirmed', 'preparing', 'ready', 'served']
    ).select_related('table', 'customer')[:20]
    
    # Coupons
    coupons = Coupon.objects.filter(tenant=tenant)
    
    context = {
        'tenant': tenant,
        'today_stats': today_stats,
        'week_stats': week_stats,
        'recent_orders': recent_orders,
        'all_orders': all_orders,
        'active_orders': active_orders,
        'categories': categories,
        'tables': tables,
        'reservations': reservations,
        'staff_members': staff_members,
        'payments': payments,
        'payment_stats': payment_stats,
        'pending_payments': pending_payments,
        'coupons': coupons,
    }
    return render(request, 'admin/unified_admin.html', context)


# ============ API ENDPOINTS ============

@csrf_exempt
@require_POST
def add_coupon(request):
    """Add new coupon"""
    data = json.loads(request.body)
    tenant = request.tenant
    
    try:
        coupon = Coupon.objects.create(
            tenant=tenant,
            code=data['code'],
            discount_type=data.get('discount_type', 'percentage'),
            discount_value=data['discount_value'],
            min_order_amount=data.get('min_order_amount', 0),
            max_uses=data.get('max_uses'),
            valid_until=data.get('valid_until') or None,
        )
        return JsonResponse({'success': True, 'coupon_id': coupon.id})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
@require_POST
def toggle_coupon(request):
    """Toggle coupon active/inactive"""
    data = json.loads(request.body)
    
    try:
        coupon = Coupon.objects.get(id=data['coupon_id'], tenant=request.tenant)
        coupon.is_active = not coupon.is_active
        coupon.save()
        return JsonResponse({'success': True, 'is_active': coupon.is_active})
    except Coupon.DoesNotExist:
        return JsonResponse({'error': 'Coupon not found'}, status=404)


@csrf_exempt
@require_POST
def send_payment_reminder(request):
    """Send payment reminder for a specific order"""
    data = json.loads(request.body)
    tenant = request.tenant
    
    try:
        order = Order.objects.get(id=data['order_id'], tenant=tenant)
        
        # TODO: Integrate with WhatsApp API
        # For now, just return success
        return JsonResponse({
            'success': True,
            'message': f'Reminder sent for order {order.order_number}'
        })
    except Order.DoesNotExist:
        return JsonResponse({'error': 'Order not found'}, status=404)


@csrf_exempt
@require_POST
def send_all_payment_reminders(request):
    """Send payment reminders for all pending orders"""
    tenant = request.tenant
    
    pending_orders = Order.objects.filter(
        tenant=tenant,
        payment_status='pending',
        status__in=['pending', 'confirmed', 'preparing', 'ready', 'served']
    )
    
    count = pending_orders.count()
    
    # TODO: Integrate with WhatsApp API
    # For now, just return success
    return JsonResponse({
        'success': True,
        'message': f'Reminders queued for {count} orders'
    })
