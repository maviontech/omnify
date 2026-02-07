"""
Views for items app.
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Q, Sum
from apps.core.models import get_current_tenant
from .models import Item, ItemType, CustomField, ItemCustomFieldValue
from apps.locations.models import Location


class ItemListView(LoginRequiredMixin, ListView):
    """List all items."""
    model = Item
    template_name = 'items/item_list.html'
    context_object_name = 'items'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Item.objects.select_related('item_type', 'location').all()
        
        # Search
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(code__icontains=search) |
                Q(name__icontains=search) |
                Q(description__icontains=search)
            )
        
        # Filter by item type
        item_type = self.request.GET.get('item_type')
        if item_type:
            queryset = queryset.filter(item_type_id=item_type)
        
        # Filter by status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # Filter by location
        location = self.request.GET.get('location')
        if location:
            queryset = queryset.filter(location_id=location)
        
        return queryset.order_by('name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['item_types'] = ItemType.objects.filter(is_active=True).order_by('name')
        context['locations'] = Location.objects.filter(is_active=True).order_by('name')
        context['search'] = self.request.GET.get('search', '')
        context['selected_item_type'] = self.request.GET.get('item_type', '')
        context['selected_status'] = self.request.GET.get('status', '')
        context['selected_location'] = self.request.GET.get('location', '')
        
        # Calculate summary stats
        items = self.get_queryset()
        context['total_items'] = items.count()
        context['total_quantity'] = items.aggregate(total=Sum('quantity'))['total'] or 0
        context['low_stock_count'] = sum(1 for item in items if item.is_low_stock())
        
        return context


class ItemDetailView(LoginRequiredMixin, DetailView):
    """Display item details."""
    model = Item
    template_name = 'items/item_detail.html'
    context_object_name = 'item'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get custom field values
        context['custom_values'] = ItemCustomFieldValue.objects.filter(
            item=self.object
        ).select_related('custom_field')
        return context


@login_required
def item_create(request):
    """Create a new item."""
    if request.method == 'POST':
        tenant = get_current_tenant()
        if not tenant:
            messages.error(request, 'No tenant context found.')
            return redirect('item_list')

        # Get form data
        item_type_id = request.POST.get('item_type')
        code = request.POST.get('code')
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        quantity = request.POST.get('quantity', 0)
        unit = request.POST.get('unit', 'pieces')
        unit_cost = request.POST.get('unit_cost') or None
        selling_price = request.POST.get('selling_price') or None
        status = request.POST.get('status', 'active')
        location_id = request.POST.get('location')
        reorder_point = request.POST.get('reorder_point') or None
        reorder_quantity = request.POST.get('reorder_quantity') or None

        # Create item with tenant and created_by
        item = Item.objects.create(
            tenant=tenant,
            item_type_id=item_type_id,
            code=code,
            name=name,
            description=description,
            quantity=quantity,
            unit=unit,
            unit_cost=unit_cost,
            selling_price=selling_price,
            status=status,
            location_id=location_id,
            reorder_point=reorder_point,
            reorder_quantity=reorder_quantity,
            created_by=request.user if request.user.is_authenticated else None,
        )

        messages.success(request, f'Item "{item.name}" created successfully!')
        return redirect('item_detail', pk=item.pk)

    # GET request
    context = {
        'item_types': ItemType.objects.filter(is_active=True).order_by('name'),
        'locations': Location.objects.filter(is_active=True).order_by('name'),
    }
    return render(request, 'items/item_form.html', context)


@login_required
def item_edit(request, pk):
    """Edit an existing item."""
    item = get_object_or_404(Item, pk=pk)

    if request.method == 'POST':
        # Update item
        item.item_type_id = request.POST.get('item_type')
        item.code = request.POST.get('code')
        item.name = request.POST.get('name')
        item.description = request.POST.get('description', '')
        item.quantity = request.POST.get('quantity', 0)
        item.unit = request.POST.get('unit', 'pieces')
        item.unit_cost = request.POST.get('unit_cost') or None
        item.selling_price = request.POST.get('selling_price') or None
        item.status = request.POST.get('status', 'active')
        item.location_id = request.POST.get('location')
        item.reorder_point = request.POST.get('reorder_point') or None
        item.reorder_quantity = request.POST.get('reorder_quantity') or None
        item.save()
        
        messages.success(request, f'Item "{item.name}" updated successfully!')
        return redirect('item_detail', pk=item.pk)
    
    # GET request
    context = {
        'item': item,
        'item_types': ItemType.objects.filter(is_active=True).order_by('name'),
        'locations': Location.objects.filter(is_active=True).order_by('name'),
    }
    return render(request, 'items/item_form.html', context)
