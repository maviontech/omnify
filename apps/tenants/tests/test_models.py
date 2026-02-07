"""
Tests for tenant models.
"""
import pytest
from apps.tenants.models import Tenant, TenantConfiguration


class TestTenant:
    """Test Tenant model."""

    def test_create_tenant(self, db):
        t = Tenant.objects.create(name='Test Org', slug='test-org', industry='hospital')
        assert t.pk is not None
        assert str(t) == 'Test Org'
        assert t.is_active is True
        assert t.subscription_tier == 'starter'

    def test_auto_slug_from_name(self, db):
        t = Tenant(name='My Great Hospital')
        t.save()
        assert t.slug == 'my-great-hospital'

    def test_slug_uniqueness(self, db):
        Tenant.objects.create(name='Org A', slug='org-a')
        with pytest.raises(Exception):
            Tenant.objects.create(name='Org A Duplicate', slug='org-a')

    def test_industry_choices(self, db):
        for industry, _ in Tenant.INDUSTRY_CHOICES:
            t = Tenant.objects.create(name=f'{industry} org', slug=f'{industry}-org', industry=industry)
            assert t.industry == industry


class TestTenantConfiguration:
    """Test TenantConfiguration model."""

    def test_create_configuration(self, tenant):
        config = tenant.configuration
        assert config.currency == 'USD'
        assert config.timezone == 'UTC'
        assert config.primary_color == '#0066FF'

    def test_default_limits(self, tenant):
        config = tenant.configuration
        assert config.max_users == 10
        assert config.max_items == 1000
        assert config.max_locations == 50

    def test_enabled_modules_default_empty(self, db):
        t = Tenant.objects.create(name='Bare Tenant', slug='bare')
        config = TenantConfiguration.objects.create(tenant=t)
        assert config.enabled_modules == []

    def test_is_module_enabled(self, tenant):
        config = tenant.configuration
        assert config.is_module_enabled('items') is True
        assert config.is_module_enabled('invoicing') is False

    def test_enabled_modules_stored_as_list(self, tenant):
        config = tenant.configuration
        config.enabled_modules = ['items', 'workflows', 'invoicing']
        config.save()
        config.refresh_from_db()
        assert 'invoicing' in config.enabled_modules
        assert config.is_module_enabled('invoicing') is True
