"""
Admin configuration for tenants app.
"""
from django.contrib import admin
from apps.tenants.models import Tenant, TenantConfiguration


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    """Admin interface for Tenant model."""
    
    list_display = ['name', 'slug', 'industry', 'subscription_tier', 'is_active', 'created_at']
    list_filter = ['industry', 'subscription_tier', 'is_active']
    search_fields = ['name', 'slug']
    readonly_fields = ['id', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'name', 'slug', 'industry')
        }),
        ('Subscription', {
            'fields': ('subscription_tier', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )


@admin.register(TenantConfiguration)
class TenantConfigurationAdmin(admin.ModelAdmin):
    """Admin interface for TenantConfiguration model."""
    
    list_display = ['tenant', 'timezone', 'currency', 'language']
    list_filter = ['timezone', 'currency', 'language']
    search_fields = ['tenant__name']
    
    fieldsets = (
        ('Tenant', {
            'fields': ('tenant',)
        }),
        ('Localization', {
            'fields': ('timezone', 'date_format', 'time_format', 'currency', 'language')
        }),
        ('Branding', {
            'fields': ('logo', 'primary_color', 'secondary_color')
        }),
        ('Features', {
            'fields': ('enable_workflows', 'enable_notifications', 'enable_reports', 'enable_api', 
                      'enable_barcode', 'enable_batch_tracking', 'enable_serial_tracking')
        }),
        ('Limits', {
            'fields': ('max_users', 'max_items', 'max_locations', 'max_storage_mb')
        }),
    )
