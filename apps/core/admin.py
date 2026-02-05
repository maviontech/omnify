"""
Admin configuration for core app.
"""
from django.contrib import admin
from apps.core.models import AuditLog, FileAttachment


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """Admin interface for AuditLog model."""
    
    list_display = ['action', 'model_name', 'object_id', 'user', 'tenant', 'created_at']
    list_filter = ['action', 'model_name', 'created_at', 'tenant']
    search_fields = ['model_name', 'object_id', 'user__email']
    readonly_fields = ['id', 'tenant', 'user', 'action', 'model_name', 'object_id', 
                      'changes', 'ip_address', 'user_agent', 'created_at']
    
    def has_add_permission(self, request):
        """Prevent manual creation of audit logs."""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Prevent deletion of audit logs."""
        return False
    
    fieldsets = (
        ('Action', {
            'fields': ('id', 'action', 'model_name', 'object_id')
        }),
        ('User Info', {
            'fields': ('tenant', 'user')
        }),
        ('Changes', {
            'fields': ('changes',)
        }),
        ('Client Info', {
            'fields': ('ip_address', 'user_agent')
        }),
        ('Timestamp', {
            'fields': ('created_at',)
        }),
    )


@admin.register(FileAttachment)
class FileAttachmentAdmin(admin.ModelAdmin):
    """Admin interface for FileAttachment model."""
    
    list_display = ['filename', 'tenant', 'uploaded_by', 'file_size', 'uploaded_at']
    list_filter = ['uploaded_at', 'tenant']
    search_fields = ['filename', 'uploaded_by__email']
    readonly_fields = ['id', 'file_size', 'uploaded_at']
    
    fieldsets = (
        ('File Info', {
            'fields': ('id', 'filename', 'file', 'file_size', 'content_type')
        }),
        ('Tenant & User', {
            'fields': ('tenant', 'uploaded_by')
        }),
        ('Attached To', {
            'fields': ('content_type_fk', 'object_id')
        }),
        ('Timestamp', {
            'fields': ('uploaded_at',)
        }),
    )
