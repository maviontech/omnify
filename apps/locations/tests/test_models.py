"""
Tests for location models: hierarchy, capacity, cycle detection.
"""
import pytest
from apps.locations.models import Location


class TestLocation:
    """Test Location model."""

    def test_create_location(self, location):
        assert location.name == 'Main Warehouse'
        assert location.location_type == 'warehouse'
        assert location.is_active is True

    def test_auto_generate_code(self, tenant_context):
        loc = Location.objects.create(
            tenant=tenant_context,
            name='Cold Storage Room',
            location_type='room',
        )
        assert loc.code == 'COLD_STORAGE_ROOM'

    def test_explicit_code_preserved(self, tenant_context):
        loc = Location.objects.create(
            tenant=tenant_context,
            name='Zone A',
            code='ZN-A',
            location_type='zone',
        )
        assert loc.code == 'ZN-A'


class TestLocationHierarchy:
    """Test hierarchical location management."""

    def test_parent_child_relationship(self, tenant_context, location):
        aisle = Location.objects.create(
            tenant=tenant_context,
            name='Aisle 1',
            code='AISLE_1',
            location_type='aisle',
            parent=location,
        )
        assert aisle.parent == location
        assert aisle in location.children.all()

    def test_get_full_path(self, tenant_context, location):
        aisle = Location.objects.create(
            tenant=tenant_context, name='Aisle 1', code='A1',
            location_type='aisle', parent=location,
        )
        shelf = Location.objects.create(
            tenant=tenant_context, name='Shelf B', code='SB',
            location_type='shelf', parent=aisle,
        )
        assert shelf.get_full_path() == 'Main Warehouse > Aisle 1 > Shelf B'

    def test_get_ancestors(self, tenant_context, location):
        aisle = Location.objects.create(
            tenant=tenant_context, name='Aisle 2', code='A2',
            location_type='aisle', parent=location,
        )
        shelf = Location.objects.create(
            tenant=tenant_context, name='Shelf C', code='SC',
            location_type='shelf', parent=aisle,
        )
        ancestors = shelf.get_ancestors()
        assert len(ancestors) == 2
        assert ancestors[0] == aisle
        assert ancestors[1] == location

    def test_get_descendants(self, tenant_context, location):
        aisle = Location.objects.create(
            tenant=tenant_context, name='Aisle 3', code='A3',
            location_type='aisle', parent=location,
        )
        shelf = Location.objects.create(
            tenant=tenant_context, name='Shelf D', code='SD',
            location_type='shelf', parent=aisle,
        )
        descendants = location.get_descendants()
        assert len(descendants) == 2
        assert aisle in descendants
        assert shelf in descendants


class TestLocationCycleDetection:
    """Test that cycles in location hierarchy are prevented."""

    def test_self_referencing_parent_detected(self, tenant_context, location):
        location.parent = location
        assert location.has_cycle() is True

    def test_indirect_cycle_detected(self, tenant_context, location):
        aisle = Location.objects.create(
            tenant=tenant_context, name='Aisle X', code='AX',
            location_type='aisle', parent=location,
        )
        # Try to set location's parent to its own child
        location.parent = aisle
        assert location.has_cycle() is True

    def test_save_prevents_cycle(self, tenant_context, location):
        aisle = Location.objects.create(
            tenant=tenant_context, name='Aisle Y', code='AY',
            location_type='aisle', parent=location,
        )
        location.parent = aisle
        with pytest.raises(ValueError, match="cycle"):
            location.save()

    def test_no_false_positive_cycle(self, tenant_context, location):
        aisle = Location.objects.create(
            tenant=tenant_context, name='Aisle Z', code='AZ',
            location_type='aisle', parent=location,
        )
        assert aisle.has_cycle() is False


class TestLocationCapacity:
    """Test location capacity tracking."""

    def test_utilization_no_capacity(self, location):
        location.capacity = None
        assert location.calculate_utilization() is None

    def test_utilization_with_items(self, tenant_context, location, item):
        location.capacity = 100
        location.save()
        util = location.calculate_utilization()
        # item has quantity 10, capacity 100 = 10%
        assert util == 10.0

    def test_utilization_empty_location(self, tenant_context):
        loc = Location.objects.create(
            tenant=tenant_context, name='Empty Room', code='EMPTY',
            location_type='room', capacity=50,
        )
        assert loc.calculate_utilization() == 0
