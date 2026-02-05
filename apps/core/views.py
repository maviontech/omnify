"""
Core views for Omnify platform.
"""
from django.shortcuts import render
from django.views.generic import TemplateView
from apps.tenants.models import Tenant


class HomeView(TemplateView):
    """Home page view."""
    template_name = 'home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tenants'] = Tenant.objects.filter(is_active=True).order_by('name')
        return context


class DashboardView(TemplateView):
    """Dashboard view for logged-in users."""
    template_name = 'dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if hasattr(self.request, 'tenant'):
            context['tenant'] = self.request.tenant
        return context
