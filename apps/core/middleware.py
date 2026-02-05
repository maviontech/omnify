"""
Core middleware for audit logging and other utilities.
"""
from django.utils.deprecation import MiddlewareMixin
from apps.core.models import AuditLog, get_current_tenant


class AuditLogMiddleware(MiddlewareMixin):
    """
    Middleware to automatically log model changes.
    
    Note: This is a simplified version. In production, you'd want to use
    Django signals or a more sophisticated approach.
    """
    
    def process_request(self, request):
        """Store request info for audit logging."""
        request.audit_info = {
            'ip_address': self._get_client_ip(request),
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
        }
        return None
    
    def _get_client_ip(self, request):
        """Get client IP address from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    @staticmethod
    def log_action(user, action, model_name, object_id, changes=None):
        """
        Create an audit log entry.
        
        Args:
            user: User performing the action
            action: Action type (create, update, delete)
            model_name: Name of the model
            object_id: ID of the object
            changes: Dictionary of changes (before/after)
        """
        tenant = get_current_tenant()
        
        AuditLog.objects.create(
            tenant=tenant,
            user=user,
            action=action,
            model_name=model_name,
            object_id=str(object_id),
            changes=changes or {},
        )
