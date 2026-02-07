# Developer Implementation Notes: Extensibility Patterns

## Overview

This document provides practical implementation guidance for developers working on Omnify. It covers how to add new modules, configurable limits, custom field types, and other extensible features. Read alongside [EXTENSIBILITY_GUIDELINES.md](EXTENSIBILITY_GUIDELINES.md) which covers the design philosophy.

---

## How to Add a New Module

Modules are the building blocks of Omnify. Each feature area (invoicing, workflows, notifications, etc.) is a "module" that tenants can enable or disable.

### Step 1: Define the Module Identifier

Add the module identifier to the module registry. Module names are lowercase, snake_case strings.

```python
# apps/core/modules.py
AVAILABLE_MODULES = {
    'items': {
        'name': 'Items & Inventory',
        'description': 'Track items, quantities, and locations',
        'default_enabled': True,
        'tier_availability': ['starter', 'professional', 'enterprise'],
        'dependencies': [],  # No dependencies
    },
    'workflows': {
        'name': 'Workflows & State Management',
        'description': 'Define item lifecycle states and transitions',
        'default_enabled': True,
        'tier_availability': ['professional', 'enterprise'],
        'dependencies': ['items'],  # Requires items module
    },
    'invoicing': {
        'name': 'Invoicing',
        'description': 'Generate and manage invoices',
        'default_enabled': False,
        'tier_availability': ['professional', 'enterprise'],
        'dependencies': ['items', 'transactions'],
    },
    # ... add new modules here
}
```

### Step 2: Create the Django App

```bash
python manage.py startapp new_module
# Move to apps/new_module/
```

### Step 3: Add Module Check to Views

```python
# apps/new_module/views.py
from apps.core.decorators import require_module

@require_module('new_module')
def new_module_list(request):
    # View logic - only accessible if module is enabled for tenant
    pass
```

### Step 4: Add Module Check to API

```python
# apps/new_module/api/views.py
from apps.core.permissions import ModuleEnabled

class NewModuleViewSet(viewsets.ModelViewSet):
    permission_classes = [ModuleEnabled('new_module')]
```

### Step 5: Hide UI When Module is Disabled

```html
<!-- In Django templates -->
{% if tenant_config.is_module_enabled 'new_module' %}
  <a href="{% url 'new_module:list' %}">New Module</a>
{% endif %}
```

### Step 6: Register in TenantConfiguration

The `enabled_modules` JSONField on `TenantConfiguration` stores enabled module names as a list. When applying a template, the template's module list populates this field.

---

## How to Add a New Configurable Limit

### Step 1: Add Field to TenantConfiguration

```python
# apps/tenants/models.py
class TenantConfiguration(models.Model):
    # ... existing fields ...
    max_new_limit = models.IntegerField(
        default=100,
        help_text="Maximum allowed for new_feature per tenant"
    )
```

### Step 2: Add Default to Subscription Tiers

```python
# apps/tenants/tier_defaults.py
TIER_DEFAULTS = {
    'starter': {
        'max_new_limit': 100,
        # ...
    },
    'professional': {
        'max_new_limit': 1000,
        # ...
    },
    'enterprise': {
        'max_new_limit': 10000,
        # ...
    },
}
```

### Step 3: Create Validation Helper

```python
# apps/core/validators.py
from django.core.exceptions import ValidationError

def validate_limit(tenant, field_name, current_count):
    """Generic limit validator. Raises ValidationError if limit exceeded."""
    config = tenant.configuration
    max_allowed = getattr(config, field_name)
    if current_count >= max_allowed:
        raise ValidationError(
            f"Limit of {max_allowed} reached for {field_name}. "
            f"Upgrade your plan or contact support."
        )
```

### Step 4: Use in Service/View

```python
def create_something(tenant, data):
    current_count = Something.objects.filter(tenant=tenant).count()
    validate_limit(tenant, 'max_new_limit', current_count)
    # proceed with creation
```

---

## How to Add a New Custom Field Type

Custom fields are stored in the `CustomField` model with a `field_type` choice. To add a new type:

### Step 1: Add to Field Type Choices

```python
# apps/items/models.py
class CustomField(TenantAwareModel):
    FIELD_TYPES = [
        ('text', 'Text'),
        ('number', 'Number'),
        ('date', 'Date'),
        ('datetime', 'Date & Time'),
        ('boolean', 'Yes/No'),
        ('dropdown', 'Dropdown'),
        ('multiselect', 'Multi-Select'),
        ('file', 'File Attachment'),
        ('url', 'URL'),
        ('currency', 'Currency'),       # NEW
        ('email', 'Email Address'),     # NEW
        ('phone', 'Phone Number'),      # NEW
        ('color', 'Color Picker'),      # NEW
    ]
```

### Step 2: Add Storage Column (if needed)

If the new type doesn't fit existing value columns (`value_text`, `value_number`, `value_date`, `value_datetime`, `value_boolean`, `value_json`), add a new column to `ItemCustomFieldValue`. Most types can reuse `value_text` or `value_json`.

### Step 3: Add Validation Logic

```python
# apps/items/services/custom_field_validator.py
class CustomFieldValidator:
    def validate_currency(self, value, field):
        """Validate currency values: must be numeric with max 2 decimal places."""
        try:
            decimal_value = Decimal(str(value))
            if decimal_value.as_tuple().exponent < -2:
                raise ValidationError("Currency values allow max 2 decimal places")
            if decimal_value < 0:
                raise ValidationError("Currency values must be non-negative")
        except InvalidOperation:
            raise ValidationError(f"Invalid currency value: {value}")
```

### Step 4: Add Frontend Rendering

```javascript
// static/js/custom_fields.js
function renderCustomField(field) {
    switch (field.type) {
        case 'currency':
            return `<input type="number" step="0.01" min="0"
                     name="cf_${field.id}" placeholder="0.00">`;
        // ... other types
    }
}
```

---

## How to Add a New Transaction Type Effect

Transaction types can affect inventory in different ways. The `affects_quantity` field uses choices: `increase`, `decrease`, `none`. To add a new effect:

### Step 1: Add to TransactionType Choices

```python
# apps/transactions/models.py
class TransactionType(TenantAwareModel):
    QUANTITY_EFFECTS = [
        ('increase', 'Increase Quantity'),
        ('decrease', 'Decrease Quantity'),
        ('none', 'No Quantity Change'),
        ('transfer', 'Transfer Between Locations'),  # NEW
        ('adjust', 'Adjustment (Can Increase or Decrease)'),  # NEW
    ]
```

### Step 2: Update TransactionProcessor

```python
# apps/transactions/services/processor.py
class TransactionProcessor:
    def process_quantity_change(self, transaction_item, effect_type):
        if effect_type == 'transfer':
            # Decrease at source, increase at destination
            self._decrease_at_location(transaction_item, transaction_item.from_location)
            self._increase_at_location(transaction_item, transaction_item.to_location)
        elif effect_type == 'adjust':
            # Positive quantity = increase, negative = decrease
            if transaction_item.quantity >= 0:
                self._increase_quantity(transaction_item)
            else:
                self._decrease_quantity(transaction_item)
```

---

## How to Add a New Workflow Condition

Workflow transitions can have conditions that must be met before the transition is allowed.

### Step 1: Define Condition Type

```python
# apps/workflows/conditions.py
CONDITION_TYPES = {
    'field_equals': {
        'description': 'A custom field must equal a specific value',
        'params': ['field_name', 'expected_value'],
    },
    'quantity_above': {
        'description': 'Item quantity must be above threshold',
        'params': ['threshold'],
    },
    'approval_required': {
        'description': 'Requires approval from user with specific role',
        'params': ['role_name'],
    },
    'time_elapsed': {
        'description': 'Minimum time must pass since entering current state',
        'params': ['hours'],
    },
}
```

### Step 2: Implement Condition Checker

```python
# apps/workflows/services/condition_checker.py
class ConditionChecker:
    def check(self, condition_type, params, item, user):
        method = getattr(self, f'check_{condition_type}', None)
        if not method:
            raise ValueError(f"Unknown condition type: {condition_type}")
        return method(params, item, user)

    def check_field_equals(self, params, item, user):
        field_value = item.get_custom_field_value(params['field_name'])
        return field_value == params['expected_value']

    def check_quantity_above(self, params, item, user):
        return item.quantity > Decimal(str(params['threshold']))
```

---

## Multi-Tenancy Patterns to Follow

### Always Use TenantAwareModel

Every model that stores tenant-specific data must extend `TenantAwareModel`:

```python
class MyModel(TenantAwareModel):
    # Your fields here
    # tenant FK and TenantManager are automatically included
    pass
```

### Never Query Without Tenant Context

```python
# WRONG - bypasses tenant isolation
items = Item.objects.all()

# RIGHT - TenantManager automatically filters by current tenant
items = Item.objects.all()  # Only works if TenantMiddleware set the tenant

# RIGHT - explicit tenant filter (for background tasks without request context)
items = Item.objects.filter(tenant=tenant)
```

### Background Tasks (Celery)

Celery tasks run outside the request cycle, so there's no TenantMiddleware. Always pass the tenant_id:

```python
@shared_task
def process_report(tenant_id, report_id):
    tenant = Tenant.objects.get(id=tenant_id)
    set_current_tenant(tenant)  # Set thread-local for the task
    try:
        # Now TenantManager filtering works
        report = ReportDefinition.objects.get(id=report_id)
        # ... process
    finally:
        clear_current_tenant()
```

---

## Template JSON Schema Reference

Templates use a standardized JSON structure. See [TEMPLATE_SYSTEM_GUIDE.md](TEMPLATE_SYSTEM_GUIDE.md) for the full schema. Key sections:

```json
{
  "template_id": "uuid",
  "name": "Template Name",
  "version": "1.0.0",
  "industry": "hospital",
  "item_types": [...],
  "workflows": [...],
  "transaction_types": [...],
  "location_hierarchy": {...},
  "roles": [...],
  "modules": { "enabled": [...], "disabled": [...] },
  "configuration": {...},
  "sample_data": [...]
}
```

---

## Testing Conventions

### Property-Based Tests (Hypothesis)

Use for universal properties that must hold for all inputs:

```python
from hypothesis import given, strategies as st

@given(st.text(min_size=1, max_size=50))
def test_item_code_uniqueness(code):
    """Property: No two items in the same tenant can have the same code."""
    # Create item with code in tenant A - should succeed
    # Create item with same code in tenant A - should fail
    # Create item with same code in tenant B - should succeed
```

### Unit Tests (pytest)

Use for specific scenarios and edge cases:

```python
def test_transaction_prevents_negative_inventory():
    """An item with quantity 5 cannot have 10 units withdrawn."""
    item = create_item(quantity=5)
    with pytest.raises(InsufficientQuantityError):
        process_transaction(item, quantity=-10)
```

### Test File Organization

```
apps/
  items/
    tests/
      __init__.py
      test_models.py          # Model unit tests
      test_services.py        # Service layer tests
      test_views.py            # View tests
      test_api.py              # API endpoint tests
      test_properties.py       # Property-based tests
      conftest.py              # Fixtures for this app
```

---

## Performance Patterns

### Use select_related for FK Traversals

```python
# WRONG - N+1 query problem
items = Item.objects.all()
for item in items:
    print(item.item_type.name)  # Separate query per item

# RIGHT
items = Item.objects.select_related('item_type', 'location', 'created_by')
```

### Use prefetch_related for Reverse Relations

```python
# WRONG - N+1
item_types = ItemType.objects.all()
for it in item_types:
    print(it.custom_fields.count())  # Separate query per type

# RIGHT
item_types = ItemType.objects.prefetch_related('custom_fields')
```

### Cache Tenant Configuration

```python
from django.core.cache import cache

def get_tenant_config(tenant):
    cache_key = f'tenant_config:{tenant.id}'
    config = cache.get(cache_key)
    if not config:
        config = TenantConfiguration.objects.get(tenant=tenant)
        cache.set(cache_key, config, timeout=900)  # 15 minutes
    return config
```

---

## Common Pitfalls

1. **Forgetting tenant context in Celery tasks** — Always pass `tenant_id` and set thread-local
2. **Hardcoding limits** — Always use TenantConfiguration fields
3. **Skipping module checks** — Always use `@require_module` decorator on views
4. **Direct model queries in views** — Always go through service layer for business logic
5. **Not using database transactions** — Wrap multi-model operations in `transaction.atomic()`
6. **Circular imports** — Use string references for FK relationships across apps
7. **Missing indexes** — Add `class Meta: indexes` for common query patterns
8. **Not invalidating cache** — Use signals or explicit invalidation when data changes
