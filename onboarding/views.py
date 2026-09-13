"""
MecGuraServe - Onboarding Views
Step-by-step resort setup wizard
"""

from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
import uuid

from tenants.models import Tenant, RestaurantTable


def onboarding_home(request):
    """Onboarding wizard home"""
    return render(request, 'onboarding/wizard.html')


def onboarding_step1(request):
    """Step 1: Basic resort info"""
    if request.method == 'POST':
        # Save to session
        request.session['onboarding'] = {
            'name': request.POST.get('name'),
            'phone': request.POST.get('phone'),
            'email': request.POST.get('email'),
            'address': request.POST.get('address'),
            'tagline': request.POST.get('tagline', 'Welcome! Scan menu and order.'),
        }
        return redirect('onboarding_step2')
    return redirect('onboarding_home')


def onboarding_step2(request):
    """Step 2: Branding"""
    if request.method == 'POST':
        onboarding = request.session.get('onboarding', {})
        onboarding['primary_color'] = request.POST.get('primary_color', '#FF6B35')
        onboarding['secondary_color'] = request.POST.get('secondary_color', '#004E89')
        onboarding['welcome_message'] = request.POST.get('welcome_message', 'Welcome! Scan menu and order.')
        request.session['onboarding'] = onboarding
        return redirect('onboarding_step3')
    return redirect('onboarding_home')


def onboarding_step3(request):
    """Step 3: Restaurant settings"""
    if request.method == 'POST':
        onboarding = request.session.get('onboarding', {})
        onboarding['tax_percent'] = request.POST.get('tax_percent', 5)
        onboarding['service_charge_percent'] = request.POST.get('service_charge_percent', 0)
        onboarding['min_order_amount'] = request.POST.get('min_order_amount', 0)
        onboarding['estimated_prep_time'] = request.POST.get('estimated_prep_time', 20)
        onboarding['num_tables'] = request.POST.get('num_tables', 10)
        request.session['onboarding'] = onboarding
        return redirect('onboarding_step4')
    return redirect('onboarding_home')


def onboarding_step4(request):
    """Step 4: Payment setup"""
    if request.method == 'POST':
        onboarding = request.session.get('onboarding', {})
        onboarding['razorpay_key_id'] = request.POST.get('razorpay_key_id', '')
        onboarding['razorpay_key_secret'] = request.POST.get('razorpay_key_secret', '')
        onboarding['whatsapp_token'] = request.POST.get('whatsapp_token', '')
        onboarding['whatsapp_phone_id'] = request.POST.get('whatsapp_phone_id', '')
        request.session['onboarding'] = onboarding
        
        # Create tenant
        return redirect('onboarding_complete')
    return redirect('onboarding_home')


def onboarding_complete(request):
    """Step 5: Create resort and show success"""
    onboarding = request.session.get('onboarding', {})
    
    if not onboarding.get('name'):
        messages.error(request, 'Please complete all steps.')
        return redirect('onboarding_home')
    
    # Generate slug
    slug = onboarding['name'].lower().replace(' ', '-').replace('&', 'and')
    slug = ''.join(c for c in slug if c.isalnum() or c == '-')[:50]
    
    # Create tenant
    tenant, created = Tenant.objects.get_or_create(
        slug=slug,
        defaults={
            'name': onboarding['name'],
            'tagline': onboarding.get('tagline', 'Welcome! Scan menu and order.'),
            'phone': onboarding['phone'],
            'email': onboarding['email'],
            'address': onboarding['address'],
            'primary_color': onboarding.get('primary_color', '#FF6B35'),
            'secondary_color': onboarding.get('secondary_color', '#004E89'),
            'welcome_message': onboarding.get('welcome_message', 'Welcome! Scan menu and order.'),
            'tax_percent': onboarding.get('tax_percent', 5),
            'service_charge_percent': onboarding.get('service_charge_percent', 0),
            'min_order_amount': onboarding.get('min_order_amount', 0),
            'estimated_prep_time': onboarding.get('estimated_prep_time', 20),
            'razorpay_key_id': onboarding.get('razorpay_key_id', ''),
            'razorpay_key_secret': onboarding.get('razorpay_key_secret', ''),
            'whatsapp_api_token': onboarding.get('whatsapp_token', ''),
            'whatsapp_phone_number_id': onboarding.get('whatsapp_phone_id', ''),
        }
    )
    
    if created:
        # Create tables
        num_tables = int(onboarding.get('num_tables', 10))
        for i in range(1, num_tables + 1):
            RestaurantTable.objects.create(
                tenant=tenant,
                table_number=f'T{i}',
                capacity=4,
            )
        
        messages.success(request, f'{tenant.name} has been created successfully!')
    
    # Clear onboarding session
    if 'onboarding' in request.session:
        del request.session['onboarding']
    
    return render(request, 'onboarding/success.html', {
        'tenant': tenant,
        'slug': slug,
    })
