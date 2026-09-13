"""
MecGuraServe - Superadmin Panel (Manage All Resorts)
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum, Count
from datetime import datetime, timedelta

from tenants.models import Tenant, RestaurantTable, Staff
from orders.models import Order
from menu.models import MenuCategory, MenuItem
from coupons.models import Coupon


def superadmin_login(request):
    """Superadmin login page"""
    if request.user.is_authenticated and request.user.is_superuser:
        return redirect('superadmin_dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None and user.is_superuser:
            login(request, user)
            return redirect('superadmin_dashboard')
        else:
            messages.error(request, 'Invalid credentials or not a superuser')
    
    return render(request, 'superadmin/login.html')


def superadmin_logout(request):
    """Superadmin logout"""
    logout(request)
    return redirect('superadmin_login')


@login_required(login_url='/superadmin/login/')
def superadmin_dashboard(request):
    """Main superadmin dashboard"""
    if not request.user.is_superuser:
        return redirect('owner_dashboard')
    
    # Get stats
    total_tenants = Tenant.objects.count()
    active_tenants = Tenant.objects.filter(is_active=True).count()
    total_staff = Staff.objects.count()
    
    # Revenue this month
    current_month = timezone.now().month
    current_year = timezone.now().year
    monthly_revenue = Order.objects.filter(
        created_at__month=current_month,
        created_at__year=current_year,
        payment_status='paid'
    ).aggregate(total=Sum('total'))['total'] or 0
    
    # Monthly orders
    monthly_orders = Order.objects.filter(
        created_at__month=current_month,
        created_at__year=current_year
    ).count()
    
    # Recent orders
    recent_orders = Order.objects.select_related('tenant', 'table').order_by('-created_at')[:10]
    
    # Top performing resorts
    top_resorts = Tenant.objects.annotate(
        order_count=Count('orders'),
        revenue=Sum('orders__total')
    ).filter(order_count__gt=0).order_by('-revenue')[:5]
    
    context = {
        'total_tenants': total_tenants,
        'active_tenants': active_tenants,
        'total_staff': total_staff,
        'monthly_revenue': monthly_revenue,
        'monthly_orders': monthly_orders,
        'recent_orders': recent_orders,
        'top_resorts': top_resorts,
    }
    return render(request, 'superadmin/dashboard.html', context)


@login_required(login_url='/superadmin/login/')
def manage_tenants(request):
    """Manage all tenants"""
    if not request.user.is_superuser:
        return redirect('owner_dashboard')
    
    tenants = Tenant.objects.all()
    return render(request, 'superadmin/manage_tenants.html', {'tenants': tenants})


@login_required(login_url='/superadmin/login/')
def add_tenant(request):
    """Add new tenant"""
    if not request.user.is_superuser:
        return redirect('owner_dashboard')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        slug = request.POST.get('slug')
        phone = request.POST.get('phone', '')
        address = request.POST.get('address', '')
        
        if Tenant.objects.filter(slug=slug).exists():
            messages.error(request, 'Slug already exists!')
            return render(request, 'superadmin/add_tenant.html')
        
        tenant = Tenant.objects.create(
            name=name,
            slug=slug,
            phone=phone,
            address=address,
            is_active=True
        )
        messages.success(request, f'{name} added successfully!')
        return redirect('manage_tenants')
    
    return render(request, 'superadmin/add_tenant.html')


@login_required(login_url='/superadmin/login/')
def edit_tenant(request, tenant_id):
    """Edit tenant"""
    if not request.user.is_superuser:
        return redirect('owner_dashboard')
    
    tenant = get_object_or_404(Tenant, id=tenant_id)
    
    if request.method == 'POST':
        tenant.name = request.POST.get('name', tenant.name)
        tenant.phone = request.POST.get('phone', tenant.phone)
        tenant.address = request.POST.get('address', tenant.address)
        tenant.is_active = 'is_active' in request.POST
        tenant.save()
        messages.success(request, f'{tenant.name} updated!')
        return redirect('manage_tenants')
    
    return render(request, 'superadmin/edit_tenant.html', {'tenant': tenant})


@login_required(login_url='/superadmin/login/')
def toggle_tenant(request, tenant_id):
    """Toggle tenant active status"""
    if not request.user.is_superuser:
        return redirect('owner_dashboard')
    
    tenant = get_object_or_404(Tenant, id=tenant_id)
    tenant.is_active = not tenant.is_active
    tenant.save()
    status = 'activated' if tenant.is_active else 'deactivated'
    messages.success(request, f'{tenant.name} {status}!')
    return redirect('manage_tenants')


@login_required(login_url='/superadmin/login/')
def tenant_orders(request, tenant_id):
    """View orders for specific tenant"""
    if not request.user.is_superuser:
        return redirect('owner_dashboard')
    
    tenant = get_object_or_404(Tenant, id=tenant_id)
    orders = Order.objects.filter(tenant=tenant).order_by('-created_at')[:50]
    return render(request, 'superadmin/tenant_orders.html', {'tenant': tenant, 'orders': orders})
