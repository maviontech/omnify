"""
Admin interface for locations app.
"""
from django.contrib import admin
from .models import Location


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    """Admin interface for Location model."""
    
    list_display = ['name', 'code', 'location_type', 'parent', 'is_active', 'capacity', 'created_at']
    list_filter = ['location_type', 'is_active', 'created_at']
    search_fields = ['name', 'code', 'address', 'city']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'tenant', 'name', 'code', 'location_type', 'parent', 'is_active')
        }),
        ('Address', {
            'fields': ('address', 'city', 'state', 'postal_code', 'country', 'latitude', 'longitude'),
            'classes': ('collapse',)
        }),
        ('Capacity', {
            'fields': ('capacity', 'capacity_unit'),
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Filter by tenant if not superuser."""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(tenant=request.user.tenant)
