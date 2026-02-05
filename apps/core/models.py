"""
Core models for Omnify platform.
Provides base classes and utilities for multi-tenancy.
"""
import uuid
import threading
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

# Thread-local storage for current tenant
_thread_locals = threading.local()


def get_current_tenant():
    """Get the current tenant from thread-local storage."""
    return getattr(_thread_locals, 'tenant', None)


def set_current_tenant(tenant):
    """Set the current tenant in thread-local storage."""
    _thread_locals.tenant = tenant


class TenantManager(models.Manager):
    """Custom manager that automatically filters by current tenant."""
    
    def get_queryset(self):
        """Override to filter by current tenant."""
        queryset = super().get_queryset()
        tenant = get_current_tenant()
        if tenant and hasattr(self.model, 'tenant'):
            return queryset.filter(tenant=tenant)
        return queryset


class TenantAwareModel(models.Model):
    """Abstract base model for tenant-aware models."""
    
    # Use custom manager
    objects = TenantManager()
    
    class Meta:
        abstract = True


class AuditLog(models.Model):
    """Immutable audit log for all changes."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=50)  # create, update, delete
    model_name = models.CharField(max_length=100)
    object_id = models.CharField(max_length=100)
    changes = models.JSONField(default=dict)  # Before/after values
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'core_audit_log'
        indexes = [
            models.Index(fields=['tenant', 'created_at']),
            models.Index(fields=['tenant', 'model_name', 'object_id']),
            models.Index(fields=['tenant', 'user']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.action} {self.model_name} {self.object_id}"
    
    def save(self, *args, **kwargs):
        """Override save to make audit logs immutable after creation."""
        if self.pk:
            raise ValueError("Audit logs cannot be modified after creation")
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        """Override delete to prevent deletion of audit logs."""
        raise ValueError("Audit logs cannot be deleted")


class FileAttachment(models.Model):
    """Generic file attachment model."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE)
    uploaded_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True)
    file = models.FileField(upload_to='attachments/%Y/%m/%d/')
    filename = models.CharField(max_length=255)
    file_size = models.BigIntegerField()
    content_type = models.CharField(max_length=100)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    # Generic foreign key for attaching to any model
    content_type_fk = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField()
    content_object = GenericForeignKey('content_type_fk', 'object_id')
    
    class Meta:
        db_table = 'core_file_attachment'
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return self.filename
