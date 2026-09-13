"""
MecGuraServe - Razorpay Payment Handler
"""

import razorpay
from django.conf import settings


def get_razorpay_client(tenant=None):
    """Get Razorpay client with resort's credentials"""
    
    key_id = ''
    key_secret = ''
    
    if tenant and tenant.razorpay_key_id:
        key_id = tenant.razorpay_key_id
        key_secret = tenant.razorpay_key_secret
    else:
        key_id = settings.RAZORPAY_KEY_ID
        key_secret = settings.RAZORPAY_KEY_SECRET
    
    if not key_id or not key_secret:
        return None
    
    return razorpay.Client(auth=(key_id, key_secret))


def create_razorpay_order(amount, currency='INR', receipt=None, tenant=None):
    """Create a Razorpay order"""
    
    client = get_razorpay_client(tenant)
    if not client:
        return None, "Razorpay not configured"
    
    try:
        # Amount should be in paise (multiply by 100)
        amount_in_paise = int(amount * 100)
        
        order_data = {
            'amount': amount_in_paise,
            'currency': currency,
            'receipt': receipt or f"order_{receipt}",
        }
        
        order = client.order.create(data=order_data)
        return order, None
    
    except Exception as e:
        return None, str(e)


def verify_payment(razorpay_order_id, razorpay_payment_id, razorpay_signature, tenant=None):
    """Verify Razorpay payment signature"""
    
    client = get_razorpay_client(tenant)
    if not client:
        return False, "Razorpay not configured"
    
    try:
        params = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature,
        }
        
        client.utility.verify_payment_signature(params)
        return True, None
    
    except Exception as e:
        return False, str(e)
