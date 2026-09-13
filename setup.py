"""
MecGuraServe - Full Setup Script
Run this script to set up everything automatically
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mecguraserve.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth.models import User
from tenants.models import Tenant, RestaurantTable, Staff, TableLayout
from menu.models import MenuCategory, MenuItem
from coupons.models import Coupon
from orders.models import Order
from django.utils import timezone
from datetime import timedelta
import uuid

print("=" * 60)
print("   MecGuraServe - Full Setup")
print("=" * 60)

# =============================================
# STEP 1: Create Superadmin
# =============================================
print("\n[1/7] Creating Superadmin...")

if not User.objects.filter(username='admin').exists():
    admin = User.objects.create_superuser('admin', 'admin@mecguraserve.com', 'admin123')
    print("   [OK] Superadmin created: admin / admin123")
else:
    admin = User.objects.get(username='admin')
    print("   [--] Superadmin already exists")

# =============================================
# STEP 2: Create Resort 1 - Grand Resort
# =============================================
print("\n[2/7] Creating Grand Resort...")

if not Tenant.objects.filter(slug='grand-resort').exists():
    grand_resort = Tenant.objects.create(
        slug='grand-resort',
        name='Grand Resort & Spa',
        tagline='Experience luxury dining',
        phone='+91 9876543210',
        email='info@grandresort.com',
        address='123 Beach Road, Goa, India',
        primary_color='#FF6B35',
        secondary_color='#004E89',
        plan='premium',
        plan_expiry=timezone.now() + timedelta(days=365),
        tax_percent=5.00,
        service_charge_percent=10.00,
        reservation_advance=100,
        estimated_prep_time=20,
        welcome_message='Welcome to Grand Resort! Scan menu and order.',
        footer_text='Thank you for dining with us!',
    )
    print("   [OK] Grand Resort created")
    
    # Create owner
    owner_user = User.objects.create_user('grand_owner', 'owner@grandresort.com', 'owner123',
                                           first_name='Raj', last_name='Sharma')
    Staff.objects.create(tenant=grand_resort, user=owner_user, role='owner', phone='+91 9876543210')
    print("   [OK] Owner created: grand_owner / owner123")
    
    # Create tables
    tables_data = [
        ('T1', 4, 'Main Hall', 'round'),
        ('T2', 4, 'Main Hall', 'round'),
        ('T3', 6, 'Main Hall', 'rectangle'),
        ('T4', 4, 'Window Side', 'round'),
        ('T5', 4, 'Window Side', 'round'),
        ('T6', 8, 'VIP Section', 'rectangle'),
        ('T7', 4, 'Garden', 'round'),
        ('T8', 4, 'Garden', 'round'),
        ('T9', 6, 'Pool Side', 'rectangle'),
        ('T10', 4, 'Pool Side', 'round'),
    ]
    
    for i, (num, cap, loc, shape) in enumerate(tables_data):
        RestaurantTable.objects.create(
            tenant=grand_resort,
            table_number=num,
            capacity=cap,
            location=loc,
            table_shape=shape,
            pos_x=50 + (i % 5) * 120,
            pos_y=50 + (i // 5) * 120,
        )
    print("   [OK] 10 tables created")
    
    # Create staff
    staff_data = [
        ('rahul', 'Rahul', 'Kumar', 'waiter', '+91 9876543211', 15000),
        ('priya', 'Priya', 'Sharma', 'waiter', '+91 9876543212', 15000),
        ('amit', 'Amit', 'Singh', 'kitchen', '+91 9876543213', 18000),
        ('neha', 'Neha', 'Gupta', 'manager', '+91 9876543214', 25000),
    ]
    
    for username, first, last, role, phone, salary in staff_data:
        user = User.objects.create_user(username, f'{username}@grandresort.com', 'staff123',
                                         first_name=first, last_name=last)
        Staff.objects.create(
            tenant=grand_resort, user=user, role=role,
            phone=phone, salary=salary,
            joining_date=timezone.now().date(),
            employee_id=f'EMP{username[:3].upper()}001',
        )
    print("   [OK] 4 staff members created")
    
    # Assign waiters to tables
    tables = RestaurantTable.objects.filter(tenant=grand_resort)
    waiters = Staff.objects.filter(tenant=grand_resort, role='waiter')
    for i, table in enumerate(tables):
        table.assigned_waiter = waiters[i % len(waiters)]
        table.save()
    print("   [OK] Waiters assigned to tables")
    
else:
    grand_resort = Tenant.objects.get(slug='grand-resort')
    print("   [--] Grand Resort already exists")

# =============================================
# STEP 3: Create Resort 2 - Lake View Hotel
# =============================================
print("\n[3/7] Creating Lake View Hotel...")

if not Tenant.objects.filter(slug='lake-view').exists():
    lake_view = Tenant.objects.create(
        slug='lake-view',
        name='Lake View Hotel',
        tagline='Dine with a view',
        phone='+91 9876543220',
        email='info@lakeview.com',
        address='456 Lake Road, Udaipur, India',
        primary_color='#2196F3',
        secondary_color='#00BCD4',
        plan='basic',
        plan_expiry=timezone.now() + timedelta(days=365),
        tax_percent=5.00,
        reservation_advance=100,
        estimated_prep_time=25,
    )
    print("   [OK] Lake View Hotel created")
    
    # Create owner
    owner_user = User.objects.create_user('lake_owner', 'owner@lakeview.com', 'owner123',
                                           first_name='Priya', last_name='Patel')
    Staff.objects.create(tenant=lake_view, user=owner_user, role='owner', phone='+91 9876543220')
    print("   [OK] Owner created: lake_owner / owner123")
    
    # Create tables
    for i in range(1, 8):
        RestaurantTable.objects.create(
            tenant=lake_view,
            table_number=f'T{i}',
            capacity=4,
            location='Lake View',
            pos_x=50 + (i % 4) * 120,
            pos_y=50 + (i // 4) * 120,
        )
    print("   [OK] 7 tables created")
    
else:
    lake_view = Tenant.objects.get(slug='lake-view')
    print("   [--] Lake View Hotel already exists")

# =============================================
# STEP 4: Create Menu for Grand Resort
# =============================================
print("\n[4/7] Creating Menu...")

categories_data = {
    'grand-resort': [
        ('Starters', [
            ('Paneer Tikka', 180, 'Grilled cottage cheese with spices', True),
            ('Chicken Seekh', 220, 'Minced chicken kebabs', False),
            ('Veg Spring Rolls', 150, 'Crispy vegetable rolls', True),
            ('Fish Amritsari', 280, 'Bengal fish fried in gram flour', False),
            ('Malai Chaap', 200, 'Soya chaap in creamy sauce', True),
        ]),
        ('Main Course', [
            ('Butter Chicken', 320, 'Creamy tomato based curry', False),
            ('Paneer Butter Masala', 280, 'Cottage cheese in butter gravy', True),
            ('Dal Makhani', 220, 'Black lentils slow cooked', True),
            ('Mutton Rogan Josh', 380, 'Kashmiri style mutton curry', False),
            ('Veg Biryani', 250, 'Fragrant rice with vegetables', True),
            ('Chicken Biryani', 300, 'Hyderabadi style biryani', False),
        ]),
        ('Breads', [
            ('Butter Naan', 60, 'Soft bread baked in tandoor', True),
            ('Garlic Naan', 70, 'Naan with garlic butter', True),
            ('Tandoori Roti', 40, 'Whole wheat bread', True),
            ('Laccha Paratha', 50, 'Layered flaky bread', True),
        ]),
        ('Rice', [
            ('Steamed Rice', 120, 'Plain basmati rice', True),
            ('Jeera Rice', 150, 'Cumin flavored rice', True),
        ]),
        ('Drinks', [
            ('Fresh Lime Soda', 60, 'Sweet or salted', True),
            ('Mango Lassi', 80, 'Creamy yogurt drink', True),
            ('Masala Chai', 40, 'Spiced Indian tea', True),
            ('Cold Coffee', 90, 'Iced coffee with cream', True),
            ('Mineral Water', 30, 'Packaged drinking water', True),
        ]),
        ('Desserts', [
            ('Gulab Jamun', 80, 'Deep fried milk balls in syrup', True),
            ('Rasmalai', 100, 'Cottage cheese in saffron milk', True),
            ('Kulfi', 70, 'Traditional Indian ice cream', True),
            ('Gajar Ka Halwa', 90, 'Carrot pudding with nuts', True),
        ]),
    ],
    'lake-view': [
        ('Starters', [
            ('Veg Pakora', 120, 'Fried vegetable fritters', True),
            ('Chicken Tikka', 200, 'Grilled chicken pieces', False),
        ]),
        ('Main Course', [
            ('Dal Fry', 150, 'Tempered lentils', True),
            ('Chicken Curry', 250, 'Home style chicken curry', False),
            ('Paneer Sabzi', 200, 'Cottage cheese curry', True),
        ]),
        ('Drinks', [
            ('Lassi', 60, 'Yogurt drink', True),
            ('Tea', 30, 'Indian tea', True),
        ]),
    ],
}

for tenant_slug, categories in categories_data.items():
    tenant = Tenant.objects.get(slug=tenant_slug)
    
    if MenuCategory.objects.filter(tenant=tenant).exists():
        print(f"   [--] {tenant.name} menu already exists")
        continue
    
    for cat_name, items in categories:
        category = MenuCategory.objects.create(tenant=tenant, name=cat_name)
        
        for i, (name, price, desc, is_veg) in enumerate(items):
            MenuItem.objects.create(
                tenant=tenant,
                category=category,
                name=name,
                price=price,
                description=desc,
                is_vegetarian=is_veg,
                is_available=True,
                sort_order=i,
            )
    
    print(f"   [OK] {tenant.name} menu created")

# =============================================
# STEP 5: Create Coupons
# =============================================
print("\n[5/7] Creating Coupons...")

coupons_data = [
    ('WELCOME20', 'percentage', 20, 0, 100, 500),
    ('FLAT50', 'fixed', 50, 200, 50, None),
    ('FESTIVE10', 'percentage', 10, 0, 200, None),
]

for tenant_slug in ['grand-resort', 'lake-view']:
    tenant = Tenant.objects.get(slug=tenant_slug)
    
    if Coupon.objects.filter(tenant=tenant).exists():
        print(f"   [--] {tenant.name} coupons already exist")
        continue
    
    for code, dtype, value, min_order, max_uses, valid_days in coupons_data:
        Coupon.objects.create(
            tenant=tenant,
            code=code,
            discount_type=dtype,
            discount_value=value,
            min_order_amount=min_order,
            max_uses=max_uses,
            valid_until=timezone.now() + timedelta(days=valid_days) if valid_days else None,
        )
    
    print(f"   [OK] {tenant.name} coupons created")

# =============================================
# STEP 6: Create Table Layouts
# =============================================
print("\n[6/7] Creating Table Layouts...")

for tenant_slug in ['grand-resort', 'lake-view']:
    tenant = Tenant.objects.get(slug=tenant_slug)
    TableLayout.objects.get_or_create(
        tenant=tenant,
        defaults={'name': 'Main Floor', 'width': 800, 'height': 600}
    )
    print(f"   [OK] {tenant.name} layout created")

# =============================================
# STEP 7: Summary
# =============================================
print("\n[7/7] Setup Complete!")
print("\n" + "=" * 60)
print("   SETUP SUMMARY")
print("=" * 60)

print("\nDatabase Stats:")
print(f"   Users: {User.objects.count()}")
print(f"   Tenants: {Tenant.objects.count()}")
print(f"   Tables: {RestaurantTable.objects.count()}")
print(f"   Staff: {Staff.objects.count()}")
print(f"   Menu Categories: {MenuCategory.objects.count()}")
print(f"   Menu Items: {MenuItem.objects.count()}")
print(f"   Coupons: {Coupon.objects.count()}")

print("\n" + "=" * 60)
print("   LOGIN CREDENTIALS")
print("=" * 60)

print("\nSuperadmin:")
print("   URL: http://localhost:8000/superadmin/login/")
print("   Username: admin")
print("   Password: admin123")

print("\nGrand Resort:")
print("   Admin Panel: http://localhost:8000/dashboard/admin/?tenant=grand-resort")
print("   Owner Login: grand_owner / owner123")
print("   Staff Login: http://localhost:8000/dashboard/staff-login/?tenant=grand-resort")
print("   - rahul / staff123 (Waiter)")
print("   - priya / staff123 (Waiter)")
print("   - amit / staff123 (Kitchen)")
print("   - neha / staff123 (Manager)")

print("\nLake View Hotel:")
print("   Admin Panel: http://localhost:8000/dashboard/admin/?tenant=lake-view")
print("   Owner Login: lake_owner / owner123")

print("\n" + "=" * 60)
print("   QUICK START")
print("=" * 60)

print("\n1. Run server:")
print("   python manage.py runserver")

print("\n2. Open browser:")
print("   http://localhost:8000/superadmin/login/")

print("\n3. Login as admin:")
print("   Username: admin")
print("   Password: admin123")

print("\n4. Access Grand Resort:")
print("   http://localhost:8000/dashboard/admin/?tenant=grand-resort")

print("\n" + "=" * 60)
print("   MecGuraServe - Setup Complete!")
print("=" * 60)
