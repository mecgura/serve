"""
MecGuraServe - Customer Flow Views
QR Scan → Welcome → Details → Menu → Order → Payment → Thank You
"""

import json
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.conf import settings

from tenants.models import Tenant, RestaurantTable
from menu.models import MenuCategory, MenuItem
from orders.models import Customer, Order, OrderItem
from coupons.models import Coupon, HappyHour


def customer_menu(request):
    """Main menu page - accessed via QR code scan"""
    table_token = request.GET.get('table')
    
    if not table_token:
        return render(request, 'customer/error.html', {'error': 'Invalid QR code. Please scan again.'})
    
    # Find table by QR token
    try:
        import uuid
        uuid.UUID(str(table_token))  # Validate UUID format
        table = RestaurantTable.objects.select_related('tenant').get(
            qr_token=table_token,
            is_active=True
        )
    except (ValueError, RestaurantTable.DoesNotExist):
        return render(request, 'customer/error.html', {'error': 'Table not found. Please ask staff for assistance.'})
    
    tenant = table.tenant
    
    # Store table info in session
    request.session['table_id'] = table.id
    request.session['tenant_slug'] = tenant.slug
    request.session['table_number'] = table.table_number
    
    # Check if customer already has active order on this table
    customer_phone = request.session.get('customer_phone')
    existing_order = None
    if customer_phone:
        try:
            customer = Customer.objects.get(tenant=tenant, phone=customer_phone)
            existing_order = Order.objects.filter(
                tenant=tenant,
                table=table,
                customer=customer,
                status__in=['pending', 'confirmed', 'preparing', 'ready']
            ).first()
        except Customer.DoesNotExist:
            pass
    
    # Get menu
    categories = MenuCategory.objects.filter(tenant=tenant, is_active=True).prefetch_related('items')
    
    # Get active offers
    active_offers = []
    for offer in tenant.offers.filter(is_active=True):
        if offer.is_valid:
            active_offers.append(offer)
    
    # Get active happy hours
    happy_hours = HappyHour.objects.filter(tenant=tenant, is_active=True)
    active_happy_hours = [hh for hh in happy_hours if hh.is_active_now]
    
    context = {
        'tenant': tenant,
        'table': table,
        'categories': categories,
        'existing_order': existing_order,
        'active_offers': active_offers,
        'active_happy_hours': active_happy_hours,
        'razorpay_key': tenant.razorpay_key_id,
    }
    
    return render(request, 'customer/menu.html', context)


def customer_details(request):
    """Customer name/phone entry page"""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        phone = request.POST.get('phone', '').strip()
        skip = request.POST.get('skip')
        
        if skip:
            # Guest mode
            request.session['customer_name'] = 'Guest'
            request.session['customer_phone'] = ''
            return redirect('customer_menu')
        
        if not phone:
            return render(request, 'customer/details.html', {
                'error': 'Phone number is required',
                'table_number': request.session.get('table_number'),
            })
        
        # Save to session
        request.session['customer_name'] = name or 'Guest'
        request.session['customer_phone'] = phone
        
        # Create/update customer in DB
        tenant_slug = request.session.get('tenant_slug')
        if tenant_slug:
            try:
                tenant = Tenant.objects.get(slug=tenant_slug)
                customer, created = Customer.objects.get_or_create(
                    tenant=tenant,
                    phone=phone,
                    defaults={'name': name}
                )
                if not created and name:
                    customer.name = name
                    customer.save()
                request.session['customer_id'] = customer.id
            except Tenant.DoesNotExist:
                pass
        
        return redirect('customer_menu')
    
    context = {
        'table_number': request.session.get('table_number'),
    }
    return render(request, 'customer/details.html', context)


@csrf_exempt
@require_POST
def apply_coupon(request):
    """Validate and apply coupon code"""
    data = json.loads(request.body)
    code = data.get('code', '').strip().upper()
    subtotal = Decimal(str(data.get('subtotal', 0)))
    
    tenant_slug = request.session.get('tenant_slug')
    if not tenant_slug:
        return JsonResponse({'error': 'Session expired. Please refresh.'}, status=400)
    
    try:
        tenant = Tenant.objects.get(slug=tenant_slug)
    except Tenant.DoesNotExist:
        return JsonResponse({'error': 'Invalid restaurant'}, status=400)
    
    try:
        coupon = Coupon.objects.get(tenant=tenant, code=code, is_active=True)
    except Coupon.DoesNotExist:
        return JsonResponse({'error': 'Invalid coupon code'}, status=400)
    
    if not coupon.is_valid:
        return JsonResponse({'error': 'Coupon has expired or reached usage limit'}, status=400)
    
    if subtotal < coupon.min_order_amount:
        return JsonResponse({
            'error': f'Minimum order ₹{coupon.min_order_amount} required for this coupon'
        }, status=400)
    
    discount = coupon.calculate_discount(subtotal)
    
    # Store coupon in session
    request.session['coupon_id'] = coupon.id
    request.session['coupon_code'] = coupon.code
    request.session['discount_amount'] = str(discount)
    
    return JsonResponse({
        'success': True,
        'coupon_code': coupon.code,
        'discount': str(discount),
        'description': coupon.description,
    })


@csrf_exempt
@require_POST
def remove_coupon(request):
    """Remove applied coupon"""
    request.session.pop('coupon_id', None)
    request.session.pop('coupon_code', None)
    request.session.pop('discount_amount', None)
    return JsonResponse({'success': True})


@csrf_exempt
@require_POST
def place_order(request):
    """Place order and optionally initiate payment"""
    data = json.loads(request.body)
    
    # Get session data
    tenant_slug = request.session.get('tenant_slug')
    table_id = request.session.get('table_id')
    customer_name = request.session.get('customer_name', 'Guest')
    customer_phone = request.session.get('customer_phone', '')
    
    if not tenant_slug or not table_id:
        return JsonResponse({'error': 'Session expired. Please scan QR again.'}, status=400)
    
    # Get tenant
    try:
        tenant = Tenant.objects.get(slug=tenant_slug)
        table = RestaurantTable.objects.get(id=table_id, tenant=tenant)
    except (Tenant.DoesNotExist, RestaurantTable.DoesNotExist):
        return JsonResponse({'error': 'Invalid restaurant or table'}, status=400)
    
    # Get or create customer
    customer = None
    if customer_phone:
        customer, _ = Customer.objects.get_or_create(
            tenant=tenant,
            phone=customer_phone,
            defaults={'name': customer_name}
        )
    
    # Parse order items
    items_data = data.get('items', [])
    if not items_data:
        return JsonResponse({'error': 'No items in order'}, status=400)
    
    # Calculate pricing
    subtotal = Decimal('0')
    order_items = []
    
    for item_data in items_data:
        try:
            menu_item = MenuItem.objects.get(id=item_data['id'], tenant=tenant, is_available=True)
        except MenuItem.DoesNotExist:
            return JsonResponse({'error': f'Item not found: {item_data["id"]}'}, status=400)
        
        quantity = int(item_data.get('quantity', 1))
        item_total = menu_item.price * quantity
        
        order_items.append({
            'menu_item': menu_item,
            'quantity': quantity,
            'unit_price': menu_item.price,
            'total_price': item_total,
            'special_instructions': item_data.get('instructions', ''),
            'customizations': item_data.get('customizations', {}),
        })
        
        subtotal += item_total
    
    # Apply coupon discount
    discount_amount = Decimal(request.session.get('discount_amount', '0'))
    coupon_id = request.session.get('coupon_id')
    coupon_code = request.session.get('coupon_code', '')
    
    # Calculate tax and total
    tax_amount = subtotal * (tenant.tax_percent / 100)
    service_charge = subtotal * (tenant.service_charge_percent / 100)
    total = subtotal - discount_amount + tax_amount + service_charge
    
    # Determine payment method
    payment_method = data.get('payment_method', 'razorpay')
    
    # Create order
    order = Order(
        tenant=tenant,
        table=table,
        customer=customer,
        subtotal=subtotal,
        discount_amount=discount_amount,
        tax_amount=tax_amount,
        service_charge=service_charge,
        total=total,
        payment_method=payment_method,
        special_instructions=data.get('instructions', ''),
        estimated_time=tenant.estimated_prep_time,
    )
    
    if coupon_id:
        from coupons.models import Coupon
        try:
            order.coupon = Coupon.objects.get(id=coupon_id)
            order.coupon_code = coupon_code
        except Coupon.DoesNotExist:
            pass
    
    order.save()
    
    # Create order items
    for item_data in order_items:
        OrderItem.objects.create(
            order=order,
            menu_item=item_data['menu_item'],
            quantity=item_data['quantity'],
            unit_price=item_data['unit_price'],
            total_price=item_data['total_price'],
            special_instructions=item_data['special_instructions'],
            customizations=item_data['customizations'],
        )
    
    # Update customer stats
    if customer:
        customer.total_orders += 1
        customer.total_spent += total
        customer.last_order_at = timezone.now()
        customer.save()
    
    # Update coupon usage
    if coupon_id:
        from coupons.models import Coupon
        try:
            coupon = Coupon.objects.get(id=coupon_id)
            coupon.used_count += 1
            coupon.save()
        except Coupon.DoesNotExist:
            pass
    
    # Clear session coupon data
    request.session.pop('coupon_id', None)
    request.session.pop('coupon_code', None)
    request.session.pop('discount_amount', None)
    
    # Notify kitchen via WebSocket
    try:
        from dashboard.consumers import notify_kitchen
        notify_kitchen(tenant.slug, order)
    except Exception as e:
        print(f"WebSocket notification failed: {e}")
    
    # Response based on payment method
    if payment_method == 'razorpay':
        return JsonResponse({
            'success': True,
            'order_id': order.id,
            'order_number': order.order_number,
            'total': str(order.total),
            'razorpay_key': tenant.razorpay_key_id,
            'razorpay_order_id': '',  # Will be created when payment is initiated
            'customer_name': customer_name,
            'customer_phone': customer_phone,
        })
    else:
        # Cash/Card/UPI at counter - order placed directly
        order.status = 'confirmed'
        order.confirmed_at = timezone.now()
        order.save()
        
        return JsonResponse({
            'success': True,
            'order_id': order.id,
            'order_number': order.order_number,
            'total': str(order.total),
            'payment_method': payment_method,
            'message': f'Order placed! Pay ₹{order.total} at the counter.',
        })


def order_tracking(request, order_id):
    """Order tracking page"""
    try:
        order = Order.objects.select_related('table', 'customer').prefetch_related('items__menu_item').get(id=order_id)
    except Order.DoesNotExist:
        return render(request, 'customer/error.html', {'error': 'Order not found'})
    
    context = {
        'order': order,
        'items': order.items.all(),
    }
    return render(request, 'customer/tracking.html', context)


def order_thank_you(request, order_id):
    """Thank you page after order"""
    try:
        order = Order.objects.select_related('table', 'customer').get(id=order_id)
    except Order.DoesNotExist:
        return render(request, 'customer/error.html', {'error': 'Order not found'})
    
    context = {
        'order': order,
    }
    return render(request, 'customer/thank_you.html', context)
