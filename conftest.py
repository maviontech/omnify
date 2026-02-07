"""
Root conftest.py — shared pytest fixtures for the entire Omnify test suite.
"""
import pytest
from apps.core.models import set_current_tenant


@pytest.fixture
def tenant(db):
    """Create a test tenant."""
    from apps.tenants.models import Tenant, TenantConfiguration
    t = Tenant.objects.create(
        name='Test Hospital',
        slug='test-hospital',
        industry='hospital',
        subscription_tier='professional',
    )
    TenantConfiguration.objects.create(
        tenant=t,
        enabled_modules=['items', 'transactions', 'workflows', 'locations', 'reports', 'notifications'],
    )
    return t


@pytest.fixture
def other_tenant(db):
    """Create a second tenant for isolation tests."""
    from apps.tenants.models import Tenant, TenantConfiguration
    t = Tenant.objects.create(
        name='Test Factory',
        slug='test-factory',
        industry='factory',
        subscription_tier='starter',
    )
    TenantConfiguration.objects.create(tenant=t)
    return t


@pytest.fixture
def tenant_context(tenant):
    """Set tenant in thread-local storage for the duration of the test."""
    set_current_tenant(tenant)
    yield tenant
    set_current_tenant(None)


@pytest.fixture
def admin_user(db, tenant):
    """Create an admin user belonging to the test tenant."""
    from apps.users.models import User
    user = User.objects.create_user(
        email='admin@test-hospital.com',
        password='testpass123',
        first_name='Admin',
        last_name='User',
        tenant=tenant,
        is_staff=True,
    )
    return user


@pytest.fixture
def regular_user(db, tenant):
    """Create a regular (non-staff) user belonging to the test tenant."""
    from apps.users.models import User
    user = User.objects.create_user(
        email='user@test-hospital.com',
        password='testpass123',
        first_name='Regular',
        last_name='User',
        tenant=tenant,
    )
    return user


@pytest.fixture
def item_type(db, tenant_context):
    """Create a test item type."""
    from apps.items.models import ItemType
    return ItemType.objects.create(
        tenant=tenant_context,
        name='Medical Equipment',
        description='Trackable medical devices',
        icon='stethoscope',
    )


@pytest.fixture
def location(db, tenant_context):
    """Create a test location."""
    from apps.locations.models import Location
    return Location.objects.create(
        tenant=tenant_context,
        name='Main Warehouse',
        code='MAIN_WH',
        location_type='warehouse',
    )


@pytest.fixture
def item(db, tenant_context, item_type, location):
    """Create a test item."""
    from apps.items.models import Item
    return Item.objects.create(
        tenant=tenant_context,
        item_type=item_type,
        code='MED-001',
        name='Blood Pressure Monitor',
        quantity=10,
        unit='pieces',
        unit_cost=150.00,
        selling_price=250.00,
        status='active',
        location=location,
        reorder_point=3,
    )


@pytest.fixture
def authenticated_client(client, admin_user, tenant):
    """Return a Django test client logged in as admin with tenant context."""
    client.login(email='admin@test-hospital.com', password='testpass123')
    # Set tenant header for TenantMiddleware
    client.defaults['HTTP_X_TENANT_SLUG'] = tenant.slug
    return client
