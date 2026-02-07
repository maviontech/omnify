"""
Tests for item models: ItemType, CustomField, Item, ItemCustomFieldValue.
"""
import pytest
from decimal import Decimal
from apps.items.models import ItemType, CustomField, Item, ItemCustomFieldValue


class TestItemType:
    """Test ItemType model."""

    def test_create_item_type(self, tenant_context):
        it = ItemType.objects.create(
            tenant=tenant_context,
            name='Pharmaceuticals',
            description='Medicines and drugs',
        )
        assert str(it) == 'Pharmaceuticals'
        assert it.is_active is True

    def test_unique_name_per_tenant(self, tenant_context, item_type):
        with pytest.raises(Exception):
            ItemType.objects.create(
                tenant=tenant_context,
                name=item_type.name,  # duplicate within same tenant
            )

    def test_same_name_different_tenants(self, tenant_context, other_tenant):
        ItemType.objects.create(tenant=tenant_context, name='Equipment')
        # Should not raise — different tenant
        it2 = ItemType.objects.create(tenant=other_tenant, name='Equipment')
        assert it2.pk is not None

    def test_hierarchical_item_types(self, tenant_context):
        parent = ItemType.objects.create(tenant=tenant_context, name='Supplies')
        child = ItemType.objects.create(
            tenant=tenant_context, name='Surgical Supplies', parent=parent,
        )
        assert child.parent == parent
        assert parent.children.first() == child


class TestCustomField:
    """Test CustomField model."""

    def test_create_custom_field(self, item_type):
        cf = CustomField.objects.create(
            item_type=item_type,
            name='Serial Number',
            field_type='text',
            is_required=True,
            is_searchable=True,
        )
        assert str(cf) == 'Medical Equipment - Serial Number'

    def test_all_field_types_valid(self, item_type):
        for field_type, _ in CustomField.DATA_TYPES:
            cf = CustomField.objects.create(
                item_type=item_type,
                name=f'Test {field_type}',
                field_type=field_type,
            )
            assert cf.field_type == field_type

    def test_dropdown_options(self, item_type):
        cf = CustomField.objects.create(
            item_type=item_type,
            name='Condition',
            field_type='dropdown',
            dropdown_options=['New', 'Good', 'Fair', 'Poor'],
        )
        assert cf.dropdown_options == ['New', 'Good', 'Fair', 'Poor']


class TestItem:
    """Test Item model."""

    def test_create_item(self, item):
        assert str(item) == 'MED-001 - Blood Pressure Monitor'
        assert item.quantity == Decimal('10')
        assert item.status == 'active'

    def test_unique_code_per_tenant(self, tenant_context, item_type, location):
        Item.objects.create(
            tenant=tenant_context, item_type=item_type,
            code='UNIQUE-001', name='Item 1', location=location,
        )
        with pytest.raises(Exception):
            Item.objects.create(
                tenant=tenant_context, item_type=item_type,
                code='UNIQUE-001', name='Item 2', location=location,
            )

    def test_is_low_stock_true(self, item):
        item.quantity = Decimal('2')
        item.reorder_point = Decimal('3')
        assert item.is_low_stock() is True

    def test_is_low_stock_false(self, item):
        item.quantity = Decimal('10')
        item.reorder_point = Decimal('3')
        assert item.is_low_stock() is False

    def test_is_low_stock_no_reorder_point(self, item):
        item.reorder_point = None
        assert item.is_low_stock() is False

    def test_is_low_stock_at_exact_point(self, item):
        item.quantity = Decimal('3')
        item.reorder_point = Decimal('3')
        assert item.is_low_stock() is True


class TestItemCustomFieldValue:
    """Test ItemCustomFieldValue polymorphic storage."""

    def test_text_value(self, item, item_type):
        cf = CustomField.objects.create(
            item_type=item_type, name='Notes', field_type='text',
        )
        val = ItemCustomFieldValue.objects.create(
            item=item, custom_field=cf, value_text='Test notes',
        )
        assert val.get_value() == 'Test notes'

    def test_number_value(self, item, item_type):
        cf = CustomField.objects.create(
            item_type=item_type, name='Weight', field_type='number',
        )
        val = ItemCustomFieldValue.objects.create(
            item=item, custom_field=cf, value_number=Decimal('5.500'),
        )
        assert val.get_value() == Decimal('5.500')

    def test_boolean_value(self, item, item_type):
        cf = CustomField.objects.create(
            item_type=item_type, name='Hazardous', field_type='boolean',
        )
        val = ItemCustomFieldValue.objects.create(
            item=item, custom_field=cf, value_boolean=True,
        )
        assert val.get_value() is True

    def test_date_value(self, item, item_type):
        from datetime import date
        cf = CustomField.objects.create(
            item_type=item_type, name='Expiry Date', field_type='date',
        )
        val = ItemCustomFieldValue.objects.create(
            item=item, custom_field=cf, value_date=date(2026, 12, 31),
        )
        assert val.get_value() == date(2026, 12, 31)

    def test_dropdown_value(self, item, item_type):
        cf = CustomField.objects.create(
            item_type=item_type, name='Status', field_type='dropdown',
            dropdown_options=['Good', 'Fair', 'Poor'],
        )
        val = ItemCustomFieldValue.objects.create(
            item=item, custom_field=cf, value_json='Good',
        )
        assert val.get_value() == 'Good'

    def test_unique_per_item_and_field(self, item, item_type):
        cf = CustomField.objects.create(
            item_type=item_type, name='Serial', field_type='text',
        )
        ItemCustomFieldValue.objects.create(item=item, custom_field=cf, value_text='SN001')
        with pytest.raises(Exception):
            ItemCustomFieldValue.objects.create(item=item, custom_field=cf, value_text='SN002')
