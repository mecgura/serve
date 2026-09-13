"""
MecGuraServe - Menu Models
"""

from django.db import models


class MenuCategory(models.Model):
    """Menu Categories (Starters, Main Course, Drinks, etc.)"""
    
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='menu_categories')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, default='')
    image = models.ImageField(upload_to='menu/categories/', blank=True, null=True)
    sort_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Menu Category"
        verbose_name_plural = "Menu Categories"
        ordering = ['sort_order', 'name']
        unique_together = ['tenant', 'name']

    def __str__(self):
        return f"{self.name} - {self.tenant.name}"


class MenuItem(models.Model):
    """Individual Menu Items"""
    
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='menu_items')
    category = models.ForeignKey(MenuCategory, on_delete=models.CASCADE, related_name='items')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, default='')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='menu/items/', blank=True, null=True)
    
    # Flags
    is_available = models.BooleanField(default=True)
    is_vegetarian = models.BooleanField(default=False)
    is_vegan = models.BooleanField(default=False)
    is_gluten_free = models.BooleanField(default=False)
    is_bestseller = models.BooleanField(default=False)
    is_spicy = models.BooleanField(default=False)
    is_new = models.BooleanField(default=False)
    
    # Prep time for this specific item
    prep_time = models.IntegerField(default=15, help_text="Preparation time in minutes")
    
    # Sort order
    sort_order = models.IntegerField(default=0)
    
    # Meta
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Menu Item"
        verbose_name_plural = "Menu Items"
        ordering = ['sort_order', 'name']
        unique_together = ['tenant', 'name']

    def __str__(self):
        return f"{self.name} - ₹{self.price} ({self.tenant.name})"


class MenuCustomization(models.Model):
    """Item Customizations (e.g., Spice Level, Extra Cheese)"""
    
    item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, related_name='customizations')
    name = models.CharField(max_length=100)  # e.g., "Spice Level", "Extra Cheese"
    options = models.JSONField(default=list)  # e.g., ["Mild", "Medium", "Spicy", "Extra Spicy"]
    price_modifier = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Extra charge
    is_required = models.BooleanField(default=False)
    max_selections = models.IntegerField(default=1)

    class Meta:
        verbose_name = "Menu Customization"
        verbose_name_plural = "Menu Customizations"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} for {self.item.name}"
