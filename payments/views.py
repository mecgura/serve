"""
MecGuraServe - Payment Views
"""

import json
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.shortcuts import render, get_object_or_404
from django.utils import timezone

from tenants.models import Tenant
from orders.models import Order
from payments.razorpay_handler import create_razorpay_order, verify_payment


@csrf_exempt
@require_POST
def create_order(request):
    """Create Razorpay order for payment"""
    data = json.loads(request.body)
    order_id = data.get('order_id')
    
    try:
        order = Order.objects.select_related('tenant').get(id=order_id)
    except Order.DoesNotExist:
        return JsonResponse({'error': 'Order not found'}, status=404)
    
    # Create Razorpay order
    razorpay_order, error = create_razorpay_order(
        amount=order.total,
        receipt=order.order_number,
        tenant=order.tenant
    )
    
    if error:
        return JsonResponse({'error': error}, status=400)
    
    # Save Razorpay order ID
    order.razorpay_order_id = razorpay_order['id']
    order.save()
    
    return JsonResponse({
        'success': True,
        'razorpay_order_id': razorpay_order['id'],
        'amount': razorpay_order['amount'],
        'currency': razorpay_order['currency'],
        'key': order.tenant.razorpay_key_id or settings.RAZORPAY_KEY_ID,
        'customer_name': order.customer.name if order.customer else 'Guest',
        'customer_phone': order.customer.phone if order.customer else '',
    })


@csrf_exempt
@require_POST
def verify_payment_view(request):
    """Verify Razorpay payment"""
    data = json.loads(request.body)
    order_id = data.get('order_id')
    razorpay_order_id = data.get('razorpay_order_id')
    razorpay_payment_id = data.get('razorpay_payment_id')
    razorpay_signature = data.get('razorpay_signature')
    
    try:
        order = Order.objects.select_related('tenant').get(id=order_id)
    except Order.DoesNotExist:
        return JsonResponse({'error': 'Order not found'}, status=404)
    
    # Verify payment signature
    is_valid, error = verify_payment(
        razorpay_order_id=razorpay_order_id,
        razorpay_payment_id=razorpay_payment_id,
        razorpay_signature=razorpay_signature,
        tenant=order.tenant
    )
    
    if not is_valid:
        order.payment_status = 'failed'
        order.save()
        return JsonResponse({'error': f'Payment verification failed: {error}'}, status=400)
    
    # Payment verified - update order
    order.razorpay_payment_id = razorpay_payment_id
    order.payment_status = 'paid'
    order.status = 'confirmed'
    order.confirmed_at = timezone.now()
    order.save()
    
    # Send WhatsApp bill
    try:
        from whatsapp_integration.utils import send_bill
        send_bill(order)
    except Exception as e:
        print(f"WhatsApp bill failed: {e}")
    
    # Notify kitchen
    try:
        from dashboard.consumers import notify_kitchen
        notify_kitchen(order.tenant.slug, order)
    except Exception as e:
        print(f"Kitchen notification failed: {e}")
    
    return JsonResponse({
        'success': True,
        'order_number': order.order_number,
        'total': str(order.total),
    })


def payment_success(request, order_id):
    """Payment success page"""
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'customer/payment_success.html', {'order': order})


def payment_failed(request, order_id):
    """Payment failed page"""
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'customer/payment_failed.html', {'order': order})
