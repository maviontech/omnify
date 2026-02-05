"""
Middleware for multi-tenancy support.
"""
from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from apps.core.models import set_current_tenant
from apps.tenants.models import Tenant


class TenantMiddleware:
    """
    Middleware to set the current tenant based on subdomain or header.
    
    Supports two methods:
    1. Subdomain: tenant-slug.omnify.com
    2. Header: X-Tenant-Slug
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Try to get tenant from subdomain first
        tenant = self._get_tenant_from_subdomain(request)
        
        # If not found, try header
        if not tenant:
            tenant = self._get_tenant_from_header(request)
        
        # If still not found and not accessing admin/api docs, show error
        if not tenant and not self._is_public_path(request.path):
            return HttpResponseForbidden("Tenant not found. Please use a valid subdomain or X-Tenant-Slug header.")
        
        # Set tenant in thread-local storage
        if tenant:
            set_current_tenant(tenant)
            request.tenant = tenant
        
        response = self.get_response(request)
        
        # Clear tenant after request
        set_current_tenant(None)
        
        return response
    
    def _get_tenant_from_subdomain(self, request):
        """Extract tenant from subdomain."""
        host = request.get_host().split(':')[0]  # Remove port
        parts = host.split('.')
        
        # Check if subdomain exists (e.g., tenant.omnify.com)
        if len(parts) >= 2:
            subdomain = parts[0]
            
            # Skip common subdomains
            if subdomain not in ['www', 'api', 'admin', 'localhost', '127']:
                try:
                    return Tenant.objects.get(slug=subdomain, is_active=True)
                except Tenant.DoesNotExist:
                    pass
        
        return None
    
    def _get_tenant_from_header(self, request):
        """Extract tenant from X-Tenant-Slug header."""
        tenant_slug = request.headers.get('X-Tenant-Slug')
        
        if tenant_slug:
            try:
                return Tenant.objects.get(slug=tenant_slug, is_active=True)
            except Tenant.DoesNotExist:
                pass
        
        return None
    
    def _is_public_path(self, path):
        """Check if path is public (doesn't require tenant)."""
        public_paths = [
            '/',
            '/admin/',
            '/api/docs/',
            '/api/schema/',
            '/static/',
            '/media/',
            '/health/',
            '/dashboard/',
        ]
        
        return any(path.startswith(p) for p in public_paths)
