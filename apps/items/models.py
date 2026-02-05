"""
Item models for inventory management.
"""
import uuid
from django.db import models
from apps.core.models import TenantAwareModel


class ItemType(TenantAwareModel):
    """Defines a category of items with custom attributes."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='children')
    icon = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'items_item_type'
        unique_together = ['tenant', 'name']
        ordering = ['name']
    
    def __str__(self):
        return self.name


class CustomField(models.Model):
    """Defines a custom field for an item type."""
    
    DATA_TYPES = [
        ('text', 'Text'),
        ('number', 'Number'),
        ('date', 'Date'),
        ('datetime', 'DateTime'),
        ('boolean', 'Boolean'),
        ('dropdown', 'Dropdown'),
        ('multiselect', 'Multi-Select'),
        ('file', 'File Attachment'),
        ('url', 'URL'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    item_type = models.ForeignKey(ItemType, on_delete=models.CASCADE, related_name='custom_fields')
    name = models.CharField(max_length=200)
    field_type = models.CharField(max_length=20, choices=DATA_TYPES)
    is_required = models.BooleanField(default=False)
    is_searchable = models.BooleanField(default=True)
    default_value = models.TextField(blank=True)
    validation_rules = models.JSONField(default=dict, blank=True)
    dropdown_options = models.JSONField(null=True, blank=True)
    display_order = models.IntegerField(default=0)
    help_text = models.TextField(blank=True)
    
    class Meta:
        db_table = 'items_custom_field'
        unique_together = ['item_type', 'name']
        ordering = ['display_order', 'name']
    
    def __str__(self):
        return f"{self.item_type.name} - {self.name}"


class Item(TenantAwareModel):
    """Represents an inventory item."""
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('discontinued', 'Discontinued'),
        ('pending', 'Pending'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE)
    item_type = models.ForeignKey(ItemType, on_delete=models.PROTECT)
    code = models.CharField(max_length=100)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    # Quantity and unit
    quantity = models.DecimalField(max_digits=15, decimal_places=3, default=0)
    unit = models.CharField(max_length=50, default='pieces')
    
    # Pricing
    unit_cost = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    selling_price = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    
    # Status and location
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='active')
    location = models.ForeignKey('locations.Location', on_delete=models.PROTECT)
    
    # Reorder management
    reorder_point = models.DecimalField(max_digits=15, decimal_places=3, null=True, blank=True)
    reorder_quantity = models.DecimalField(max_digits=15, decimal_places=3, null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        db_table = 'items_item'
        unique_together = ['tenant', 'code']
        ordering = ['name']
        indexes = [
            models.Index(fields=['tenant', 'item_type']),
            models.Index(fields=['tenant', 'status']),
            models.Index(fields=['tenant', 'location']),
            models.Index(fields=['tenant', 'code']),
        ]
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    def is_low_stock(self):
        """Check if item is below reorder point."""
        if self.reorder_point:
            return self.quantity <= self.reorder_point
        return False


class ItemCustomFieldValue(models.Model):
    """Stores custom field values for items."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='custom_values')
    custom_field = models.ForeignKey(CustomField, on_delete=models.CASCADE)
    
    # Value storage for different types
    value_text = models.TextField(blank=True)
    value_number = models.DecimalField(max_digits=15, decimal_places=3, null=True, blank=True)
    value_date = models.DateField(null=True, blank=True)
    value_datetime = models.DateTimeField(null=True, blank=True)
    value_boolean = models.BooleanField(null=True, blank=True)
    value_json = models.JSONField(null=True, blank=True)
    
    class Meta:
        db_table = 'items_custom_field_value'
        unique_together = ['item', 'custom_field']
    
    def __str__(self):
        return f"{self.item.code} - {self.custom_field.name}"
    
    def get_value(self):
        """Get the value based on field type."""
        field_type = self.custom_field.field_type
        
        if field_type == 'text' or field_type == 'url':
            return self.value_text
        elif field_type == 'number':
            return self.value_number
        elif field_type == 'date':
            return self.value_date
        elif field_type == 'datetime':
            return self.value_datetime
        elif field_type == 'boolean':
            return self.value_boolean
        elif field_type in ['dropdown', 'multiselect', 'file']:
            return self.value_json
        
        return None
