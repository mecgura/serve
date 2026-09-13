"""
MecGuraServe - Dashboard Views (Kitchen + Owner)
"""

import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Sum, Count, Q, Avg
from datetime import datetime, timedelta

from tenants.models import Tenant, RestaurantTable
from menu.models import MenuCategory, MenuItem
from orders.models import Order, OrderItem
from coupons.models import Coupon


@login_required
def kitchen_display(request):
    """Kitchen display - shows incoming orders"""
    tenant = getattr(request, 'tenant', None)
    if not tenant:
        return redirect('superadmin_dashboard')
    
    # Get active orders
    active_orders = Order.objects.filter(
        tenant=tenant,
        status__in=['pending', 'confirmed', 'preparing', 'ready']
    ).select_related('table', 'customer').prefetch_related('items__menu_item').order_by('created_at')
    
    # Get today's stats
    today = timezone.now().date()
    today_orders = Order.objects.filter(
        tenant=tenant,
        created_at__date=today
    )
    stats = {
        'total_orders': today_orders.count(),
        'total_revenue': today_orders.filter(payment_status='paid').aggregate(total=Sum('total'))['total'] or 0,
        'avg_prep_time': today_orders.filter(actual_time__isnull=False).aggregate(avg=Avg('actual_time'))['avg'] or 0,
    }
    
    context = {
        'tenant': tenant,
        'active_orders': active_orders,
        'stats': stats,
    }
    return render(request, 'dashboard/kitchen.html', context)


@login_required
def owner_dashboard(request):
    """Owner/Manager dashboard - full overview"""
    tenant = getattr(request, 'tenant', None)
    if not tenant:
        return redirect('superadmin_dashboard')
    
    # Date range
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
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
    
    # This month stats
    month_orders = Order.objects.filter(tenant=tenant, created_at__date__gte=month_ago)
    month_stats = {
        'total_orders': month_orders.count(),
        'total_revenue': month_orders.filter(payment_status='paid').aggregate(total=Sum('total'))['total'] or 0,
    }
    
    # Recent orders
    recent_orders = Order.objects.filter(
        tenant=tenant
    ).select_related('table', 'customer').order_by('-created_at')[:10]
    
    # Popular items
    popular_items = OrderItem.objects.filter(
        order__tenant=tenant,
        order__created_at__date__gte=week_ago
    ).values('menu_item__name').annotate(
        total_quantity=Sum('quantity')
    ).order_by('-total_quantity')[:5]
    
    context = {
        'tenant': tenant,
        'today_stats': today_stats,
        'week_stats': week_stats,
        'month_stats': month_stats,
        'recent_orders': recent_orders,
        'popular_items': popular_items,
    }
    return render(request, 'dashboard/owner.html', context)


@login_required
def menu_management(request):
    """Manage menu items"""
    tenant = getattr(request, 'tenant', None)
    if not tenant:
        return redirect('superadmin_dashboard')
    
    categories = MenuCategory.objects.filter(tenant=tenant).prefetch_related('items')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'add_category':
            name = request.POST.get('name')
            if name:
                category = MenuCategory.objects.create(tenant=tenant, name=name)
                # Handle category image
                if 'image' in request.FILES:
                    category.image = request.FILES['image']
                    category.save()
                return JsonResponse({'success': True})
        
        elif action == 'add_item':
            category_id = request.POST.get('category_id')
            name = request.POST.get('name')
            price = request.POST.get('price')
            description = request.POST.get('description', '')
            is_vegetarian = request.POST.get('is_vegetarian') in ['on', 'true', 'True', '1']
            is_bestseller = request.POST.get('is_bestseller') in ['on', 'true', 'True', '1']
            is_spicy = request.POST.get('is_spicy') in ['on', 'true', 'True', '1']
            is_new = request.POST.get('is_new') in ['on', 'true', 'True', '1']
            prep_time = request.POST.get('prep_time', 15)
            
            if category_id and name and price:
                category = MenuCategory.objects.get(id=category_id, tenant=tenant)
                item = MenuItem.objects.create(
                    tenant=tenant,
                    category=category,
                    name=name,
                    price=price,
                    description=description,
                    is_vegetarian=is_vegetarian,
                    is_bestseller=is_bestseller,
                    is_spicy=is_spicy,
                    is_new=is_new,
                    prep_time=prep_time,
                )
                # Handle item image
                if 'image' in request.FILES:
                    item.image = request.FILES['image']
                    item.save()
                return JsonResponse({'success': True})
        
        elif action == 'edit_item':
            item_id = request.POST.get('item_id')
            try:
                item = MenuItem.objects.get(id=item_id, tenant=tenant)
                item.name = request.POST.get('name', item.name)
                item.price = request.POST.get('price', item.price)
                item.description = request.POST.get('description', item.description)
                item.is_vegetarian = request.POST.get('is_vegetarian') in ['on', 'true', 'True', '1']
                item.is_bestseller = request.POST.get('is_bestseller') in ['on', 'true', 'True', '1']
                item.is_spicy = request.POST.get('is_spicy') in ['on', 'true', 'True', '1']
                item.is_new = request.POST.get('is_new') in ['on', 'true', 'True', '1']
                item.prep_time = request.POST.get('prep_time', item.prep_time)
                
                # Handle item image
                if 'image' in request.FILES:
                    item.image = request.FILES['image']
                item.save()
                return JsonResponse({'success': True})
            except MenuItem.DoesNotExist:
                return JsonResponse({'error': 'Item not found'}, status=404)
        
        elif action == 'delete_item':
            item_id = request.POST.get('item_id')
            try:
                item = MenuItem.objects.get(id=item_id, tenant=tenant)
                item.delete()
                return JsonResponse({'success': True})
            except MenuItem.DoesNotExist:
                return JsonResponse({'error': 'Item not found'}, status=404)
        
        elif action == 'toggle_item':
            item_id = request.POST.get('item_id')
            item = MenuItem.objects.get(id=item_id, tenant=tenant)
            item.is_available = not item.is_available
            item.save()
            return JsonResponse({'success': True, 'is_available': item.is_available})
    
    context = {
        'tenant': tenant,
        'categories': categories,
    }
    return render(request, 'dashboard/menu.html', context)


@login_required
def order_management(request):
    """Manage all orders"""
    tenant = getattr(request, 'tenant', None)
    if not tenant:
        return redirect('superadmin_dashboard')
    
    status_filter = request.GET.get('status', 'all')
    
    orders = Order.objects.filter(tenant=tenant).select_related('table', 'customer')
    
    if status_filter != 'all':
        orders = orders.filter(status=status_filter)
    
    orders = orders.order_by('-created_at')[:50]
    
    context = {
        'tenant': tenant,
        'orders': orders,
        'status_filter': status_filter,
    }
    return render(request, 'dashboard/orders.html', context)


@csrf_exempt
@require_POST
def update_order_status(request):
    """Update order status via AJAX"""
    data = json.loads(request.body)
    order_id = data.get('order_id')
    new_status = data.get('status')
    
    try:
        order = Order.objects.get(id=order_id, tenant=request.tenant)
        old_status = order.status
        order.status = new_status
        
        # Set timestamp for status
        if new_status == 'confirmed':
            order.confirmed_at = timezone.now()
        elif new_status == 'preparing':
            order.preparing_at = timezone.now()
        elif new_status == 'ready':
            order.ready_at = timezone.now()
        elif new_status == 'served':
            order.served_at = timezone.now()
        elif new_status == 'completed':
            order.completed_at = timezone.now()
            # Calculate actual time
            if order.confirmed_at:
                order.actual_time = int((timezone.now() - order.confirmed_at).total_seconds() / 60)
        
        order.save()
        
        # Notify via WebSocket
        try:
            from dashboard.consumers import notify_status_update
            notify_status_update(order.tenant.slug, order)
        except Exception as e:
            print(f"WebSocket notification failed: {e}")
        
        return JsonResponse({'success': True, 'new_status': new_status})
    
    except Order.DoesNotExist:
        return JsonResponse({'error': 'Order not found'}, status=404)


@csrf_exempt
@require_POST
def mark_payment_paid(request):
    """Mark cash/counter payment as paid"""
    data = json.loads(request.body)
    order_id = data.get('order_id')
    
    try:
        order = Order.objects.get(id=order_id, tenant=request.tenant)
        order.payment_status = 'paid'
        order.save()
        
        # Send WhatsApp bill
        try:
            from whatsapp_integration.utils import send_bill
            send_bill(order)
        except Exception as e:
            print(f"WhatsApp bill failed: {e}")
        
        return JsonResponse({'success': True})
    
    except Order.DoesNotExist:
        return JsonResponse({'error': 'Order not found'}, status=404)


@login_required
def waiter_dashboard(request):
    """Waiter dashboard - Table-wise orders with customer names"""
    tenant = getattr(request, 'tenant', None)
    if not tenant:
        return redirect('superadmin_dashboard')
    
    # Get all tables with their current orders
    tables = RestaurantTable.objects.filter(tenant=tenant, is_active=True)
    
    table_data = []
    for table in tables:
        # Get latest active order for this table
        current_order = Order.objects.filter(
            tenant=tenant,
            table=table,
            status__in=['pending', 'confirmed', 'preparing', 'ready', 'served']
        ).select_related('customer').prefetch_related('items__menu_item').order_by('-created_at').first()
        
        table_data.append({
            'table': table,
            'order': current_order,
            'customer_name': current_order.customer.name if current_order and current_order.customer else 'Guest',
            'customer_phone': current_order.customer.phone if current_order and current_order.customer else '',
            'items': current_order.items.all() if current_order else [],
            'status': current_order.status if current_order else 'empty',
            'total': current_order.total if current_order else 0,
            'payment_status': current_order.payment_status if current_order else '',
            'payment_method': current_order.payment_method if current_order else '',
            'time_since': current_order.time_since_order if current_order else 0,
        })
    
    # Get today's summary
    today = timezone.now().date()
    today_orders = Order.objects.filter(tenant=tenant, created_at__date=today)
    summary = {
        'total_orders': today_orders.count(),
        'active_orders': today_orders.filter(status__in=['pending', 'confirmed', 'preparing', 'ready']).count(),
        'total_revenue': today_orders.filter(payment_status='paid').aggregate(total=Sum('total'))['total'] or 0,
    }
    
    context = {
        'tenant': tenant,
        'table_data': table_data,
        'summary': summary,
    }
    return render(request, 'dashboard/waiter.html', context)
