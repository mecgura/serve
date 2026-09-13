"""
MecGuraServe - Staff Login & Dashboard Views
"""

import json
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from tenants.models import Tenant, Staff


def staff_login_page(request):
    """Staff login page"""
    tenant_slug = request.GET.get('tenant') or request.session.get('tenant_slug')
    if not tenant_slug:
        return redirect('superadmin_login')
    
    try:
        tenant = Tenant.objects.get(slug=tenant_slug, is_active=True)
    except Tenant.DoesNotExist:
        return redirect('superadmin_login')
    
    return render(request, 'staff/login.html', {'tenant': tenant})


@csrf_exempt
@require_POST
def staff_login(request):
    """Staff login API"""
    data = json.loads(request.body)
    tenant_slug = request.GET.get('tenant') or request.session.get('tenant_slug')
    
    try:
        tenant = Tenant.objects.get(slug=tenant_slug, is_active=True)
    except Tenant.DoesNotExist:
        return JsonResponse({'error': 'Resort not found'}, status=404)
    
    username = data.get('username')
    password = data.get('password')
    staff_type = data.get('staff_type', 'waiter')
    
    user = authenticate(request, username=username, password=password)
    
    if user is None:
        return JsonResponse({'error': 'Invalid username or password'}, status=401)
    
    # Check if user is staff for this tenant
    try:
        staff = Staff.objects.get(user=user, tenant=tenant, is_active=True)
    except Staff.DoesNotExist:
        return JsonResponse({'error': 'You are not staff at this resort'}, status=403)
    
    # Check role matches
    if staff_type == 'waiter' and staff.role not in ['waiter', 'manager']:
        return JsonResponse({'error': 'This is not a waiter account'}, status=403)
    if staff_type == 'kitchen' and staff.role not in ['kitchen', 'manager']:
        return JsonResponse({'error': 'This is not a kitchen account'}, status=403)
    
    login(request, user)
    request.session['staff_id'] = staff.id
    request.session['tenant_slug'] = tenant.slug
    
    if staff.role in ['kitchen']:
        redirect_url = f'/dashboard/kitchen-staff/?tenant={tenant.slug}'
    else:
        redirect_url = f'/dashboard/staff-panel/?tenant={tenant.slug}'
    
    return JsonResponse({'success': True, 'redirect_url': redirect_url})


def staff_logout(request):
    """Staff logout"""
    logout(request)
    return redirect('staff_login_page')


@login_required
def staff_panel(request):
    """Staff dashboard for waiters"""
    tenant_slug = request.GET.get('tenant') or request.session.get('tenant_slug')
    staff_id = request.session.get('staff_id')
    
    if not tenant_slug or not staff_id:
        return redirect('superadmin_login')
    
    try:
        tenant = Tenant.objects.get(slug=tenant_slug, is_active=True)
        staff = Staff.objects.get(id=staff_id, tenant=tenant, is_active=True)
    except (Tenant.DoesNotExist, Staff.DoesNotExist):
        return redirect('superadmin_login')
    
    # Get assigned orders
    from orders.models import Order
    
    # For waiters - get orders from their assigned tables
    if staff.role == 'waiter':
        assigned_tables = staff.assigned_tables.all()
        assigned_orders = Order.objects.filter(
            tenant=tenant,
            table__in=assigned_tables,
            status__in=['pending', 'confirmed', 'preparing', 'ready']
        ).select_related('table', 'customer').prefetch_related('items__menu_item').order_by('-created_at')
    else:
        # Managers see all
        assigned_orders = Order.objects.filter(
            tenant=tenant,
            status__in=['pending', 'confirmed', 'preparing', 'ready']
        ).select_related('table', 'customer').prefetch_related('items__menu_item').order_by('-created_at')
    
    # Stats
    today = timezone.now().date()
    completed_today = Order.objects.filter(
        tenant=tenant,
        table__assigned_waiter=staff,
        status='completed',
        created_at__date=today
    ).count()
    
    context = {
        'tenant': tenant,
        'staff': staff,
        'assigned_orders': assigned_orders,
        'pending_count': assigned_orders.filter(status='pending').count(),
        'completed_count': completed_today,
    }
    return render(request, 'staff/dashboard.html', context)


# ============ ORDER COMPLETE VIEW ============

def order_complete(request):
    """Order complete page with engagement content"""
    from orders.models import Order, OrderItem
    
    tenant_slug = request.GET.get('tenant')
    order_id = request.GET.get('order_id')
    lang = request.GET.get('lang', 'en')
    
    if not tenant_slug or not order_id:
        return redirect('superadmin_login')
    
    try:
        tenant = Tenant.objects.get(slug=tenant_slug, is_active=True)
        order = Order.objects.get(id=order_id, tenant=tenant)
    except (Tenant.DoesNotExist, Order.DoesNotExist):
        return redirect('superadmin_login')
    
    # Get assigned waiter
    assigned_waiter = None
    if order.table and order.table.assigned_waiter:
        assigned_waiter = order.table.assigned_waiter
    
    # Food facts
    facts = [
        {
            "text": "Honey never spoils! Archaeologists found 3000-year-old honey in Egyptian tombs that was still edible.",
            "text_hi": "शहद कभी खराब नहीं होता! मिस्र के पिरामिडों में 3000 साल पुराना शहद मिला जो अभी भी खाने योग्य था।",
            "source": "National Geographic"
        },
        {
            "text": "Bananas are berries, but strawberries are not! Botanically speaking, bananas meet all criteria of a berry.",
            "text_hi": "केला एक बेरी है, लेकिन स्ट्रॉबेरी नहीं! वनस्पतिशास्त्र के अनुसार, केला बेरी की सभी शर्तें पूरी करता है।",
            "source": "Botany Science"
        },
        {
            "text": "India is the world's largest producer of milk, pulses, and spices!",
            "text_hi": "भारत दूध, दालों और मसालों का विश्व का सबसे बड़ा उत्पादक है!",
            "source": "FAO Statistics"
        },
        {
            "text": "The world's most expensive spice is Saffron (Kesar), which costs more than gold by weight!",
            "text_hi": "दुनिया का सबसे महंगा मसाला केसर है, जो वजन में सोने से भी महंगा है!",
            "source": "Spice Trade India"
        },
        {
            "text": "Chocolate was once used as currency by the Aztecs. Cacao beans were more valuable than gold dust!",
            "text_hi": "चॉकलेट का इस्तेमाल एक समय में एज़्टेक लोग मुद्रा के रूप में करते थे! कोको के दाने सोने की धूल से भी ज़्यादा कीमती थे!",
            "source": "History Channel"
        },
        {
            "text": "Carrots were originally purple! The orange variety was developed in the Netherlands in the 17th century.",
            "text_hi": "गाजर मूल रूप से बैंगनी रंग की थी! नारंगी किस्म 17वीं सदी में नीदरलैंड में विकसित की गई थी।",
            "source": "History of Food"
        }
    ]
    
    import random
    current_fact = random.choice(facts)
    
    # Resort story
    resort_story = f"""{tenant.name} has been serving authentic cuisine since its establishment. 
    Our chefs combine traditional recipes with modern techniques to create an unforgettable dining experience. 
    We source our ingredients from local farmers to ensure the freshest quality in every dish.
    From our humble beginnings to becoming a beloved dining destination, we've always believed in 
    the power of good food to bring people together."""
    
    if lang == 'hi':
        resort_story = f"""{tenant.name} अपनी स्थापना से प्रामाणिक व्यंजन परोसता आ रहा है। 
    हमारे शेफ पारंपरिक व्यंजनों को आधुनिक तकनीकों के साथ मिलाकर एक अविस्मरणीय भोज अनुभव बनाते हैं। 
    हम स्थानीय किसानों से अपनी सामग्री प्राप्त करते हैं ताकि हर व्यंजन में ताज़गी सुनिश्चित हो सके।
    हमारे विनम्र शुरुआत से लेकर एक प्रिय भोजन गंतव्य बनने तक, हमने हमेशा अच्छे भोजन की शक्ति में विश्वास किया है
    जो लोगों को एक साथ लाता है।"""
    
    # Food quiz
    quizzes = [
        {
            "question": "Which country is the origin of Pizza?",
            "question_hi": "पिज़्ज़ा किस देश की उत्पत्ति है?",
            "options": ["Italy", "France", "Greece", "Spain"],
            "options_hi": ["इटली", "फ्रांस", "यूनान", "स्पेन"],
            "correct_index": 0
        },
        {
            "question": "What is the main ingredient in Guacamole?",
            "question_hi": "गुआकामोले का मुख्य घटक क्या है?",
            "options": ["Tomato", "Avocado", "Onion", "Pepper"],
            "options_hi": ["टमाटर", "एवोकाडो", "प्याज", "मिर्च"],
            "correct_index": 1
        },
        {
            "question": "Which spice is known as 'Queen of Spices'?",
            "question_hi": "किस मसाले को 'मसालों की रानी' कहा जाता है?",
            "options": ["Cinnamon", "Cardamom", "Clove", "Pepper"],
            "options_hi": ["दालचीनी", "इलायची", "लौंग", "काली मिर्च"],
            "correct_index": 1
        }
    ]
    
    current_quiz = random.choice(quizzes)
    if lang == 'hi':
        current_quiz['question'] = current_quiz['question_hi']
        current_quiz['options'] = current_quiz['options_hi']
    
    import json as json_module
    facts_json = json_module.dumps(facts)
    
    context = {
        'tenant': tenant,
        'order': order,
        'assigned_waiter': assigned_waiter,
        'lang': lang,
        'current_fact': current_fact,
        'facts_json': facts_json,
        'resort_story': resort_story,
        'current_quiz': current_quiz,
    }
    return render(request, 'customer/order_complete.html', context)
