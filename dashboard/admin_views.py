"""
MecGuraServe - Admin Table Management Views
"""

import io
import json
import zipfile
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Sum

import segno

from tenants.models import (
    Tenant, RestaurantTable, Staff, TableReservation,
    AdvancePayment, ComplimentaryService, TableLayout
)
from orders.models import Order


@login_required
def table_management(request):
    """Table management - layout, QR, assignment"""
    tenant = getattr(request, 'tenant', None)
    if not tenant:
        return redirect('superadmin_dashboard')
    
    tables = RestaurantTable.objects.filter(tenant=tenant).select_related('assigned_waiter__user')
    waiters = Staff.objects.filter(tenant=tenant, role='waiter', is_active=True).select_related('user')
    
    # Get or create layout
    layout, _ = TableLayout.objects.get_or_create(tenant=tenant)
    
    context = {
        'tenant': tenant,
        'tables': tables,
        'waiters': waiters,
        'layout': layout,
    }
    return render(request, 'admin/table_management.html', context)


@login_required
def reservation_management(request):
    """Manage table reservations"""
    tenant = getattr(request, 'tenant', None)
    if not tenant:
        return redirect('superadmin_dashboard')
    
    today = timezone.now().date()
    reservations = TableReservation.objects.filter(
        tenant=tenant
    ).select_related('table').order_by('-reservation_date', '-start_time')
    
    # Filter by status
    status_filter = request.GET.get('status', 'all')
    if status_filter != 'all':
        reservations = reservations.filter(status=status_filter)
    
    # Filter by date
    date_filter = request.GET.get('date', '')
    if date_filter:
        reservations = reservations.filter(reservation_date=date_filter)
    
    context = {
        'tenant': tenant,
        'reservations': reservations[:50],
        'status_filter': status_filter,
        'today': today,
    }
    return render(request, 'admin/reservations.html', context)


@login_required
def advance_payments(request):
    """Manage advance payments"""
    tenant = getattr(request, 'tenant', None)
    if not tenant:
        return redirect('superadmin_dashboard')
    
    payments = AdvancePayment.objects.filter(tenant=tenant).select_related('recorded_by')
    
    # Today's summary
    today = timezone.now().date()
    today_payments = payments.filter(created_at__date=today)
    summary = {
        'total_today': today_payments.aggregate(total=Sum('amount'))['total'] or 0,
        'count_today': today_payments.count(),
        'cash_today': today_payments.filter(payment_method='cash').aggregate(total=Sum('amount'))['total'] or 0,
        'online_today': today_payments.filter(payment_method='razorpay').aggregate(total=Sum('amount'))['total'] or 0,
    }
    
    context = {
        'tenant': tenant,
        'payments': payments[:50],
        'summary': summary,
    }
    return render(request, 'admin/advance_payments.html', context)


@login_required
def complimentary_services(request):
    """Manage complimentary services"""
    tenant = getattr(request, 'tenant', None)
    if not tenant:
        return redirect('superadmin_dashboard')
    
    services = ComplimentaryService.objects.filter(tenant=tenant)
    
    context = {
        'tenant': tenant,
        'services': services,
    }
    return render(request, 'admin/complimentary.html', context)


# ============ API ENDPOINTS ============

@csrf_exempt
@require_POST
def add_table(request):
    """Add new table"""
    data = json.loads(request.body)
    tenant = request.tenant
    
    table = RestaurantTable.objects.create(
        tenant=tenant,
        table_number=data['table_number'],
        capacity=data.get('capacity', 4),
        location=data.get('location', ''),
        pos_x=data.get('pos_x', 0),
        pos_y=data.get('pos_y', 0),
        table_shape=data.get('table_shape', 'round'),
    )
    
    return JsonResponse({
        'success': True,
        'table': {
            'id': table.id,
            'table_number': table.table_number,
            'qr_token': str(table.qr_token),
        }
    })


@csrf_exempt
@require_POST
def update_table_position(request):
    """Update table position on layout"""
    data = json.loads(request.body)
    
    try:
        table = RestaurantTable.objects.get(id=data['table_id'], tenant=request.tenant)
        table.pos_x = data['pos_x']
        table.pos_y = data['pos_y']
        table.save()
        return JsonResponse({'success': True})
    except RestaurantTable.DoesNotExist:
        return JsonResponse({'error': 'Table not found'}, status=404)


@csrf_exempt
@require_POST
def assign_waiter(request):
    """Assign waiter to table"""
    data = json.loads(request.body)
    
    try:
        table = RestaurantTable.objects.get(id=data['table_id'], tenant=request.tenant)
        if data.get('waiter_id'):
            waiter = Staff.objects.get(id=data['waiter_id'], tenant=request.tenant, role='waiter')
            table.assigned_waiter = waiter
        else:
            table.assigned_waiter = None
        table.save()
        return JsonResponse({'success': True})
    except (RestaurantTable.DoesNotExist, Staff.DoesNotExist):
        return JsonResponse({'error': 'Not found'}, status=404)


@csrf_exempt
@require_POST
def update_table_status(request):
    """Update table status"""
    data = json.loads(request.body)
    
    try:
        table = RestaurantTable.objects.get(id=data['table_id'], tenant=request.tenant)
        table.status = data['status']
        table.save()
        return JsonResponse({'success': True})
    except RestaurantTable.DoesNotExist:
        return JsonResponse({'error': 'Table not found'}, status=404)


@csrf_exempt
@require_POST
def add_reservation(request):
    """Add new reservation"""
    data = json.loads(request.body)
    tenant = request.tenant
    
    try:
        table = RestaurantTable.objects.get(id=data['table_id'], tenant=tenant)
        
        reservation = TableReservation.objects.create(
            tenant=tenant,
            table=table,
            customer_name=data['customer_name'],
            customer_phone=data['customer_phone'],
            customer_email=data.get('customer_email', ''),
            reservation_date=data['reservation_date'],
            start_time=data['start_time'],
            end_time=data['end_time'],
            party_size=data.get('party_size', 2),
            advance_amount=data.get('advance_amount', tenant.reservation_advance),
            advance_payment_method=data.get('advance_payment_method', ''),
            advance_status='paid' if data.get('advance_paid') else 'pending',
            special_requests=data.get('special_requests', ''),
            status='confirmed' if data.get('advance_paid') else 'pending',
        )
        
        # Mark table as reserved
        table.status = 'reserved'
        table.save()
        
        return JsonResponse({'success': True, 'reservation_id': reservation.id})
    except RestaurantTable.DoesNotExist:
        return JsonResponse({'error': 'Table not found'}, status=404)


@csrf_exempt
@require_POST
def cancel_reservation(request):
    """Cancel reservation"""
    data = json.loads(request.body)
    
    try:
        reservation = TableReservation.objects.get(id=data['reservation_id'], tenant=request.tenant)
        reservation.status = 'cancelled'
        reservation.save()
        
        # Free up table
        table = reservation.table
        table.status = 'available'
        table.save()
        
        return JsonResponse({'success': True})
    except TableReservation.DoesNotExist:
        return JsonResponse({'error': 'Reservation not found'}, status=404)


@csrf_exempt
@require_POST
def add_advance_payment(request):
    """Add manual advance payment"""
    data = json.loads(request.body)
    tenant = request.tenant
    
    payment = AdvancePayment.objects.create(
        tenant=tenant,
        amount=Decimal(str(data['amount'])),
        payment_method=data['payment_method'],
        reference_number=data.get('reference_number', ''),
        notes=data.get('notes', ''),
        customer_name=data.get('customer_name', ''),
        customer_phone=data.get('customer_phone', ''),
        recorded_by=request.user,
    )
    
    return JsonResponse({'success': True, 'payment_id': payment.id})


@csrf_exempt
@require_POST
def add_complimentary_service(request):
    """Add complimentary service"""
    data = json.loads(request.body)
    tenant = request.tenant
    
    service = ComplimentaryService.objects.create(
        tenant=tenant,
        name=data['name'],
        description=data.get('description', ''),
        value=Decimal(str(data.get('value', 0))),
        min_order_amount=Decimal(str(data.get('min_order_amount', 0))),
        max_per_customer=data.get('max_per_customer', 1),
        is_active=True,
    )
    
    return JsonResponse({'success': True, 'service_id': service.id})


@csrf_exempt
@require_POST
def toggle_complimentary(request):
    """Toggle complimentary service active/inactive"""
    data = json.loads(request.body)
    
    try:
        service = ComplimentaryService.objects.get(id=data['service_id'], tenant=request.tenant)
        service.is_active = not service.is_active
        service.save()
        return JsonResponse({'success': True, 'is_active': service.is_active})
    except ComplimentaryService.DoesNotExist:
        return JsonResponse({'error': 'Service not found'}, status=404)


def download_table_qr(request, table_id):
    """Download QR code for a specific table"""
    table = get_object_or_404(RestaurantTable, id=table_id)
    
    qr = segno.make(table.qr_url)
    buffer = io.BytesIO()
    qr.save(buffer, kind='png', scale=10, border=4)
    buffer.seek(0)
    
    response = HttpResponse(buffer.getvalue(), content_type='image/png')
    response['Content-Disposition'] = f'inline; filename="table_{table.table_number}_qr.png"'
    return response


def download_all_qr_zip(request):
    """Download all QR codes as ZIP"""
    tenant = request.tenant
    tables = RestaurantTable.objects.filter(tenant=tenant, is_active=True)
    
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for table in tables:
            qr = segno.make(table.qr_url)
            qr_buffer = io.BytesIO()
            qr.save(qr_buffer, kind='png', scale=12, border=4)
            qr_buffer.seek(0)
            filename = f"Table_{table.table_number}_QR.png"
            zip_file.writestr(filename, qr_buffer.getvalue())
    
    zip_buffer.seek(0)
    response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
    response['Content-Disposition'] = f'attachment; filename="{tenant.slug}_QR_Codes.zip"'
    return response


# ============ STAFF MANAGEMENT ============

@login_required
def staff_management(request):
    """Manage staff members"""
    tenant = getattr(request, 'tenant', None)
    if not tenant:
        return redirect('superadmin_dashboard')
    
    role_filter = request.GET.get('role', '')
    
    staff_members = Staff.objects.filter(tenant=tenant).select_related('user')
    
    if role_filter:
        staff_members = staff_members.filter(role=role_filter)
    
    context = {
        'tenant': tenant,
        'staff_members': staff_members,
        'role_filter': role_filter,
    }
    return render(request, 'admin/staff_management.html', context)


@csrf_exempt
@require_POST
def add_staff(request):
    """Add new staff member"""
    tenant = request.tenant
    
    try:
        from django.contrib.auth.models import User
        
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        
        # Check if username exists
        if User.objects.filter(username=username).exists():
            return JsonResponse({'error': 'Username already exists'}, status=400)
        
        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )
        
        # Create staff profile
        staff = Staff.objects.create(
            tenant=tenant,
            user=user,
            role=request.POST.get('role', 'waiter'),
            phone=request.POST.get('phone', ''),
            address=request.POST.get('address', ''),
            date_of_birth=request.POST.get('date_of_birth') or None,
            gender=request.POST.get('gender', ''),
            employee_id=request.POST.get('employee_id', ''),
            joining_date=request.POST.get('joining_date') or None,
            salary=request.POST.get('salary') or None,
            shift_start=request.POST.get('shift_start') or None,
            shift_end=request.POST.get('shift_end') or None,
            emergency_contact_name=request.POST.get('emergency_name', ''),
            emergency_contact_phone=request.POST.get('emergency_phone', ''),
        )
        
        # Handle photo upload
        if 'photo' in request.FILES:
            staff.photo = request.FILES['photo']
            staff.save()
        
        return JsonResponse({'success': True, 'staff_id': staff.id})
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
@require_POST
def toggle_staff(request):
    """Toggle staff active/inactive"""
    data = json.loads(request.body)
    
    try:
        staff = Staff.objects.get(id=data['staff_id'], tenant=request.tenant)
        staff.is_active = not staff.is_active
        staff.save()
        return JsonResponse({'success': True, 'is_active': staff.is_active})
    except Staff.DoesNotExist:
        return JsonResponse({'error': 'Staff not found'}, status=404)


@csrf_exempt
@require_POST
def remove_staff(request):
    """Remove staff member (soft delete - deactivate + remove from tables)"""
    data = json.loads(request.body)
    
    try:
        staff = Staff.objects.get(id=data['staff_id'], tenant=request.tenant)
        
        # Remove from assigned tables
        from tenants.models import RestaurantTable
        RestaurantTable.objects.filter(assigned_waiter=staff).update(assigned_waiter=None)
        
        # Deactivate staff
        staff.is_active = False
        staff.save()
        
        # Optionally delete user account
        if data.get('delete_user', False):
            user = staff.user
            staff.delete()
            user.delete()
            return JsonResponse({'success': True, 'deleted': True})
        
        return JsonResponse({'success': True, 'deactivated': True})
    except Staff.DoesNotExist:
        return JsonResponse({'error': 'Staff not found'}, status=404)


@csrf_exempt
@require_POST
def update_staff(request):
    """Update staff member details"""
    data = json.loads(request.body)
    
    try:
        staff = Staff.objects.get(id=data['staff_id'], tenant=request.tenant)
        
        # Update fields
        if 'phone' in data:
            staff.phone = data['phone']
        if 'salary' in data:
            staff.salary = data['salary'] or None
        if 'role' in data:
            staff.role = data['role']
        if 'shift_start' in data:
            staff.shift_start = data['shift_start'] or None
        if 'shift_end' in data:
            staff.shift_end = data['shift_end'] or None
        if 'address' in data:
            staff.address = data['address']
        if 'emergency_name' in data:
            staff.emergency_contact_name = data['emergency_name']
        if 'emergency_phone' in data:
            staff.emergency_contact_phone = data['emergency_phone']
        
        staff.save()
        
        # Update user info
        user = staff.user
        if 'first_name' in data:
            user.first_name = data['first_name']
        if 'last_name' in data:
            user.last_name = data['last_name']
        if 'email' in data:
            user.email = data['email']
        user.save()
        
        return JsonResponse({'success': True})
    except Staff.DoesNotExist:
        return JsonResponse({'error': 'Staff not found'}, status=404)
