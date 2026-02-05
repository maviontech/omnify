# Omnify - Customization Approaches

## The Question

When **Tenant A (Hospital)** and **Tenant B (Factory)** sign up for Omnify, who configures the platform to match their specific needs?

---

## Three Possible Approaches

### **Approach 1: Self-Service Configuration (Recommended)**
**Tenants configure it themselves through the web interface**

### **Approach 2: Onboarding Service**
**Your team helps tenants set up during onboarding**

### **Approach 3: Hybrid Approach**
**Combination of templates + self-service + optional support**

---

## Approach 1: Self-Service Configuration (Recommended)

### How It Works

**When a new tenant signs up:**

1. **Initial Setup Wizard** (5-10 minutes)
   - Choose industry template (Hospital, Factory, Warehouse, Library, etc.)
   - Or start from scratch
   - Set basic info (company name, timezone, currency)

2. **Template Applied Automatically**
   - Pre-configured item types for their industry
   - Pre-configured custom fields
   - Pre-configured workflows
   - Pre-configured transaction types
   - Sample data (optional)

3. **Tenant Customizes Further** (through web interface)
   - Add/remove/modify item types
   - Add/remove/modify custom fields
   - Adjust workflows
   - Configure permissions
   - Enable/disable modules

### Example: Hospital Signs Up

**Step 1: Choose Template**
```
Welcome to the Platform!
Select your industry:
○ Library
○ Warehouse
● Hospital          ← Selected
○ Factory
○ Retail
○ Custom (start from scratch)

[Next]
```

**Step 2: Template Applied**
```
✓ Created Item Types:
  - Medical Equipment
  - Pharmaceuticals
  - Surgical Instruments
  - Consumable Supplies

✓ Added Custom Fields:
  - Serial Number
  - Manufacturer
  - Calibration Date
  - Warranty Expiration
  - Department Assignment

✓ Created Workflows:
  - Equipment Lifecycle (Available → In Use → Maintenance → Sterilization → Available)
  - Pharmaceutical Tracking (In Stock → Dispensed → Administered)

✓ Created Transaction Types:
  - Issue to Department
  - Return from Department
  - Send for Maintenance
  - Dispose/Retire

✓ Created Locations:
  - Main Hospital
    └─ Departments (Emergency, Surgery, ICU, etc.)
    └─ Storage Areas
    └─ Maintenance Workshop

Your hospital inventory system is ready with Omnify!
```

**Step 3: Hospital Admin Customizes**
```
The hospital admin logs in and can:
- Add more departments
- Add custom fields (e.g., "FDA Approval Number")
- Modify workflows (e.g., add "Quarantine" state)
- Add more transaction types
- Configure user roles
- Enable invoicing module (if they bill patients)
```

### Example: Factory Signs Up

**Step 1: Choose Template**
```
Welcome to the Platform!
Select your industry:
○ Library
○ Warehouse
○ Hospital
● Factory          ← Selected
○ Retail
○ Custom (start from scratch)

[Next]
```

**Step 2: Template Applied**
```
✓ Created Item Types:
  - Raw Materials
  - Work in Progress
  - Finished Products
  - Packaging Materials

✓ Added Custom Fields:
  - Batch Number
  - Manufacturing Date
  - Expiry Date
  - Supplier
  - Quality Grade
  - Storage Temperature

✓ Created Workflows:
  - Production Flow (Ordered → Received → QC → In Stock → Issued → Production → Finished)
  - Quality Control (Pending → Inspecting → Passed/Failed)

✓ Created Transaction Types:
  - Goods Receipt Note (GRN)
  - Quality Inspection
  - Issue to Production
  - Production Output
  - Dispatch to Customer

✓ Created Locations:
  - Factory Building
    └─ Raw Material Storage
    └─ Production Floor
    └─ Finished Goods Warehouse
    └─ Shipping Area

✓ Enabled Modules:
  - Invoicing
  - Purchase Orders
  - Sales Orders
  - Batch Tracking

Your factory inventory system is ready!
```

**Step 3: Factory Admin Customizes**
```
The factory admin logs in and can:
- Add more product categories
- Add custom fields (e.g., "Allergen Information" for food factory)
- Modify workflows (e.g., add "Packaging" stage)
- Configure pricing
- Set up suppliers and customers
- Configure invoice templates
```

---

## What Each Tenant Sees When They Log In

### Hospital Admin Logs In

**Dashboard:**
```
┌─────────────────────────────────────────────────┐
│  City Hospital - Inventory Management           │
├─────────────────────────────────────────────────┤
│  📊 Dashboard                                    │
│  🏥 Medical Equipment (1,234 items)             │
│  💊 Pharmaceuticals (5,678 items)               │
│  🔧 Surgical Instruments (890 items)            │
│  📦 Consumable Supplies (3,456 items)           │
│                                                  │
│  Recent Transactions:                            │
│  - Issued Ventilator to ICU                     │
│  - Returned Wheelchair from Emergency           │
│  - Sent X-Ray Machine for Calibration          │
│                                                  │
│  Alerts:                                         │
│  ⚠️ 12 items need calibration this week         │
│  ⚠️ 5 pharmaceuticals expiring in 30 days       │
└─────────────────────────────────────────────────┘

Menu:
- Medical Equipment
- Pharmaceuticals
- Surgical Instruments
- Consumables
- Departments
- Maintenance Schedule
- Reports
```

### Factory Admin Logs In

**Dashboard:**
```
┌─────────────────────────────────────────────────┐
│  ABC Manufacturing - Inventory Management        │
├─────────────────────────────────────────────────┤
│  📊 Dashboard                                    │
│  🏭 Raw Materials (2,345 items)                 │
│  ⚙️ Work in Progress (567 items)                │
│  📦 Finished Products (1,890 items)             │
│  📋 Packaging Materials (890 items)             │
│                                                  │
│  Recent Transactions:                            │
│  - Received Steel Sheets (GRN-2024-001)         │
│  - Issued Materials to Production Line 3        │
│  - Completed Production Batch #4567             │
│  - Dispatched Order #8901 to Customer           │
│                                                  │
│  Alerts:                                         │
│  ⚠️ 3 raw materials below reorder level         │
│  ⚠️ 8 batches expiring in 30 days               │
│  💰 5 invoices overdue                           │
└─────────────────────────────────────────────────┘

Menu:
- Raw Materials
- Production
- Finished Products
- Suppliers
- Customers
- Purchase Orders
- Sales Orders
- Invoices
- Financial Reports
```

**They see completely different interfaces!**
- Different item types
- Different fields
- Different workflows
- Different transaction types
- Different menus
- Different modules enabled

---

## Approach 2: Onboarding Service

### How It Works

**When a new tenant signs up:**

1. **Sales/Onboarding Call**
   - Your team talks to the client
   - Understands their requirements
   - Documents their needs

2. **Your Team Configures**
   - Your onboarding specialist logs into admin panel
   - Configures the tenant's workspace
   - Sets up item types, fields, workflows
   - Imports initial data if provided
   - Creates user accounts

3. **Training Session**
   - Walk the client through their configured system
   - Train their team
   - Answer questions
   - Hand over admin access

### Pros & Cons

**Pros:**
- ✅ White-glove service
- ✅ Ensures proper setup
- ✅ Can charge premium for onboarding
- ✅ Builds relationship with client

**Cons:**
- ❌ Requires your team's time
- ❌ Doesn't scale well (bottleneck)
- ❌ Slower onboarding
- ❌ Higher operational costs

**Best For:**
- Enterprise clients
- Complex configurations
- High-value contracts
- Industries with specific compliance needs

---

## Approach 3: Hybrid Approach (Best of Both Worlds)

### How It Works

**Tier-Based Onboarding:**

#### **Self-Service Tier (Small Businesses)**
- Sign up online
- Choose template
- Configure themselves
- Access to help documentation
- Community forum support

#### **Assisted Tier (Medium Businesses)**
- Sign up online
- Choose template
- Get 1-2 hour onboarding call
- Your team helps with initial setup
- Email/chat support

#### **White-Glove Tier (Enterprise)**
- Sales call first
- Custom configuration by your team
- Dedicated onboarding specialist
- Training sessions
- Ongoing support

### Industry Templates

You provide **pre-built templates** for common industries:

```
Available Templates:

1. Hospital & Healthcare
   - Medical equipment tracking
   - Pharmaceutical management
   - Department-based workflows
   - Calibration tracking

2. Manufacturing & Factory
   - Raw materials management
   - Production tracking
   - Batch/lot tracking
   - Quality control workflows
   - Financial management

3. Warehouse & Distribution
   - Multi-location inventory
   - Inbound/outbound logistics
   - Shipping management
   - Carrier integration

4. Library & Media
   - Book cataloging
   - Borrower management
   - Due date tracking
   - Fine calculation

5. Retail Store
   - Product catalog
   - Point of sale integration
   - Stock management
   - Customer orders

6. Food & Beverage
   - Ingredient tracking
   - Recipe management
   - Expiry date monitoring
   - FIFO inventory rotation
   - Food safety compliance

7. Construction & Equipment
   - Tool tracking
   - Equipment maintenance
   - Project-based allocation
   - Rental management

8. Education & School
   - Asset tracking
   - Lab equipment
   - Textbook management
   - Department allocation

9. Government & Public Sector
   - Asset management
   - Procurement tracking
   - Compliance reporting
   - Multi-department structure

10. Custom (Start from Scratch)
    - Build your own configuration
    - Maximum flexibility
```

---

## Technical Implementation

### How Templates Work

**Template Definition (JSON stored in database):**

```json
{
  "template_id": "hospital",
  "name": "Hospital & Healthcare",
  "description": "Complete inventory management for hospitals",
  "item_types": [
    {
      "name": "Medical Equipment",
      "custom_fields": [
        {"name": "Serial Number", "type": "text", "required": true},
        {"name": "Manufacturer", "type": "text"},
        {"name": "Calibration Date", "type": "date"},
        {"name": "Next Service Date", "type": "date"},
        {"name": "Department", "type": "dropdown", "options": ["Emergency", "ICU", "Surgery"]}
      ]
    },
    {
      "name": "Pharmaceuticals",
      "custom_fields": [
        {"name": "Drug Name", "type": "text", "required": true},
        {"name": "Dosage", "type": "text"},
        {"name": "Expiry Date", "type": "date", "required": true},
        {"name": "Batch Number", "type": "text"},
        {"name": "Storage Temperature", "type": "dropdown", "options": ["Room Temp", "Refrigerated", "Frozen"]}
      ]
    }
  ],
  "workflows": [
    {
      "name": "Equipment Lifecycle",
      "states": ["Available", "In Use", "Maintenance", "Sterilization"],
      "transitions": [
        {"from": "Available", "to": "In Use", "name": "Issue"},
        {"from": "In Use", "to": "Maintenance", "name": "Send for Service"},
        {"from": "Maintenance", "to": "Sterilization", "name": "Service Complete"},
        {"from": "Sterilization", "to": "Available", "name": "Ready for Use"}
      ]
    }
  ],
  "transaction_types": [
    {"name": "Issue to Department", "affects_quantity": "decrease"},
    {"name": "Return from Department", "affects_quantity": "increase"},
    {"name": "Send for Maintenance", "affects_quantity": "none"},
    {"name": "Dispose", "affects_quantity": "decrease"}
  ],
  "locations": [
    {"name": "Main Hospital", "children": [
      {"name": "Emergency Department"},
      {"name": "ICU"},
      {"name": "Surgery"},
      {"name": "Central Storage"}
    ]}
  ],
  "enabled_modules": ["workflows", "locations", "reports"],
  "disabled_modules": ["invoicing", "purchase_orders", "sales_orders"]
}
```

**When tenant selects template:**

```python
def apply_template(tenant, template_id):
    template = Template.objects.get(id=template_id)
    
    # Create item types
    for item_type_data in template.item_types:
        item_type = ItemType.objects.create(
            tenant=tenant,
            name=item_type_data['name']
        )
        
        # Create custom fields
        for field_data in item_type_data['custom_fields']:
            CustomField.objects.create(
                item_type=item_type,
                name=field_data['name'],
                field_type=field_data['type'],
                is_required=field_data.get('required', False),
                dropdown_options=field_data.get('options')
            )
    
    # Create workflows
    for workflow_data in template.workflows:
        workflow = Workflow.objects.create(
            tenant=tenant,
            name=workflow_data['name']
        )
        # ... create states and transitions
    
    # Create transaction types
    for trans_type_data in template.transaction_types:
        TransactionType.objects.create(
            tenant=tenant,
            name=trans_type_data['name'],
            affects_quantity=trans_type_data['affects_quantity']
        )
    
    # Create locations
    # ... create location hierarchy
    
    # Enable/disable modules
    tenant.configuration.enabled_modules = template.enabled_modules
    tenant.configuration.save()
```

---

## Admin Configuration Interface

### What Tenant Admins Can Configure

**Through Web Interface (No Coding):**

1. **Item Types**
   - Add new types
   - Modify existing types
   - Set icons and colors
   - Organize in hierarchies

2. **Custom Fields**
   - Add fields to any item type
   - Choose data types
   - Set validation rules
   - Mark as required/optional
   - Set default values

3. **Workflows**
   - Create new workflows
   - Add states
   - Define transitions
   - Set permissions per transition
   - Configure notifications

4. **Transaction Types**
   - Create new transaction types
   - Set whether they increase/decrease inventory
   - Configure required fields
   - Set icons and colors

5. **Locations**
   - Create location hierarchies
   - Set capacity limits
   - Add custom fields to locations

6. **Users & Permissions**
   - Create roles
   - Assign permissions
   - Add users
   - Assign roles to users

7. **Modules**
   - Enable/disable features
   - Configure module settings

8. **Branding**
   - Upload logo
   - Set color scheme
   - Customize invoice templates

9. **Integrations**
   - Configure API keys
   - Set up webhooks
   - Connect external systems

---

## Recommended Approach

### **Start with Hybrid:**

**Phase 1: Launch (Months 1-6)**
- Provide 5-10 industry templates
- Self-service for simple cases
- Assisted onboarding for paying customers
- Build knowledge base and documentation

**Phase 2: Scale (Months 6-12)**
- Add more templates based on demand
- Improve self-service wizard
- Create video tutorials
- Build community forum

**Phase 3: Mature (Year 2+)**
- Mostly self-service
- Premium onboarding for enterprise
- Template marketplace (users can share templates)
- AI-assisted configuration

---

## Summary

### Who Does the Customization?

**Answer: It depends on your business model, but typically:**

1. **You provide templates** (one-time work)
2. **Tenants choose a template** (automated)
3. **System applies template** (automated)
4. **Tenants customize further** (self-service through web UI)
5. **Optional: Your team helps** (for premium customers)

### Key Points:

✅ **No coding required** - Everything through web interface  
✅ **Templates speed up onboarding** - 80% configured in minutes  
✅ **Self-service scales** - No bottleneck  
✅ **Flexibility remains** - Tenants can customize everything  
✅ **Premium service option** - For enterprise customers  

### What You Build Once:

- The platform (Django application)
- Industry templates (JSON configurations)
- Configuration UI (admin interface)
- Documentation and tutorials

### What Happens Per Tenant:

- They sign up
- Choose template (or start from scratch)
- System applies configuration automatically
- They customize through web UI
- They start using it

**Result:** Hospital sees hospital version. Factory sees factory version. Same Omnify platform. Different configurations. Zero code changes.
