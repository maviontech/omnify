"""
Tests for core models: TenantAwareModel, AuditLog, tenant isolation.
"""
import pytest
from apps.core.models import (
    AuditLog, set_current_tenant, get_current_tenant, TenantManager,
)


class TestTenantContext:
    """Test thread-local tenant context management."""

    def test_set_and_get_tenant(self, tenant):
        set_current_tenant(tenant)
        assert get_current_tenant() == tenant
        set_current_tenant(None)
        assert get_current_tenant() is None

    def test_default_tenant_is_none(self):
        set_current_tenant(None)
        assert get_current_tenant() is None


class TestAuditLog:
    """Test audit log immutability."""

    def test_create_audit_log(self, db, tenant):
        log = AuditLog.objects.create(
            tenant=tenant,
            action='create',
            model_name='Item',
            object_id='test-uuid',
            changes={'name': {'old': None, 'new': 'Test Item'}},
        )
        assert log.pk is not None
        assert log.action == 'create'

    def test_audit_log_cannot_be_modified(self, db, tenant):
        log = AuditLog.objects.create(
            tenant=tenant,
            action='create',
            model_name='Item',
            object_id='test-uuid',
        )
        log.action = 'update'
        with pytest.raises(ValueError, match="cannot be modified"):
            log.save()

    def test_audit_log_cannot_be_deleted(self, db, tenant):
        log = AuditLog.objects.create(
            tenant=tenant,
            action='delete',
            model_name='Item',
            object_id='test-uuid',
        )
        with pytest.raises(ValueError, match="cannot be deleted"):
            log.delete()


class TestTenantIsolation:
    """Test that TenantManager filters queries by current tenant."""

    def test_items_filtered_by_tenant(self, tenant_context, other_tenant, item_type, location):
        from apps.items.models import Item, ItemType
        from apps.locations.models import Location

        # Create item in current tenant (via tenant_context)
        item_a = Item.objects.create(
            tenant=tenant_context,
            item_type=item_type,
            code='A-001',
            name='Item A',
            quantity=5,
            location=location,
        )

        # Create item in other tenant
        other_type = ItemType.objects.create(
            tenant=other_tenant,
            name='Other Type',
        )
        other_loc = Location.objects.create(
            tenant=other_tenant,
            name='Other Location',
            code='OTHER_LOC',
        )
        item_b = Item.objects.create(
            tenant=other_tenant,
            item_type=other_type,
            code='B-001',
            name='Item B',
            quantity=3,
            location=other_loc,
        )

        # Query should only return items for current tenant
        items = list(Item.objects.all())
        assert len(items) == 1
        assert items[0].code == 'A-001'

    def test_locations_filtered_by_tenant(self, tenant_context, other_tenant, location):
        from apps.locations.models import Location

        # Create location in other tenant
        Location.objects.create(
            tenant=other_tenant,
            name='Other Warehouse',
            code='OTHER_WH',
        )

        # Query should only return locations for current tenant
        locations = list(Location.objects.all())
        assert len(locations) == 1
        assert locations[0].name == 'Main Warehouse'
