"""
Location models for hierarchical location management.
"""
import uuid
from django.db import models
from apps.core.models import TenantAwareModel


class Location(TenantAwareModel):
    """Represents a physical or logical storage location."""
    
    LOCATION_TYPES = [
        ('warehouse', 'Warehouse'),
        ('building', 'Building'),
        ('floor', 'Floor'),
        ('room', 'Room'),
        ('aisle', 'Aisle'),
        ('shelf', 'Shelf'),
        ('bin', 'Bin'),
        ('zone', 'Zone'),
        ('other', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50, blank=True)
    location_type = models.CharField(max_length=50, choices=LOCATION_TYPES, default='other')
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='children')
    
    # Address information
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, blank=True)
    
    # Coordinates
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    # Capacity
    capacity = models.DecimalField(max_digits=15, decimal_places=3, null=True, blank=True)
    capacity_unit = models.CharField(max_length=50, default='items')
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        db_table = 'locations_location'
        unique_together = ['tenant', 'code']
        ordering = ['name']
        indexes = [
            models.Index(fields=['tenant', 'parent']),
            models.Index(fields=['tenant', 'is_active']),
            models.Index(fields=['tenant', 'location_type']),
        ]
    
    def __str__(self):
        return self.get_full_path()
    
    def get_full_path(self):
        """Return complete location path (e.g., 'Warehouse A > Aisle 3 > Shelf B')."""
        path = [self.name]
        current = self.parent
        
        while current:
            path.insert(0, current.name)
            current = current.parent
        
        return ' > '.join(path)
    
    def get_ancestors(self):
        """Get all ancestor locations."""
        ancestors = []
        current = self.parent
        
        while current:
            ancestors.append(current)
            current = current.parent
        
        return ancestors
    
    def get_descendants(self):
        """Get all descendant locations."""
        descendants = []
        
        def collect_children(location):
            for child in location.children.all():
                descendants.append(child)
                collect_children(child)
        
        collect_children(self)
        return descendants
    
    def has_cycle(self):
        """Check if setting this parent would create a cycle."""
        if not self.parent:
            return False
        
        visited = set()
        current = self.parent
        
        while current:
            if current.id in visited or current.id == self.id:
                return True
            visited.add(current.id)
            current = current.parent
        
        return False
    
    def calculate_utilization(self):
        """Calculate current capacity utilization."""
        if not self.capacity:
            return None
        
        # Count items in this location
        from apps.items.models import Item
        total_quantity = Item.objects.filter(
            tenant=self.tenant,
            location=self
        ).aggregate(
            total=models.Sum('quantity')
        )['total'] or 0
        
        if self.capacity > 0:
            return (float(total_quantity) / float(self.capacity)) * 100
        return 0
    
    def save(self, *args, **kwargs):
        """Override save to prevent cycles."""
        if self.parent and self.has_cycle():
            raise ValueError("Cannot set parent: would create a cycle in location hierarchy")
        
        # Auto-generate code if not provided
        if not self.code:
            self.code = self.name.upper().replace(' ', '_')[:50]
        
        super().save(*args, **kwargs)
