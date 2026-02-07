# Template System Implementation Specification

## Overview

The Template System is Omnify's core differentiator — it enables a single platform to serve any industry by pre-configuring the platform for specific use cases. When a tenant signs up and selects "Hospital", the platform instantly provisions item types (Medical Equipment, Pharmaceuticals), workflows (Equipment Lifecycle), transaction types (Issue to Department, Return), location hierarchies, roles, and module settings.

This document covers the implementation-level specification: database models, the template engine, the application process, seed templates, versioning, and the template builder UI. For the conceptual guide, see [TEMPLATE_SYSTEM_GUIDE.md](TEMPLATE_SYSTEM_GUIDE.md).

---

## 1. Database Models

### 1.1 TemplateCategory

Groups templates by industry for the selection UI.

```python
class TemplateCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)    # CSS class or emoji
    display_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['display_order', 'name']
```

### 1.2 Template

The core template model storing the full configuration as JSON.

```python
class Template(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    category = models.ForeignKey(TemplateCategory, on_delete=models.SET_NULL, null=True)

    # Template configuration (the core payload)
    configuration = models.JSONField(
        help_text="Full template configuration: item_types, workflows, "
                  "transaction_types, locations, roles, modules, settings"
    )

    # Metadata
    version = models.CharField(max_length=20, default='1.0.0')
    status = models.CharField(
        max_length=20,
        choices=[
            ('draft', 'Draft'),
            ('active', 'Active'),
            ('deprecated', 'Deprecated'),
        ],
        default='draft'
    )

    # Usage tracking
    usage_count = models.IntegerField(default=0)

    # Thumbnail/preview
    preview_image = models.ImageField(upload_to='templates/previews/', null=True, blank=True)

    # Authorship
    created_by = models.ForeignKey(
        'users.User', on_delete=models.SET_NULL, null=True, blank=True
    )
    is_system_template = models.BooleanField(default=False)  # Built-in vs user-created

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-usage_count', 'name']
```

### 1.3 TemplateApplication

Tracks which templates have been applied to which tenants.

```python
class TemplateApplication(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    template = models.ForeignKey(Template, on_delete=models.CASCADE)
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE)
    template_version = models.CharField(max_length=20)
    applied_at = models.DateTimeField(auto_now_add=True)
    applied_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True)

    # Track what was customized after application
    customizations_made = models.JSONField(default=dict, blank=True)

    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('applied', 'Applied'),
            ('customized', 'Customized'),
            ('reverted', 'Reverted'),
        ],
        default='applied'
    )

    class Meta:
        ordering = ['-applied_at']
```

---

## 2. Template JSON Schema

The `configuration` JSONField stores the complete template payload. Here is the canonical schema:

```json
{
  "$schema": "omnify-template-v1",
  "metadata": {
    "name": "Hospital & Healthcare",
    "version": "1.0.0",
    "description": "Complete hospital operations management",
    "industry": "hospital",
    "author": "Omnify Team"
  },

  "item_types": [
    {
      "name": "Medical Equipment",
      "description": "Trackable medical devices and equipment",
      "icon": "stethoscope",
      "parent": null,
      "custom_fields": [
        {
          "name": "Serial Number",
          "field_type": "text",
          "is_required": true,
          "is_searchable": true,
          "help_text": "Manufacturer serial number",
          "validation_rules": { "min_length": 3, "max_length": 50 }
        },
        {
          "name": "Manufacturer",
          "field_type": "text",
          "is_required": true,
          "is_searchable": true
        },
        {
          "name": "Calibration Date",
          "field_type": "date",
          "is_required": false,
          "help_text": "Next calibration due date"
        },
        {
          "name": "Department",
          "field_type": "dropdown",
          "is_required": true,
          "dropdown_options": ["Emergency", "ICU", "Surgery", "Radiology", "General Ward"]
        },
        {
          "name": "Condition",
          "field_type": "dropdown",
          "is_required": true,
          "dropdown_options": ["New", "Good", "Fair", "Needs Repair", "Out of Service"],
          "default_value": "New"
        }
      ]
    }
  ],

  "workflows": [
    {
      "name": "Equipment Lifecycle",
      "description": "Track equipment from availability through maintenance",
      "item_type": "Medical Equipment",
      "states": [
        { "name": "Available", "is_initial": true, "is_final": false, "color": "#00C853" },
        { "name": "In Use", "is_initial": false, "is_final": false, "color": "#2196F3" },
        { "name": "Maintenance", "is_initial": false, "is_final": false, "color": "#FF9800" },
        { "name": "Calibration", "is_initial": false, "is_final": false, "color": "#9C27B0" },
        { "name": "Out of Service", "is_initial": false, "is_final": true, "color": "#F44336" }
      ],
      "transitions": [
        {
          "name": "Issue",
          "from_state": "Available",
          "to_state": "In Use",
          "allowed_roles": ["Equipment Manager", "Department Head"]
        },
        {
          "name": "Return",
          "from_state": "In Use",
          "to_state": "Available",
          "allowed_roles": ["Equipment Manager", "Department Head"]
        },
        {
          "name": "Send for Maintenance",
          "from_state": "In Use",
          "to_state": "Maintenance",
          "allowed_roles": ["Equipment Manager"]
        },
        {
          "name": "Complete Maintenance",
          "from_state": "Maintenance",
          "to_state": "Available",
          "allowed_roles": ["Maintenance Technician"]
        },
        {
          "name": "Send for Calibration",
          "from_state": "Available",
          "to_state": "Calibration",
          "allowed_roles": ["Equipment Manager"]
        },
        {
          "name": "Complete Calibration",
          "from_state": "Calibration",
          "to_state": "Available",
          "allowed_roles": ["Equipment Manager"]
        },
        {
          "name": "Retire",
          "from_state": "Available",
          "to_state": "Out of Service",
          "allowed_roles": ["Equipment Manager"]
        }
      ]
    }
  ],

  "transaction_types": [
    {
      "name": "Issue to Department",
      "description": "Issue equipment or supplies to a department",
      "affects_quantity": "decrease",
      "requires_approval": false
    },
    {
      "name": "Return from Department",
      "description": "Return equipment or supplies from a department",
      "affects_quantity": "increase",
      "requires_approval": false
    },
    {
      "name": "Receive from Supplier",
      "description": "Receive new inventory from supplier",
      "affects_quantity": "increase",
      "requires_approval": true
    },
    {
      "name": "Dispose / Retire",
      "description": "Remove item from active inventory",
      "affects_quantity": "decrease",
      "requires_approval": true
    }
  ],

  "location_hierarchy": {
    "name": "Main Hospital",
    "type": "building",
    "children": [
      {
        "name": "Emergency Department",
        "type": "floor",
        "children": [
          { "name": "ED Storage", "type": "room" }
        ]
      },
      {
        "name": "ICU",
        "type": "floor",
        "children": [
          { "name": "ICU Equipment Room", "type": "room" }
        ]
      },
      {
        "name": "Surgery",
        "type": "floor",
        "children": [
          { "name": "OR Equipment Storage", "type": "room" },
          { "name": "Instrument Sterilization", "type": "room" }
        ]
      },
      {
        "name": "Pharmacy",
        "type": "room",
        "children": [
          { "name": "Controlled Substances Cabinet", "type": "shelf" },
          { "name": "General Medications", "type": "shelf" },
          { "name": "Refrigerated Storage", "type": "shelf" }
        ]
      },
      {
        "name": "Central Equipment Storage",
        "type": "warehouse",
        "children": [
          { "name": "Medical Devices", "type": "aisle" },
          { "name": "Surgical Instruments", "type": "aisle" },
          { "name": "Supplies", "type": "aisle" }
        ]
      }
    ]
  },

  "roles": [
    {
      "name": "Equipment Manager",
      "description": "Full control over equipment and inventory",
      "permissions": ["items.*", "transactions.*", "workflows.*", "locations.*", "reports.view"]
    },
    {
      "name": "Department Head",
      "description": "View and request items for their department",
      "permissions": ["items.view", "items.create", "transactions.create", "workflows.execute"]
    },
    {
      "name": "Pharmacist",
      "description": "Manage pharmaceutical inventory",
      "permissions": ["items.view", "items.edit", "transactions.create", "transactions.view"]
    },
    {
      "name": "Maintenance Technician",
      "description": "Handle equipment maintenance and calibration",
      "permissions": ["items.view", "workflows.execute", "transactions.view"]
    },
    {
      "name": "Viewer",
      "description": "Read-only access to inventory data",
      "permissions": ["items.view", "locations.view", "reports.view"]
    }
  ],

  "modules": {
    "enabled": [
      "items", "transactions", "workflows", "locations",
      "reports", "notifications"
    ],
    "disabled": [
      "invoicing", "payments", "purchase_orders", "sales_orders",
      "financial_reports"
    ]
  },

  "configuration": {
    "currency": "USD",
    "date_format": "YYYY-MM-DD",
    "timezone": "America/New_York",
    "low_stock_threshold": 10,
    "enable_barcode": true,
    "require_approval_for_high_value": true,
    "high_value_threshold": 5000
  },

  "sample_data": []
}
```

### 2.1 Schema Validation

Before applying a template, validate the JSON against the schema:

```python
REQUIRED_SECTIONS = ['metadata', 'item_types', 'modules']
OPTIONAL_SECTIONS = [
    'workflows', 'transaction_types', 'location_hierarchy',
    'roles', 'configuration', 'sample_data'
]

VALID_FIELD_TYPES = [
    'text', 'number', 'date', 'datetime', 'boolean',
    'dropdown', 'multiselect', 'file', 'url'
]

VALID_QUANTITY_EFFECTS = ['increase', 'decrease', 'none']

VALID_LOCATION_TYPES = [
    'warehouse', 'building', 'floor', 'room',
    'aisle', 'shelf', 'bin', 'zone', 'other'
]
```

Validation checks:
1. All required sections present
2. Each item_type has a `name` and valid `custom_fields`
3. Each custom_field has valid `field_type`
4. Workflow states have exactly one `is_initial: true`
5. Workflow transitions reference existing states
6. Transaction type `affects_quantity` is valid
7. Location types are valid
8. Module names are recognized

---

## 3. Template Engine

### 3.1 TemplateEngine Service

The core service that validates and applies templates to tenants.

```python
class TemplateEngine:
    """
    Validates template configurations and applies them to tenants.

    Usage:
        engine = TemplateEngine()
        errors = engine.validate(template_json)
        if not errors:
            engine.apply(tenant, template)
    """

    def validate(self, configuration: dict) -> list[str]:
        """
        Validate a template configuration JSON.
        Returns list of error messages (empty = valid).
        """
        errors = []
        # Check required sections
        # Validate item types and custom fields
        # Validate workflows (states, transitions)
        # Validate transaction types
        # Validate location hierarchy (no cycles, valid types)
        # Validate role permissions format
        # Validate module names
        return errors

    def apply(self, tenant, template, applied_by=None):
        """
        Apply a template to a tenant. Creates all configured entities.
        Runs inside a database transaction for atomicity.
        """
        with transaction.atomic():
            config = template.configuration

            # 1. Create Item Types with Custom Fields
            item_type_map = self._create_item_types(tenant, config.get('item_types', []))

            # 2. Create Workflows with States and Transitions
            self._create_workflows(tenant, config.get('workflows', []), item_type_map)

            # 3. Create Transaction Types
            self._create_transaction_types(tenant, config.get('transaction_types', []))

            # 4. Create Location Hierarchy
            self._create_locations(tenant, config.get('location_hierarchy'), applied_by)

            # 5. Create Roles with Permissions
            self._create_roles(tenant, config.get('roles', []))

            # 6. Configure Modules
            self._configure_modules(tenant, config.get('modules', {}))

            # 7. Apply Configuration Settings
            self._apply_configuration(tenant, config.get('configuration', {}))

            # 8. Create Sample Data (if included)
            self._create_sample_data(tenant, config.get('sample_data', []), item_type_map)

            # 9. Record Application
            TemplateApplication.objects.create(
                template=template,
                tenant=tenant,
                template_version=template.version,
                applied_by=applied_by,
            )

            # 10. Increment usage counter
            Template.objects.filter(id=template.id).update(
                usage_count=models.F('usage_count') + 1
            )

    def _create_item_types(self, tenant, item_types_config):
        """Create item types and their custom fields. Returns name→object map."""
        item_type_map = {}
        for it_config in item_types_config:
            item_type = ItemType.objects.create(
                tenant=tenant,
                name=it_config['name'],
                description=it_config.get('description', ''),
                icon=it_config.get('icon', ''),
                parent=item_type_map.get(it_config.get('parent')),
            )
            item_type_map[it_config['name']] = item_type

            for idx, cf_config in enumerate(it_config.get('custom_fields', [])):
                CustomField.objects.create(
                    item_type=item_type,
                    name=cf_config['name'],
                    field_type=cf_config['field_type'],
                    is_required=cf_config.get('is_required', False),
                    is_searchable=cf_config.get('is_searchable', False),
                    default_value=cf_config.get('default_value', ''),
                    help_text=cf_config.get('help_text', ''),
                    validation_rules=cf_config.get('validation_rules', {}),
                    dropdown_options=cf_config.get('dropdown_options', []),
                    display_order=idx,
                )
        return item_type_map

    def _create_workflows(self, tenant, workflows_config, item_type_map):
        """Create workflows with states and transitions."""
        for wf_config in workflows_config:
            item_type = item_type_map.get(wf_config.get('item_type'))
            workflow = Workflow.objects.create(
                tenant=tenant,
                name=wf_config['name'],
                description=wf_config.get('description', ''),
                item_type=item_type,
            )

            state_map = {}
            for state_config in wf_config.get('states', []):
                state = WorkflowState.objects.create(
                    workflow=workflow,
                    name=state_config['name'],
                    is_initial=state_config.get('is_initial', False),
                    is_final=state_config.get('is_final', False),
                )
                state_map[state_config['name']] = state

            for trans_config in wf_config.get('transitions', []):
                WorkflowTransition.objects.create(
                    workflow=workflow,
                    name=trans_config['name'],
                    from_state=state_map[trans_config['from_state']],
                    to_state=state_map[trans_config['to_state']],
                    conditions=trans_config.get('conditions', {}),
                    required_fields=trans_config.get('required_fields', {}),
                )

    def _create_transaction_types(self, tenant, transaction_types_config):
        """Create transaction types."""
        for tt_config in transaction_types_config:
            TransactionType.objects.create(
                tenant=tenant,
                name=tt_config['name'],
                description=tt_config.get('description', ''),
                affects_quantity=tt_config.get('affects_quantity', 'none'),
                requires_approval=tt_config.get('requires_approval', False),
            )

    def _create_locations(self, tenant, location_config, created_by=None, parent=None):
        """Recursively create location hierarchy."""
        if not location_config:
            return
        location = Location.objects.create(
            tenant=tenant,
            name=location_config['name'],
            location_type=location_config.get('type', 'room'),
            parent=parent,
            created_by=created_by,
        )
        for child_config in location_config.get('children', []):
            self._create_locations(tenant, child_config, created_by, parent=location)

    def _create_roles(self, tenant, roles_config):
        """Create roles with permissions."""
        for role_config in roles_config:
            role = Role.objects.create(
                tenant=tenant,
                name=role_config['name'],
                description=role_config.get('description', ''),
            )
            for perm_string in role_config.get('permissions', []):
                resource, action = perm_string.rsplit('.', 1)
                permission, _ = Permission.objects.get_or_create(
                    resource=resource, action=action
                )
                RolePermission.objects.create(role=role, permission=permission)

    def _configure_modules(self, tenant, modules_config):
        """Enable/disable modules on tenant configuration."""
        config = tenant.configuration
        enabled = modules_config.get('enabled', [])
        config.enabled_modules = enabled
        config.save()

    def _apply_configuration(self, tenant, settings_config):
        """Apply configuration settings to tenant."""
        config = tenant.configuration
        field_mapping = {
            'currency': 'currency',
            'date_format': 'date_format',
            'timezone': 'timezone',
        }
        for key, field in field_mapping.items():
            if key in settings_config:
                setattr(config, field, settings_config[key])
        config.save()

    def _create_sample_data(self, tenant, sample_data, item_type_map):
        """Optionally create sample items for the tenant."""
        for item_data in sample_data:
            item_type = item_type_map.get(item_data.get('item_type'))
            if item_type:
                Item.objects.create(
                    tenant=tenant,
                    item_type=item_type,
                    code=item_data['code'],
                    name=item_data['name'],
                    quantity=item_data.get('quantity', 0),
                    unit=item_data.get('unit', 'pcs'),
                )
```

---

## 4. Template Cloning

### 4.1 Clone from Existing Tenant

Extract a tenant's configuration (excluding actual data) and package as a template:

```python
class TemplateCloner:
    def clone_from_tenant(self, tenant, template_name, created_by=None):
        """
        Extract configuration from a tenant and create a reusable template.
        Excludes actual items, transactions, and user data.
        """
        configuration = {
            'metadata': {
                'name': template_name,
                'version': '1.0.0',
                'description': f'Cloned from {tenant.name}',
                'industry': tenant.industry,
            },
            'item_types': self._extract_item_types(tenant),
            'workflows': self._extract_workflows(tenant),
            'transaction_types': self._extract_transaction_types(tenant),
            'location_hierarchy': self._extract_location_hierarchy(tenant),
            'roles': self._extract_roles(tenant),
            'modules': self._extract_modules(tenant),
            'configuration': self._extract_configuration(tenant),
            'sample_data': [],
        }

        template = Template.objects.create(
            name=template_name,
            slug=slugify(template_name),
            description=f'Template cloned from {tenant.name}',
            configuration=configuration,
            version='1.0.0',
            status='draft',
            created_by=created_by,
            is_system_template=False,
        )
        return template

    def _extract_item_types(self, tenant):
        result = []
        for it in ItemType.objects.filter(tenant=tenant, parent=None):
            result.append(self._serialize_item_type(it))
        return result

    def _serialize_item_type(self, item_type):
        return {
            'name': item_type.name,
            'description': item_type.description,
            'icon': item_type.icon,
            'custom_fields': [
                {
                    'name': cf.name,
                    'field_type': cf.field_type,
                    'is_required': cf.is_required,
                    'is_searchable': cf.is_searchable,
                    'default_value': cf.default_value,
                    'help_text': cf.help_text,
                    'validation_rules': cf.validation_rules,
                    'dropdown_options': cf.dropdown_options,
                }
                for cf in item_type.custom_fields.all()
            ],
            'children': [
                self._serialize_item_type(child)
                for child in item_type.children.all()
            ],
        }

    # Similar methods for workflows, transaction_types, locations, roles, modules, config
```

---

## 5. Template Versioning

### 5.1 Versioning Rules

- Use semantic versioning: `MAJOR.MINOR.PATCH`
- **PATCH** (1.0.0 → 1.0.1): Fix typos in descriptions, adjust default values
- **MINOR** (1.0.0 → 1.1.0): Add new item types, custom fields, workflow states
- **MAJOR** (1.0.0 → 2.0.0): Remove item types, restructure workflows, breaking changes

### 5.2 Version Tracking

When a template is updated, existing tenants are NOT affected. The `TemplateApplication` records which version was applied. This allows:
- Tenants to continue using their applied version
- Admins to see which tenants use outdated templates
- Optional "upgrade" path in future

---

## 6. Seed Templates

### 6.1 Management Command

```python
# apps/tenants/management/commands/load_seed_templates.py

class Command(BaseCommand):
    help = 'Load seed industry templates into the database'

    def handle(self, *args, **options):
        templates_dir = Path(__file__).resolve().parent.parent.parent / 'templates' / 'seed'

        for json_file in templates_dir.glob('*.json'):
            with open(json_file) as f:
                config = json.load(f)

            template, created = Template.objects.update_or_create(
                slug=slugify(config['metadata']['name']),
                defaults={
                    'name': config['metadata']['name'],
                    'description': config['metadata']['description'],
                    'configuration': config,
                    'version': config['metadata']['version'],
                    'status': 'active',
                    'is_system_template': True,
                }
            )

            action = 'Created' if created else 'Updated'
            self.stdout.write(f'{action}: {template.name}')
```

### 6.2 Seed Template Files

Store seed templates as JSON files:

```
apps/
  tenants/
    templates/
      seed/
        hospital.json
        manufacturing.json
        warehouse.json
        library.json
        retail.json
        food_beverage.json
        clinic.json
        education.json
        construction.json
```

### 6.3 Priority Templates (Build First)

Based on market opportunity and example completeness:

1. **Hospital & Healthcare** — Most detailed example in specs
2. **Medical Clinic** — Complete example exists in CLINIC_EXAMPLE.md
3. **Manufacturing & Factory** — Detailed in EXTENSIBILITY_GUIDELINES.md
4. **Warehouse & Distribution** — Core use case
5. **Library & Media** — Simple, good for testing

---

## 7. Template Selection UI

### 7.1 Onboarding Flow

```
Step 1: Organization Setup
  ├── Organization name
  ├── Admin email & password
  └── Industry selection (dropdown)

Step 2: Choose Template
  ├── Recommended templates (based on industry selection)
  ├── All templates (browse by category)
  ├── Template preview (modal showing what will be created)
  └── "Start from scratch" option

Step 3: Customize (optional)
  ├── Review item types (rename, add, remove)
  ├── Review workflows (adjust states)
  ├── Configure branding (logo, colors)
  └── Set locale (timezone, currency, date format)

Step 4: Complete
  ├── Summary of what was configured
  ├── Quick-start guide
  └── Redirect to dashboard
```

### 7.2 Template Preview

Before applying, show the tenant what the template includes:

```html
<!-- Template preview modal -->
<div class="template-preview">
  <h3>Hospital & Healthcare Template</h3>
  <p>This template will create:</p>

  <div class="preview-section">
    <h4>Item Types (3)</h4>
    <ul>
      <li>Medical Equipment — 5 custom fields</li>
      <li>Pharmaceuticals — 7 custom fields</li>
      <li>Surgical Instruments — 3 custom fields</li>
    </ul>
  </div>

  <div class="preview-section">
    <h4>Workflows (2)</h4>
    <ul>
      <li>Equipment Lifecycle — 5 states, 7 transitions</li>
      <li>Pharmaceutical Tracking — 3 states, 4 transitions</li>
    </ul>
  </div>

  <div class="preview-section">
    <h4>Locations</h4>
    <p>Hospital hierarchy with 5 departments, 12 rooms</p>
  </div>

  <div class="preview-section">
    <h4>Roles (5)</h4>
    <p>Equipment Manager, Department Head, Pharmacist, Maintenance Tech, Viewer</p>
  </div>

  <button class="btn-primary">Apply This Template</button>
</div>
```

---

## 8. API Endpoints

```
GET    /api/v1/templates/                    # List available templates
GET    /api/v1/templates/{slug}/             # Get template detail with preview
POST   /api/v1/templates/{slug}/apply/       # Apply template to current tenant
GET    /api/v1/templates/categories/         # List template categories
POST   /api/v1/templates/validate/           # Validate template JSON
POST   /api/v1/templates/clone/              # Clone current tenant as template
GET    /api/v1/templates/applications/       # List template applications for tenant
```

---

## 9. Testing Strategy

### 9.1 Unit Tests

```python
class TestTemplateEngine:
    def test_validate_valid_template(self):
        """A well-formed template JSON passes validation."""

    def test_validate_missing_required_sections(self):
        """Templates missing required sections fail validation."""

    def test_validate_invalid_field_types(self):
        """Custom fields with invalid types fail validation."""

    def test_validate_workflow_missing_initial_state(self):
        """Workflows without an initial state fail validation."""

    def test_apply_creates_item_types(self):
        """Applying a template creates all defined item types."""

    def test_apply_creates_custom_fields(self):
        """Applying a template creates custom fields for each item type."""

    def test_apply_creates_workflows(self):
        """Applying a template creates workflows with states and transitions."""

    def test_apply_creates_locations(self):
        """Applying a template creates the location hierarchy."""

    def test_apply_is_atomic(self):
        """If any part of template application fails, nothing is created."""

    def test_apply_increments_usage_count(self):
        """Applying a template increments its usage counter."""

    def test_clone_from_tenant(self):
        """Cloning a tenant produces a valid template JSON."""

    def test_clone_excludes_actual_data(self):
        """Cloned templates don't include items, transactions, or users."""
```

### 9.2 Integration Tests

```python
class TestTemplateOnboarding:
    def test_full_onboarding_flow(self):
        """Signup → template selection → apply → dashboard access."""

    def test_hospital_template_creates_expected_entities(self):
        """Hospital template creates specific item types, workflows, etc."""

    def test_start_from_scratch_creates_empty_tenant(self):
        """Choosing 'start from scratch' creates tenant with no item types."""
```

---

## 10. Migration Plan

### 10.1 Database Migrations

1. Create `TemplateCategory` model and migration
2. Create `Template` model and migration
3. Create `TemplateApplication` model and migration
4. Run `load_seed_templates` management command to populate initial templates

### 10.2 Integration with Existing Code

- Add `templates` app to `INSTALLED_APPS`
- Or: Add models to existing `tenants` app (since templates are tightly coupled to tenants)
- Register Template and TemplateCategory in Django admin
- Add template selection to tenant creation flow

### 10.3 Recommended: Add to `tenants` app

Since templates are fundamentally about tenant provisioning, add the models to `apps/tenants/models.py` rather than creating a separate app. This avoids circular imports (templates need to create ItemTypes, Workflows, etc. from other apps, but the tenants app is already the dependency root).

---

## 11. Acceptance Criteria

1. Templates can be created, validated, and stored as JSON in the database
2. Applying a template to a tenant creates all configured entities atomically
3. Template application records are tracked for audit purposes
4. At least 5 seed templates are available on first deployment
5. Templates can be cloned from existing tenant configurations
6. Template preview shows what will be created before application
7. Invalid template JSON is rejected with clear error messages
8. Template versioning tracks which version was applied to each tenant
9. Tenants can customize their configuration after template application
10. Template application does not affect other tenants
