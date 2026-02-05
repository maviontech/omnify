# Template System - Complete Technical Guide

## Overview

This guide explains how to build, manage, and apply industry templates in the platform. Templates allow new tenants to start with pre-configured setups tailored to their industry.

---

## Template Architecture

### What is a Template?

A template is a **JSON configuration** that defines:
- Item Types and their custom fields
- Workflows with states and transitions
- Transaction types
- Location hierarchies
- Enabled/disabled modules
- Default settings

### Template Storage

```
Database Tables:

templates
├── id (UUID)
├── name (e.g., "Hospital & Healthcare")
├── slug (e.g., "hospital")
├── description
├── industry_category
├── configuration (JSONB) ← The actual template data
├── version (e.g., "1.2.0")
├── status (draft, active, deprecated)
├── created_at
├── updated_at
├── created_by_user_id
└── usage_count

template_applications
├── id
├── template_id
├── tenant_id
├── applied_at
├── template_version
└── customizations_made (JSON)
```

---

## Template JSON Structure

### Complete Template Example

```json
{
  "template_id": "hospital-v1",
  "name": "Hospital & Healthcare",
  "version": "1.0.0",
  "description": "Complete inventory management for hospitals and healthcare facilities",
  "industry": "Healthcare",
  "author": "Platform Team",
  "created_at": "2024-01-15",
  
  "item_types": [
    {
      "name": "Medical Equipment",
      "description": "Diagnostic and treatment equipment",
      "icon": "medical-equipment",
      "color": "#2196F3",
      "custom_fields": [
        {
          "name": "Serial Number",
          "field_type": "text",
          "is_required": true,
          "is_searchable": true,
          "validation_rules": {
            "min_length": 5,
            "max_length": 50
          },
          "help_text": "Manufacturer's serial number"
        },
        {
          "name": "Manufacturer",
          "field_type": "text",
          "is_required": true,
          "is_searchable": true
        },
        {
          "name": "Model Number",
          "field_type": "text",
          "is_searchable": true
        },
        {
          "name": "Purchase Date",
          "field_type": "date",
          "is_required": false
        },
        {
          "name": "Warranty Expiration",
          "field_type": "date",
          "is_required": false
        },
        {
          "name": "Calibration Date",
          "field_type": "date",
          "is_required": false
        },
        {
          "name": "Next Service Date",
          "field_type": "date",
          "is_required": false
        },
        {
          "name": "Department",
          "field_type": "dropdown",
          "is_required": true,
          "dropdown_options": [
            "Emergency",
            "ICU",
            "Surgery",
            "Radiology",
            "Laboratory",
            "Pharmacy",
            "General Ward"
          ]
        },
        {
          "name": "Condition",
          "field_type": "dropdown",
          "is_required": true,
          "dropdown_options": [
            "Excellent",
            "Good",
            "Fair",
            "Needs Repair",
            "Out of Service"
          ],
          "default_value": "Good"
        }
      ]
    },
    {
      "name": "Pharmaceuticals",
      "description": "Medications and drugs",
      "icon": "pill",
      "color": "#4CAF50",
      "custom_fields": [
        {
          "name": "Drug Name",
          "field_type": "text",
          "is_required": true,
          "is_searchable": true
        },
        {
          "name": "Generic Name",
          "field_type": "text",
          "is_searchable": true
        },
        {
          "name": "Dosage",
          "field_type": "text",
          "is_required": true
        },
        {
          "name": "Batch Number",
          "field_type": "text",
          "is_required": true,
          "is_searchable": true
        },
        {
          "name": "Expiry Date",
          "field_type": "date",
          "is_required": true
        },
        {
          "name": "Storage Temperature",
          "field_type": "dropdown",
          "is_required": true,
          "dropdown_options": [
            "Room Temperature (15-25°C)",
            "Refrigerated (2-8°C)",
            "Frozen (-20°C or below)"
          ]
        },
        {
          "name": "Controlled Substance",
          "field_type": "boolean",
          "default_value": false
        }
      ]
    },
    {
      "name": "Surgical Instruments",
      "description": "Reusable surgical tools",
      "icon": "surgical-tool",
      "color": "#FF9800",
      "custom_fields": [
        {
          "name": "Instrument Type",
          "field_type": "text",
          "is_required": true
        },
        {
          "name": "Sterilization Date",
          "field_type": "date"
        },
        {
          "name": "Sterilization Method",
          "field_type": "dropdown",
          "dropdown_options": [
            "Autoclave",
            "Chemical",
            "Radiation",
            "Dry Heat"
          ]
        },
        {
          "name": "Sharpness Status",
          "field_type": "dropdown",
          "dropdown_options": [
            "Sharp",
            "Acceptable",
            "Needs Sharpening"
          ]
        }
      ]
    }
  ],
  
  "workflows": [
    {
      "name": "Equipment Lifecycle",
      "description": "Standard lifecycle for medical equipment",
      "item_types": ["Medical Equipment"],
      "states": [
        {
          "name": "Available",
          "is_initial": true,
          "is_final": false,
          "color": "#4CAF50",
          "description": "Equipment is ready for use"
        },
        {
          "name": "In Use",
          "is_initial": false,
          "is_final": false,
          "color": "#2196F3",
          "description": "Equipment is currently being used"
        },
        {
          "name": "Maintenance",
          "is_initial": false,
          "is_final": false,
          "color": "#FF9800",
          "description": "Equipment is being serviced or repaired",
          "time_limit_hours": 168
        },
        {
          "name": "Calibration",
          "is_initial": false,
          "is_final": false,
          "color": "#9C27B0",
          "description": "Equipment is being calibrated"
        },
        {
          "name": "Out of Service",
          "is_initial": false,
          "is_final": true,
          "color": "#F44336",
          "description": "Equipment is permanently retired"
        }
      ],
      "transitions": [
        {
          "name": "Issue to Department",
          "from_state": "Available",
          "to_state": "In Use",
          "required_roles": ["Equipment Manager", "Department Head"],
          "required_fields": ["Department"],
          "auto_create_transaction": true,
          "transaction_type": "Issue to Department"
        },
        {
          "name": "Return from Department",
          "from_state": "In Use",
          "to_state": "Available",
          "auto_create_transaction": true,
          "transaction_type": "Return from Department"
        },
        {
          "name": "Send for Maintenance",
          "from_state": "In Use",
          "to_state": "Maintenance",
          "required_fields": ["Next Service Date"],
          "auto_create_transaction": true,
          "transaction_type": "Send for Maintenance"
        },
        {
          "name": "Send for Calibration",
          "from_state": "Available",
          "to_state": "Calibration",
          "required_fields": ["Calibration Date"]
        },
        {
          "name": "Maintenance Complete",
          "from_state": "Maintenance",
          "to_state": "Available"
        },
        {
          "name": "Calibration Complete",
          "from_state": "Calibration",
          "to_state": "Available"
        },
        {
          "name": "Retire Equipment",
          "from_state": "Available",
          "to_state": "Out of Service",
          "required_roles": ["Equipment Manager"],
          "auto_create_transaction": true,
          "transaction_type": "Dispose"
        }
      ]
    },
    {
      "name": "Pharmaceutical Tracking",
      "description": "Track pharmaceutical inventory",
      "item_types": ["Pharmaceuticals"],
      "states": [
        {
          "name": "In Stock",
          "is_initial": true,
          "is_final": false,
          "color": "#4CAF50"
        },
        {
          "name": "Dispensed",
          "is_initial": false,
          "is_final": true,
          "color": "#2196F3"
        },
        {
          "name": "Expired",
          "is_initial": false,
          "is_final": true,
          "color": "#F44336"
        }
      ],
      "transitions": [
        {
          "name": "Dispense to Patient",
          "from_state": "In Stock",
          "to_state": "Dispensed",
          "required_roles": ["Pharmacist"],
          "auto_create_transaction": true,
          "transaction_type": "Dispense"
        },
        {
          "name": "Mark as Expired",
          "from_state": "In Stock",
          "to_state": "Expired",
          "auto_create_transaction": true,
          "transaction_type": "Dispose"
        }
      ]
    }
  ],
  
  "transaction_types": [
    {
      "name": "Issue to Department",
      "description": "Issue equipment to a department",
      "affects_quantity": "none",
      "icon": "arrow-right",
      "color": "#2196F3",
      "requires_approval": false,
      "required_fields": ["Department"]
    },
    {
      "name": "Return from Department",
      "description": "Return equipment from a department",
      "affects_quantity": "none",
      "icon": "arrow-left",
      "color": "#4CAF50",
      "requires_approval": false
    },
    {
      "name": "Send for Maintenance",
      "description": "Send equipment for maintenance or repair",
      "affects_quantity": "none",
      "icon": "wrench",
      "color": "#FF9800",
      "requires_approval": false
    },
    {
      "name": "Receive New Equipment",
      "description": "Receive newly purchased equipment",
      "affects_quantity": "increase",
      "icon": "plus",
      "color": "#4CAF50",
      "requires_approval": false
    },
    {
      "name": "Dispense",
      "description": "Dispense pharmaceuticals to patients",
      "affects_quantity": "decrease",
      "icon": "medical",
      "color": "#2196F3",
      "requires_approval": false
    },
    {
      "name": "Dispose",
      "description": "Dispose of expired or damaged items",
      "affects_quantity": "decrease",
      "icon": "trash",
      "color": "#F44336",
      "requires_approval": true
    }
  ],
  
  "locations": [
    {
      "name": "Main Hospital",
      "location_type": "building",
      "children": [
        {
          "name": "Emergency Department",
          "location_type": "department",
          "children": [
            {"name": "ER Storage Room", "location_type": "room"},
            {"name": "ER Equipment Cart", "location_type": "cart"}
          ]
        },
        {
          "name": "Intensive Care Unit",
          "location_type": "department",
          "children": [
            {"name": "ICU Storage", "location_type": "room"},
            {"name": "ICU Equipment Room", "location_type": "room"}
          ]
        },
        {
          "name": "Surgery",
          "location_type": "department",
          "children": [
            {"name": "OR 1", "location_type": "room"},
            {"name": "OR 2", "location_type": "room"},
            {"name": "Surgical Instrument Storage", "location_type": "room"}
          ]
        },
        {
          "name": "Pharmacy",
          "location_type": "department",
          "children": [
            {"name": "Refrigerated Storage", "location_type": "room"},
            {"name": "Controlled Substances Vault", "location_type": "room"},
            {"name": "General Pharmacy Storage", "location_type": "room"}
          ]
        },
        {
          "name": "Central Equipment Storage",
          "location_type": "warehouse",
          "children": [
            {"name": "Aisle A", "location_type": "aisle"},
            {"name": "Aisle B", "location_type": "aisle"}
          ]
        },
        {
          "name": "Maintenance Workshop",
          "location_type": "workshop"
        }
      ]
    }
  ],
  
  "roles": [
    {
      "name": "Equipment Manager",
      "description": "Manages all medical equipment",
      "permissions": [
        "items.view",
        "items.create",
        "items.update",
        "items.delete",
        "transactions.view",
        "transactions.create",
        "workflows.execute",
        "reports.view",
        "reports.export"
      ]
    },
    {
      "name": "Department Head",
      "description": "Manages equipment for their department",
      "permissions": [
        "items.view",
        "items.update",
        "transactions.view",
        "transactions.create",
        "workflows.execute"
      ]
    },
    {
      "name": "Pharmacist",
      "description": "Manages pharmaceutical inventory",
      "permissions": [
        "items.view",
        "items.create",
        "items.update",
        "transactions.view",
        "transactions.create",
        "workflows.execute"
      ]
    },
    {
      "name": "Maintenance Technician",
      "description": "Handles equipment maintenance",
      "permissions": [
        "items.view",
        "items.update",
        "transactions.view",
        "workflows.execute"
      ]
    },
    {
      "name": "Viewer",
      "description": "Read-only access to inventory",
      "permissions": [
        "items.view",
        "transactions.view",
        "reports.view"
      ]
    }
  ],
  
  "enabled_modules": [
    "items",
    "transactions",
    "workflows",
    "locations",
    "reports",
    "notifications"
  ],
  
  "disabled_modules": [
    "invoicing",
    "payments",
    "purchase_orders",
    "sales_orders",
    "financial_reports"
  ],
  
  "configuration": {
    "default_currency": "USD",
    "date_format": "MM/DD/YYYY",
    "timezone": "America/New_York",
    "low_stock_threshold": 10,
    "enable_barcode_scanning": true,
    "require_approval_for_disposal": true
  },
  
  "sample_data": {
    "include_sample_items": true,
    "sample_items": [
      {
        "item_type": "Medical Equipment",
        "code": "VENT-001",
        "name": "Ventilator - Model X200",
        "quantity": 1,
        "location": "ICU Equipment Room",
        "custom_fields": {
          "Serial Number": "VX200-2024-001",
          "Manufacturer": "MedTech Corp",
          "Model Number": "X200",
          "Department": "ICU",
          "Condition": "Excellent"
        }
      }
    ]
  }
}
```

---

## How to Build Templates

### Method 1: Template Builder UI (Recommended)

**Step-by-Step Process:**

1. **Access Template Builder**
   - Log in as platform administrator
   - Navigate to Admin → Templates → Create New Template

2. **Basic Information**
   ```
   Template Name: Hospital & Healthcare
   Industry: Healthcare
   Description: Complete inventory management for hospitals
   Icon: hospital
   ```

3. **Add Item Types**
   - Click "Add Item Type"
   - Fill in name, description, icon
   - Add custom fields one by one
   - Set field properties (type, required, searchable)
   - Preview how it will look

4. **Define Workflows**
   - Click "Add Workflow"
   - Use visual state diagram editor
   - Drag and drop states
   - Draw transitions between states
   - Configure transition rules

5. **Add Transaction Types**
   - Click "Add Transaction Type"
   - Set name, description, icon
   - Choose if it increases/decreases inventory
   - Set approval requirements

6. **Create Location Hierarchy**
   - Use tree view editor
   - Add locations and sub-locations
   - Drag to reorganize

7. **Configure Modules**
   - Toggle modules on/off
   - Set default configurations

8. **Preview & Test**
   - Preview how tenant will see it
   - Test apply to a demo tenant
   - Verify everything works

9. **Publish**
   - Save as draft or publish immediately
   - Set version number
   - Add release notes

### Method 2: JSON Import

**For Advanced Users:**

1. **Create JSON File**
   - Use the structure shown above
   - Validate JSON syntax

2. **Import via UI**
   - Admin → Templates → Import
   - Upload JSON file
   - System validates structure
   - Preview before importing
   - Confirm import

3. **Edit if Needed**
   - Use template builder to refine
   - Test and publish

### Method 3: Clone from Existing Tenant

**Fastest Way to Create Templates:**

1. **Find Successful Tenant**
   - Identify a tenant with good configuration
   - Get their permission (if needed)

2. **Clone Configuration**
   - Admin → Tenants → Select Tenant
   - Click "Clone as Template"
   - System extracts configuration
   - Excludes actual data (items, transactions, users)

3. **Clean Up**
   - Remove tenant-specific customizations
   - Generalize names and descriptions
   - Add sample data if desired

4. **Publish**
   - Review and publish as new template

---

## Template Application Process

### When Tenant Signs Up

```python
# Simplified code flow

def apply_template_to_tenant(tenant, template):
    """Apply a template to a new tenant"""
    
    with transaction.atomic():
        # 1. Create Item Types
        for item_type_data in template['item_types']:
            item_type = ItemType.objects.create(
                tenant=tenant,
                name=item_type_data['name'],
                description=item_type_data['description'],
                icon=item_type_data['icon'],
                color=item_type_data['color']
            )
            
            # Create Custom Fields
            for field_data in item_type_data['custom_fields']:
                CustomField.objects.create(
                    item_type=item_type,
                    name=field_data['name'],
                    field_type=field_data['field_type'],
                    is_required=field_data.get('is_required', False),
                    is_searchable=field_data.get('is_searchable', True),
                    validation_rules=field_data.get('validation_rules', {}),
                    dropdown_options=field_data.get('dropdown_options'),
                    default_value=field_data.get('default_value'),
                    help_text=field_data.get('help_text', '')
                )
        
        # 2. Create Workflows
        for workflow_data in template['workflows']:
            workflow = Workflow.objects.create(
                tenant=tenant,
                name=workflow_data['name'],
                description=workflow_data['description']
            )
            
            # Create States
            state_map = {}
            for state_data in workflow_data['states']:
                state = WorkflowState.objects.create(
                    workflow=workflow,
                    name=state_data['name'],
                    description=state_data.get('description', ''),
                    is_initial=state_data.get('is_initial', False),
                    is_final=state_data.get('is_final', False),
                    color=state_data['color'],
                    time_limit_hours=state_data.get('time_limit_hours')
                )
                state_map[state_data['name']] = state
            
            # Create Transitions
            for trans_data in workflow_data['transitions']:
                WorkflowTransition.objects.create(
                    workflow=workflow,
                    name=trans_data['name'],
                    from_state=state_map[trans_data['from_state']],
                    to_state=state_map[trans_data['to_state']],
                    required_fields=trans_data.get('required_fields', []),
                    auto_create_transaction=trans_data.get('auto_create_transaction', False),
                    conditions=trans_data.get('conditions', {})
                )
        
        # 3. Create Transaction Types
        for trans_type_data in template['transaction_types']:
            TransactionType.objects.create(
                tenant=tenant,
                name=trans_type_data['name'],
                description=trans_type_data['description'],
                affects_quantity=trans_type_data['affects_quantity'],
                icon=trans_type_data['icon'],
                color=trans_type_data['color'],
                requires_approval=trans_type_data.get('requires_approval', False)
            )
        
        # 4. Create Locations
        def create_location_hierarchy(parent, location_data):
            location = Location.objects.create(
                tenant=tenant,
                parent=parent,
                name=location_data['name'],
                location_type=location_data['location_type']
            )
            for child_data in location_data.get('children', []):
                create_location_hierarchy(location, child_data)
        
        for location_data in template['locations']:
            create_location_hierarchy(None, location_data)
        
        # 5. Create Roles
        for role_data in template.get('roles', []):
            role = Role.objects.create(
                tenant=tenant,
                name=role_data['name'],
                description=role_data['description']
            )
            # Assign permissions
            for perm_code in role_data['permissions']:
                permission = Permission.objects.get(code=perm_code)
                RolePermission.objects.create(role=role, permission=permission)
        
        # 6. Configure Modules
        tenant.configuration.enabled_modules = template['enabled_modules']
        tenant.configuration.save()
        
        # 7. Apply Configuration
        config = template.get('configuration', {})
        tenant.configuration.default_currency = config.get('default_currency', 'USD')
        tenant.configuration.date_format = config.get('date_format', 'YYYY-MM-DD')
        tenant.configuration.timezone = config.get('timezone', 'UTC')
        tenant.configuration.save()
        
        # 8. Create Sample Data (if requested)
        if template.get('sample_data', {}).get('include_sample_items'):
            for item_data in template['sample_data']['sample_items']:
                # Create sample items...
                pass
        
        # 9. Record Template Application
        TemplateApplication.objects.create(
            template_id=template['template_id'],
            tenant=tenant,
            template_version=template['version']
        )
    
    return True
```

---

## Template Management Best Practices

### 1. **Start with Core Templates**
Build 5-10 templates for most common industries:
- Hospital & Healthcare
- Manufacturing & Factory
- Warehouse & Distribution
- Library & Media
- Retail Store
- Food & Beverage
- Construction & Equipment
- Education & School

### 2. **Keep Templates Simple**
- Don't try to cover every edge case
- Focus on 80% use case
- Let tenants customize the remaining 20%

### 3. **Version Templates**
- Use semantic versioning (1.0.0, 1.1.0, 2.0.0)
- Document changes in each version
- Allow tenants to upgrade

### 4. **Test Thoroughly**
- Apply template to test tenant
- Verify all configurations work
- Test workflows end-to-end
- Check for errors

### 5. **Gather Feedback**
- Track which templates are popular
- Monitor customization patterns
- Update templates based on feedback

### 6. **Maintain Templates**
- Update when platform adds new features
- Fix bugs in template configurations
- Deprecate outdated templates

---

## Summary

### Template System Enables:

✅ **Fast Onboarding** - Tenants start with 80% configured  
✅ **Industry-Specific** - Each industry gets relevant setup  
✅ **Scalable** - No manual configuration needed  
✅ **Flexible** - Tenants can customize after applying  
✅ **Reusable** - Clone successful configurations  
✅ **Maintainable** - Update templates over time  

### Who Builds Templates:

1. **Your Team** - Initial core templates
2. **Platform Admins** - New templates as needed
3. **Cloning** - From successful tenant setups
4. **Community** - Eventually, users can share templates

### Result:

- Hospital signs up → Gets hospital template → Customizes → Ready in 30 minutes
- Factory signs up → Gets factory template → Customizes → Ready in 30 minutes
- **Same platform. Different configurations. Zero code changes.**
