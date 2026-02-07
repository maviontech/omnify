"""
Views for locations app.
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Q, Count
from apps.core.models import get_current_tenant
from .models import Location


class LocationListView(LoginRequiredMixin, ListView):
    """List all locations."""
    model = Location
    template_name = 'locations/location_list.html'
    context_object_name = 'locations'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Location.objects.select_related('parent').all()
        
        # Search
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(code__icontains=search) |
                Q(address__icontains=search) |
                Q(city__icontains=search)
            )
        
        # Filter by location type
        location_type = self.request.GET.get('location_type')
        if location_type:
            queryset = queryset.filter(location_type=location_type)
        
        # Filter by active status
        is_active = self.request.GET.get('is_active')
        if is_active:
            queryset = queryset.filter(is_active=is_active == 'true')
        
        return queryset.order_by('name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['location_types'] = Location.LOCATION_TYPES
        context['search'] = self.request.GET.get('search', '')
        context['selected_location_type'] = self.request.GET.get('location_type', '')
        
        # Calculate summary stats
        locations = self.get_queryset()
        context['total_locations'] = locations.count()
        context['active_locations'] = locations.filter(is_active=True).count()
        
        return context


class LocationDetailView(LoginRequiredMixin, DetailView):
    """Display location details."""
    model = Location
    template_name = 'locations/location_detail.html'
    context_object_name = 'location'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get child locations
        context['children'] = self.object.children.all().order_by('name')
        # Get items in this location
        from apps.items.models import Item
        context['items'] = Item.objects.filter(location=self.object).select_related('item_type')
        context['item_count'] = context['items'].count()
        # Calculate utilization
        context['utilization'] = self.object.calculate_utilization()
        return context


@login_required
def location_create(request):
    """Create a new location."""
    if request.method == 'POST':
        tenant = get_current_tenant()
        if not tenant:
            messages.error(request, 'No tenant context found.')
            return redirect('location_list')

        # Get form data
        name = request.POST.get('name')
        code = request.POST.get('code', '')
        location_type = request.POST.get('location_type', 'other')
        parent_id = request.POST.get('parent') or None
        address = request.POST.get('address', '')
        city = request.POST.get('city', '')
        state = request.POST.get('state', '')
        postal_code = request.POST.get('postal_code', '')
        country = request.POST.get('country', '')
        capacity = request.POST.get('capacity') or None
        capacity_unit = request.POST.get('capacity_unit', 'items')
        is_active = request.POST.get('is_active') == 'on'

        # Create location with tenant and created_by
        location = Location.objects.create(
            tenant=tenant,
            name=name,
            code=code,
            location_type=location_type,
            parent_id=parent_id,
            address=address,
            city=city,
            state=state,
            postal_code=postal_code,
            country=country,
            capacity=capacity,
            capacity_unit=capacity_unit,
            is_active=is_active,
            created_by=request.user if request.user.is_authenticated else None,
        )
        
        messages.success(request, f'Location "{location.name}" created successfully!')
        return redirect('location_detail', pk=location.pk)
    
    # GET request
    context = {
        'location_types': Location.LOCATION_TYPES,
        'locations': Location.objects.filter(is_active=True).order_by('name'),
    }
    return render(request, 'locations/location_form.html', context)


@login_required
def location_edit(request, pk):
    """Edit an existing location."""
    location = get_object_or_404(Location, pk=pk)
    
    if request.method == 'POST':
        # Update location
        location.name = request.POST.get('name')
        location.code = request.POST.get('code', '')
        location.location_type = request.POST.get('location_type', 'other')
        parent_id = request.POST.get('parent') or None
        location.parent_id = parent_id
        location.address = request.POST.get('address', '')
        location.city = request.POST.get('city', '')
        location.state = request.POST.get('state', '')
        location.postal_code = request.POST.get('postal_code', '')
        location.country = request.POST.get('country', '')
        location.capacity = request.POST.get('capacity') or None
        location.capacity_unit = request.POST.get('capacity_unit', 'items')
        location.is_active = request.POST.get('is_active') == 'on'
        location.save()
        
        messages.success(request, f'Location "{location.name}" updated successfully!')
        return redirect('location_detail', pk=location.pk)
    
    # GET request
    context = {
        'location': location,
        'location_types': Location.LOCATION_TYPES,
        'locations': Location.objects.filter(is_active=True).exclude(pk=location.pk).order_by('name'),
    }
    return render(request, 'locations/location_form.html', context)
