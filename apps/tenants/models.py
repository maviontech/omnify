"""
Tenant models for multi-tenancy support.
"""
import uuid
from django.db import models
from django.utils.text import slugify


class Tenant(models.Model):
    """Represents an organization using the platform."""
    
    SUBSCRIPTION_TIERS = [
        ('starter', 'Starter'),
        ('professional', 'Professional'),
        ('enterprise', 'Enterprise'),
    ]
    
    INDUSTRY_CHOICES = [
        ('hospital', 'Hospital'),
        ('factory', 'Factory'),
        ('clinic', 'Clinic'),
        ('library', 'Library'),
        ('school', 'School'),
        ('retail', 'Retail'),
        ('restaurant', 'Restaurant'),
        ('construction', 'Construction'),
        ('warehouse', 'Warehouse'),
        ('other', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, max_length=255)
    industry = models.CharField(max_length=50, choices=INDUSTRY_CHOICES, default='other')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    subscription_tier = models.CharField(max_length=50, choices=SUBSCRIPTION_TIERS, default='starter')
    
    class Meta:
        db_table = 'tenants_tenant'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        """Auto-generate slug from name if not provided."""
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class TenantConfiguration(models.Model):
    """Tenant-specific configuration settings."""
    
    tenant = models.OneToOneField(Tenant, on_delete=models.CASCADE, related_name='configuration')
    timezone = models.CharField(max_length=50, default='UTC')
    date_format = models.CharField(max_length=20, default='YYYY-MM-DD')
    time_format = models.CharField(max_length=20, default='HH:mm:ss')
    currency = models.CharField(max_length=3, default='USD')
    language = models.CharField(max_length=10, default='en')
    
    # Branding
    logo = models.ImageField(upload_to='tenant_logos/', null=True, blank=True)
    primary_color = models.CharField(max_length=7, default='#0066FF')  # Omnify Blue
    secondary_color = models.CharField(max_length=7, default='#1A1A2E')  # Omnify Dark
    
    # Features enabled (individual flags for core features)
    enable_workflows = models.BooleanField(default=True)
    enable_notifications = models.BooleanField(default=True)
    enable_reports = models.BooleanField(default=True)
    enable_api = models.BooleanField(default=True)
    enable_barcode = models.BooleanField(default=False)
    enable_batch_tracking = models.BooleanField(default=False)
    enable_serial_tracking = models.BooleanField(default=False)

    # Extensible module system (for template-driven configuration)
    enabled_modules = models.JSONField(
        default=list,
        blank=True,
        help_text="List of enabled module identifiers, e.g. ['items', 'transactions', 'workflows']"
    )

    # Limits (configurable per subscription tier)
    max_users = models.IntegerField(default=10)
    max_items = models.IntegerField(default=1000)
    max_locations = models.IntegerField(default=50)
    max_storage_mb = models.IntegerField(default=1000)  # 1GB
    max_item_type_depth = models.IntegerField(default=10)
    max_location_depth = models.IntegerField(default=15)
    max_bulk_operation_size = models.IntegerField(default=1000)
    max_import_rows = models.IntegerField(default=100000)
    max_file_upload_mb = models.IntegerField(default=10)

    class Meta:
        db_table = 'tenants_configuration'

    def __str__(self):
        return f"Configuration for {self.tenant.name}"

    def is_module_enabled(self, module_name):
        """Check if a specific module is enabled for this tenant."""
        return module_name in self.enabled_modules
