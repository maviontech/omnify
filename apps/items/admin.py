"""
Admin interface for items app.
"""
from django.contrib import admin
from .models import ItemType, CustomField, Item, ItemCustomFieldValue


class CustomFieldInline(admin.TabularInline):
    """Inline admin for custom fields."""
    model = CustomField
    extra = 1
    fields = ['name', 'field_type', 'is_required', 'is_searchable', 'display_order']


@admin.register(ItemType)
class ItemTypeAdmin(admin.ModelAdmin):
    """Admin interface for ItemType model."""
    
    list_display = ['name', 'parent', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['id', 'created_at']
    inlines = [CustomFieldInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'tenant', 'name', 'description', 'parent', 'icon', 'is_active')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Filter by tenant if not superuser."""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(tenant=request.user.tenant)


@admin.register(CustomField)
class CustomFieldAdmin(admin.ModelAdmin):
    """Admin interface for CustomField model."""
    
    list_display = ['name', 'item_type', 'field_type', 'is_required', 'is_searchable', 'display_order']
    list_filter = ['field_type', 'is_required', 'is_searchable']
    search_fields = ['name', 'item_type__name']
    readonly_fields = ['id']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'item_type', 'name', 'field_type', 'help_text')
        }),
        ('Validation', {
            'fields': ('is_required', 'is_searchable', 'default_value', 'validation_rules', 'dropdown_options')
        }),
        ('Display', {
            'fields': ('display_order',)
        }),
    )


class ItemCustomFieldValueInline(admin.TabularInline):
    """Inline admin for item custom field values."""
    model = ItemCustomFieldValue
    extra = 0
    fields = ['custom_field', 'value_text', 'value_number', 'value_date', 'value_boolean']


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    """Admin interface for Item model."""
    
    list_display = ['code', 'name', 'item_type', 'quantity', 'unit', 'status', 'location', 'created_at']
    list_filter = ['status', 'item_type', 'created_at']
    search_fields = ['code', 'name', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at']
    inlines = [ItemCustomFieldValueInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'tenant', 'item_type', 'code', 'name', 'description', 'status')
        }),
        ('Inventory', {
            'fields': ('quantity', 'unit', 'location')
        }),
        ('Pricing', {
            'fields': ('unit_cost', 'selling_price'),
            'classes': ('collapse',)
        }),
        ('Reorder Management', {
            'fields': ('reorder_point', 'reorder_quantity'),
            'classes': ('collapse',)
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


@admin.register(ItemCustomFieldValue)
class ItemCustomFieldValueAdmin(admin.ModelAdmin):
    """Admin interface for ItemCustomFieldValue model."""
    
    list_display = ['item', 'custom_field', 'get_value']
    search_fields = ['item__code', 'item__name', 'custom_field__name']
    readonly_fields = ['id']
    
    def get_value(self, obj):
        """Display the value based on field type."""
        return obj.get_value()
    get_value.short_description = 'Value'
