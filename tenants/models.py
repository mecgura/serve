"""
MecGuraServe - Tenant Models (Resort/Hotel)
"""

import uuid
from django.db import models
from django.utils.text import slugify
from django.utils import timezone


class Tenant(models.Model):
    """Each Resort/Hotel is a Tenant"""
    
    PLAN_CHOICES = [
        ('trial', 'Trial'),
        ('basic', 'Basic'),
        ('premium', 'Premium'),
        ('enterprise', 'Enterprise'),
    ]

    # Basic Info
    slug = models.SlugField(unique=True, max_length=50)
    name = models.CharField(max_length=200)
    tagline = models.CharField(max_length=300, blank=True, default="Welcome to our restaurant!")
    logo = models.ImageField(upload_to='tenants/logos/', blank=True, null=True)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    address = models.TextField()
    
    # Branding
    primary_color = models.CharField(max_length=7, default='#FF6B35')
    secondary_color = models.CharField(max_length=7, default='#004E89')
    background_image = models.ImageField(upload_to='tenants/backgrounds/', blank=True, null=True)
    favicon = models.ImageField(upload_to='tenants/favicons/', blank=True, null=True)
    banner_image = models.ImageField(upload_to='tenants/banners/', blank=True, null=True)
    footer_text = models.CharField(max_length=500, blank=True, default='Thank you for dining with us!')
    welcome_message = models.CharField(max_length=300, blank=True, default='Welcome! Scan menu and order.')
    
    # Settings
    tax_percent = models.DecimalField(max_digits=5, decimal_places=2, default=5.00)
    service_charge_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    min_order_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    estimated_prep_time = models.IntegerField(default=20)
    reservation_advance = models.DecimalField(max_digits=10, decimal_places=2, default=100, help_text="Advance amount for table reservation")
    
    # Razorpay
    razorpay_key_id = models.CharField(max_length=100, blank=True, default='')
    razorpay_key_secret = models.CharField(max_length=100, blank=True, default='')
    
    # WhatsApp
    whatsapp_api_token = models.CharField(max_length=500, blank=True, default='')
    whatsapp_phone_number_id = models.CharField(max_length=50, blank=True, default='')
    
    # Subscription
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default='trial')
    plan_expiry = models.DateField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    # Meta
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Tenant"
        verbose_name_plural = "Tenants"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.slug})"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def domain_url(self):
        return f"https://{self.slug}.mecguraserve.com"


class RestaurantTable(models.Model):
    """Tables in the restaurant"""
    
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('occupied', 'Occupied'),
        ('reserved', 'Reserved'),
        ('maintenance', 'Maintenance'),
    ]

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='tables')
    table_number = models.CharField(max_length=10)
    capacity = models.PositiveIntegerField(default=4)
    qr_token = models.UUIDField(default=uuid.uuid4, unique=True)
    location = models.CharField(max_length=100, blank=True, default='')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    
    # Layout position (for floor plan)
    pos_x = models.IntegerField(default=0, help_text="X position on floor plan")
    pos_y = models.IntegerField(default=0, help_text="Y position on floor plan")
    table_shape = models.CharField(max_length=20, default='round', choices=[('round', 'Round'), ('square', 'Square'), ('rectangle', 'Rectangle')])
    
    # Waiter assignment
    assigned_waiter = models.ForeignKey('Staff', on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tables')
    
    # Reservation settings
    accepts_reservations = models.BooleanField(default=True)
    
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Table"
        verbose_name_plural = "Tables"
        unique_together = ['tenant', 'table_number']
        ordering = ['table_number']

    def __str__(self):
        return f"{self.tenant.name} - Table {self.table_number}"

    @property
    def qr_url(self):
        return f"https://{self.tenant.slug}.mecguraserve.com/menu/?table={self.qr_token}"

    @property
    def current_reservation(self):
        return self.reservations.filter(
            status='confirmed',
            reservation_date=timezone.now().date(),
            start_time__lte=timezone.now().time(),
            end_time__gte=timezone.now().time()
        ).first()


class TableReservation(models.Model):
    """Table reservations"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
        ('no_show', 'No Show'),
    ]

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='reservations')
    table = models.ForeignKey(RestaurantTable, on_delete=models.CASCADE, related_name='reservations')
    
    # Customer Info
    customer_name = models.CharField(max_length=100)
    customer_phone = models.CharField(max_length=20)
    customer_email = models.EmailField(blank=True, default='')
    
    # Reservation Details
    reservation_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    party_size = models.PositiveIntegerField(default=2)
    
    # Advance Payment
    advance_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    advance_payment_method = models.CharField(max_length=20, blank=True, default='')
    advance_payment_id = models.CharField(max_length=100, blank=True, default='')
    advance_status = models.CharField(max_length=20, default='pending', choices=[
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('refunded', 'Refunded'),
    ])
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    special_requests = models.TextField(blank=True, default='')
    
    # Meta
    created_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = "Table Reservation"
        verbose_name_plural = "Table Reservations"
        ordering = ['-reservation_date', '-start_time']

    def __str__(self):
        return f"{self.customer_name} - Table {self.table.table_number} on {self.reservation_date}"


class AdvancePayment(models.Model):
    """Manual advance payments"""
    
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('upi', 'UPI'),
        ('razorpay', 'Online'),
    ]

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='advance_payments')
    order = models.ForeignKey('orders.Order', on_delete=models.SET_NULL, null=True, blank=True, related_name='advance_payments')
    reservation = models.ForeignKey(TableReservation, on_delete=models.SET_NULL, null=True, blank=True, related_name='advance_payments')
    
    # Payment Details
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    reference_number = models.CharField(max_length=100, blank=True, default='')
    notes = models.TextField(blank=True, default='')
    
    # Customer Info
    customer_name = models.CharField(max_length=100, blank=True, default='')
    customer_phone = models.CharField(max_length=20, blank=True, default='')
    
    # Staff who recorded
    recorded_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, related_name='recorded_advances')
    
    # Meta
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Advance Payment"
        verbose_name_plural = "Advance Payments"
        ordering = ['-created_at']

    def __str__(self):
        return f"₹{self.amount} - {self.customer_name or 'N/A'} ({self.payment_method})"


class ComplimentaryService(models.Model):
    """Complimentary services offered by resort"""
    
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='complimentary_services')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, default='')
    
    # Value
    value = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Monetary value of service")
    
    # Conditions
    min_order_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Minimum order to get this free")
    max_per_customer = models.PositiveIntegerField(default=1)
    applicable_days = models.JSONField(default=list, blank=True, help_text="Day numbers (0=Sunday) or empty for all")
    
    # Validity
    is_active = models.BooleanField(default=True)
    valid_from = models.DateTimeField(blank=True, null=True)
    valid_until = models.DateTimeField(blank=True, null=True)
    
    # Usage tracking
    used_count = models.PositiveIntegerField(default=0)
    
    # Meta
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Complimentary Service"
        verbose_name_plural = "Complimentary Services"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} - {self.tenant.name}"

    @property
    def is_valid(self):
        now = timezone.now()
        if not self.is_active:
            return False
        if self.valid_from and now < self.valid_from:
            return False
        if self.valid_until and now > self.valid_until:
            return False
        return True


class TableLayout(models.Model):
    """Floor plan layout for the restaurant"""
    
    tenant = models.OneToOneField(Tenant, on_delete=models.CASCADE, related_name='layout')
    name = models.CharField(max_length=100, default='Main Floor')
    width = models.PositiveIntegerField(default=800, help_text="Canvas width in pixels")
    height = models.PositiveIntegerField(default=600, help_text="Canvas height in pixels")
    background_color = models.CharField(max_length=7, default='#f5f5f5')
    
    # Meta
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Table Layout"
        verbose_name_plural = "Table Layouts"

    def __str__(self):
        return f"{self.tenant.name} - {self.name}"


class Staff(models.Model):
    """Staff members (Owner, Manager, Kitchen, Waiter)"""
    
    ROLE_CHOICES = [
        ('owner', 'Owner'),
        ('manager', 'Manager'),
        ('kitchen', 'Kitchen Staff'),
        ('waiter', 'Waiter'),
        ('cashier', 'Cashier'),
    ]

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='staff')
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE, related_name='staff_profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    
    # Profile Details
    photo = models.ImageField(upload_to='staff/photos/', blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, default='')
    address = models.TextField(blank=True, default='')
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=10, blank=True, default='', choices=[
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ])
    
    # Employment Details
    employee_id = models.CharField(max_length=50, blank=True, default='')
    joining_date = models.DateField(blank=True, null=True)
    salary = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    shift_start = models.TimeField(blank=True, null=True)
    shift_end = models.TimeField(blank=True, null=True)
    
    # Emergency Contact
    emergency_contact_name = models.CharField(max_length=100, blank=True, default='')
    emergency_contact_phone = models.CharField(max_length=20, blank=True, default='')
    
    # Documents
    id_proof = models.FileField(upload_to='staff/id_proof/', blank=True, null=True)
    resume = models.FileField(upload_to='staff/resume/', blank=True, null=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Meta
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Staff"
        verbose_name_plural = "Staff"
        unique_together = ['tenant', 'user']

    def __str__(self):
        return f"{self.user.get_full_name} - {self.get_role_display()} @ {self.tenant.name}"
    
    @property
    def full_name(self):
        return self.user.get_full_name or self.user.username
    
    @property
    def photo_url(self):
        if self.photo:
            return self.photo.url
        return '/static/images/default-avatar.png'
