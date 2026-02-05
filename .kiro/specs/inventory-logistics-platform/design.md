# Omnify - Design Document

## Overview

This document describes the technical design for **Omnify** - a multi-tenant, configurable operations management platform built with Django, MySQL, HTML, CSS, and JavaScript. Omnify serves multiple industries by providing flexible item types, customizable workflows, role-based access control, and comprehensive transaction tracking.

**Omnify: Everything. Organized.**

### Design Goals

1. **Multi-tenancy**: Complete data isolation between organizations while sharing infrastructure
2. **Configurability**: Allow tenants to define custom item types, fields, workflows, and business rules
3. **Scalability**: Support thousands of concurrent users and millions of inventory items
4. **Security**: Implement robust authentication, authorization, and data protection
5. **Performance**: Achieve sub-second response times for common operations
6. **Maintainability**: Use Django best practices and clean architecture patterns

### Technology Stack

- **Backend**: Django 5.x (Python 3.11+)
- **Database**: MySQL 8.0+
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Caching**: Redis for session management and data caching
- **Task Queue**: Celery with Redis broker for asynchronous processing
- **Web Server**: Gunicorn with Nginx reverse proxy
- **Storage**: Local filesystem or S3-compatible object storage for file attachments

## Architecture

### High-Level Architecture

The platform follows a layered architecture pattern:

```
┌─────────────────────────────────────────────────────────┐
│                    Presentation Layer                    │
│         (Django Templates, HTML/CSS/JS, REST API)       │
└─────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────┐
│                    Application Layer                     │
│        (Django Views, ViewSets, Business Logic)         │
└─────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────┐
│                      Domain Layer                        │
│         (Django Models, Managers, Domain Logic)         │
└─────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────┐
│                   Infrastructure Layer                   │
│           (MySQL Database, Redis Cache, Celery)         │
└─────────────────────────────────────────────────────────┘
```


### Django Project Structure

```
inventory_platform/
├── manage.py
├── config/                      # Project configuration
│   ├── settings/
│   │   ├── base.py             # Base settings
│   │   ├── development.py      # Development settings
│   │   └── production.py       # Production settings
│   ├── urls.py                 # Root URL configuration
│   └── wsgi.py
├── apps/
│   ├── tenants/                # Multi-tenancy management
│   ├── users/                  # User authentication and management
│   ├── items/                  # Item and item type management
│   ├── transactions/           # Transaction processing
│   ├── workflows/              # Workflow engine
│   ├── locations/              # Location management
│   ├── permissions/            # Role-based access control
│   ├── notifications/          # Notification system
│   ├── reports/                # Reporting engine
│   ├── api/                    # REST API
│   └── core/                   # Shared utilities and base classes
├── templates/                  # Django templates
├── static/                     # Static files (CSS, JS, images)
├── media/                      # User-uploaded files
└── requirements.txt
```

### Multi-Tenancy Strategy

**Approach**: Shared database with tenant identifier (row-level isolation)

**Rationale**: This approach provides the best balance of:
- Cost efficiency (single database instance)
- Operational simplicity (unified backups, migrations)
- Adequate isolation for most use cases
- Scalability for thousands of tenants

**Implementation**:
- Every model includes a `tenant` foreign key
- Custom Django middleware sets the current tenant context
- Custom model manager automatically filters queries by tenant
- Database-level row security policies as additional safeguard


## Components and Interfaces

### 1. Tenants App

**Purpose**: Manage tenant organizations and their configurations

**Key Models**:

```python
class Tenant(models.Model):
    """Represents an organization using the platform"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    subscription_tier = models.CharField(max_length=50)
    
class TenantConfiguration(models.Model):
    """Tenant-specific configuration settings"""
    tenant = models.OneToOneField(Tenant, on_delete=models.CASCADE)
    timezone = models.CharField(max_length=50, default='UTC')
    date_format = models.CharField(max_length=20)
    currency = models.CharField(max_length=3, default='USD')
    logo = models.ImageField(upload_to='tenant_logos/', null=True)
    primary_color = models.CharField(max_length=7)  # Hex color
```

**Key Interfaces**:
- `TenantMiddleware`: Sets current tenant from subdomain or header
- `TenantManager`: Custom manager that filters by current tenant
- `get_current_tenant()`: Utility function to retrieve current tenant

### 2. Users App

**Purpose**: Handle user authentication, authorization, and profile management

**Key Models**:

```python
class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model extending Django's AbstractBaseUser"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(null=True)
    mfa_enabled = models.BooleanField(default=False)
    mfa_secret = models.CharField(max_length=32, null=True)
    
class UserSession(models.Model):
    """Track active user sessions"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    session_key = models.CharField(max_length=40, unique=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
```

**Key Interfaces**:
- `CustomAuthBackend`: Authentication backend supporting email login
- `MFAMixin`: Mixin for multi-factor authentication
- `PasswordValidator`: Custom password complexity validation


### 3. Permissions App

**Purpose**: Implement role-based access control (RBAC)

**Key Models**:

```python
class Role(models.Model):
    """Defines a role with specific permissions"""
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField()
    parent = models.ForeignKey('self', null=True, on_delete=models.SET_NULL)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['tenant', 'name']

class Permission(models.Model):
    """Granular permission definition"""
    code = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=200)
    resource = models.CharField(max_length=50)  # items, transactions, etc.
    action = models.CharField(max_length=50)    # view, create, update, delete
    
class RolePermission(models.Model):
    """Maps permissions to roles"""
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)
    item_type = models.ForeignKey('items.ItemType', null=True, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ['role', 'permission', 'item_type']

class UserRole(models.Model):
    """Assigns roles to users"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    assigned_at = models.DateTimeField(auto_now_add=True)
    assigned_by = models.ForeignKey(User, related_name='role_assignments', on_delete=models.SET_NULL, null=True)
```

**Key Interfaces**:
- `PermissionChecker`: Service class to check user permissions
- `@require_permission` decorator: View decorator for permission checks
- `has_permission(user, permission_code, obj=None)`: Permission checking function


### 4. Items App

**Purpose**: Manage item types, custom fields, and inventory items

**Key Models**:

```python
class ItemType(models.Model):
    """Defines a category of items with custom attributes"""
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    description = models.TextField()
    parent = models.ForeignKey('self', null=True, on_delete=models.SET_NULL)
    icon = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['tenant', 'name']

class CustomField(models.Model):
    """Defines a custom field for an item type"""
    DATA_TYPES = [
        ('text', 'Text'),
        ('number', 'Number'),
        ('date', 'Date'),
        ('datetime', 'DateTime'),
        ('boolean', 'Boolean'),
        ('dropdown', 'Dropdown'),
        ('multiselect', 'Multi-Select'),
        ('file', 'File Attachment'),
        ('url', 'URL'),
    ]
    
    item_type = models.ForeignKey(ItemType, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    field_type = models.CharField(max_length=20, choices=DATA_TYPES)
    is_required = models.BooleanField(default=False)
    is_searchable = models.BooleanField(default=True)
    default_value = models.TextField(null=True)
    validation_rules = models.JSONField(default=dict)  # min, max, regex, etc.
    dropdown_options = models.JSONField(null=True)     # For dropdown/multiselect
    display_order = models.IntegerField(default=0)
    help_text = models.TextField(blank=True)
    
    class Meta:
        unique_together = ['item_type', 'name']
        ordering = ['display_order', 'name']

class Item(models.Model):
    """Represents an inventory item"""
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    item_type = models.ForeignKey(ItemType, on_delete=models.PROTECT)
    code = models.CharField(max_length=100)  # SKU or custom code
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    quantity = models.DecimalField(max_digits=15, decimal_places=3, default=0)
    unit = models.CharField(max_length=50, default='pieces')
    unit_cost = models.DecimalField(max_digits=15, decimal_places=2, null=True)
    status = models.CharField(max_length=50, default='active')
    location = models.ForeignKey('locations.Location', on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['tenant', 'code']
        indexes = [
            models.Index(fields=['tenant', 'item_type']),
            models.Index(fields=['tenant', 'status']),
            models.Index(fields=['tenant', 'location']),
        ]

class ItemCustomFieldValue(models.Model):
    """Stores custom field values for items"""
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='custom_values')
    custom_field = models.ForeignKey(CustomField, on_delete=models.CASCADE)
    value_text = models.TextField(null=True)
    value_number = models.DecimalField(max_digits=15, decimal_places=3, null=True)
    value_date = models.DateField(null=True)
    value_datetime = models.DateTimeField(null=True)
    value_boolean = models.BooleanField(null=True)
    value_json = models.JSONField(null=True)  # For multiselect
    
    class Meta:
        unique_together = ['item', 'custom_field']
```

**Key Interfaces**:
- `ItemManager`: Custom manager with tenant filtering and search
- `CustomFieldValidator`: Validates custom field values
- `ItemSerializer`: Serializes items with custom fields for API


### 5. Locations App

**Purpose**: Manage storage locations with hierarchical structure

**Key Models**:

```python
class Location(models.Model):
    """Represents a physical or logical storage location"""
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    location_type = models.CharField(max_length=50)  # warehouse, room, shelf, bin
    parent = models.ForeignKey('self', null=True, on_delete=models.SET_NULL, related_name='children')
    address = models.TextField(blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True)
    capacity = models.DecimalField(max_digits=15, decimal_places=3, null=True)
    capacity_unit = models.CharField(max_length=50, default='items')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['tenant', 'name']
        indexes = [
            models.Index(fields=['tenant', 'parent']),
            models.Index(fields=['tenant', 'is_active']),
        ]

class LocationCustomFieldValue(models.Model):
    """Custom field values for locations"""
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    custom_field = models.ForeignKey('items.CustomField', on_delete=models.CASCADE)
    value_text = models.TextField(null=True)
    value_number = models.DecimalField(max_digits=15, decimal_places=3, null=True)
    value_date = models.DateField(null=True)
    value_boolean = models.BooleanField(null=True)
```

**Key Interfaces**:
- `LocationManager`: Handles hierarchical queries
- `get_full_path()`: Returns complete location path (e.g., "Warehouse A > Aisle 3 > Shelf B")
- `calculate_utilization()`: Calculates current capacity usage


### 6. Transactions App

**Purpose**: Record and process inventory transactions

**Key Models**:

```python
class TransactionType(models.Model):
    """Defines types of inventory transactions"""
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField()
    affects_quantity = models.CharField(max_length=10, choices=[
        ('increase', 'Increase'),
        ('decrease', 'Decrease'),
        ('none', 'No Change')
    ])
    requires_approval = models.BooleanField(default=False)
    icon = models.CharField(max_length=50)
    color = models.CharField(max_length=7)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['tenant', 'name']

class Transaction(models.Model):
    """Records an inventory transaction"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
        ('reversed', 'Reversed'),
    ]
    
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    transaction_type = models.ForeignKey(TransactionType, on_delete=models.PROTECT)
    reference_number = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='transactions_created')
    completed_at = models.DateTimeField(null=True)
    notes = models.TextField(blank=True)
    reversed_transaction = models.ForeignKey('self', null=True, on_delete=models.SET_NULL, related_name='reversal')
    
    class Meta:
        indexes = [
            models.Index(fields=['tenant', 'status']),
            models.Index(fields=['tenant', 'created_at']),
            models.Index(fields=['tenant', 'transaction_type']),
        ]

class TransactionItem(models.Model):
    """Items involved in a transaction"""
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='items')
    item = models.ForeignKey('items.Item', on_delete=models.PROTECT)
    quantity = models.DecimalField(max_digits=15, decimal_places=3)
    unit_cost = models.DecimalField(max_digits=15, decimal_places=2, null=True)
    from_location = models.ForeignKey('locations.Location', null=True, on_delete=models.PROTECT, related_name='transactions_from')
    to_location = models.ForeignKey('locations.Location', null=True, on_delete=models.PROTECT, related_name='transactions_to')
    batch_number = models.CharField(max_length=100, blank=True)
    serial_number = models.CharField(max_length=100, blank=True)
    expiry_date = models.DateField(null=True)

class TransactionApproval(models.Model):
    """Tracks approval workflow for transactions"""
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='approvals')
    approver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ])
    comments = models.TextField(blank=True)
    decided_at = models.DateTimeField(null=True)
```

**Key Interfaces**:
- `TransactionProcessor`: Service class to process transactions
- `validate_transaction()`: Validates transaction before processing
- `process_transaction()`: Updates inventory and creates audit trail
- `reverse_transaction()`: Creates compensating transaction


### 7. Workflows App

**Purpose**: Implement configurable state machine workflows

**Key Models**:

```python
class Workflow(models.Model):
    """Defines a workflow with states and transitions"""
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    description = models.TextField()
    item_type = models.ForeignKey('items.ItemType', on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['tenant', 'name']

class WorkflowState(models.Model):
    """Defines a state in a workflow"""
    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE, related_name='states')
    name = models.CharField(max_length=100)
    description = models.TextField()
    is_initial = models.BooleanField(default=False)
    is_final = models.BooleanField(default=False)
    color = models.CharField(max_length=7)
    time_limit_hours = models.IntegerField(null=True)  # Alert if item stays too long
    
    class Meta:
        unique_together = ['workflow', 'name']

class WorkflowTransition(models.Model):
    """Defines allowed transitions between states"""
    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE, related_name='transitions')
    from_state = models.ForeignKey(WorkflowState, on_delete=models.CASCADE, related_name='transitions_from')
    to_state = models.ForeignKey(WorkflowState, on_delete=models.CASCADE, related_name='transitions_to')
    name = models.CharField(max_length=100)
    conditions = models.JSONField(default=dict)  # Conditions that must be met
    required_fields = models.JSONField(default=list)  # Fields required for transition
    auto_create_transaction = models.BooleanField(default=False)
    transaction_type = models.ForeignKey('transactions.TransactionType', null=True, on_delete=models.SET_NULL)
    
class WorkflowTransitionPermission(models.Model):
    """Defines which roles can perform transitions"""
    transition = models.ForeignKey(WorkflowTransition, on_delete=models.CASCADE)
    role = models.ForeignKey('permissions.Role', on_delete=models.CASCADE)

class ItemWorkflowState(models.Model):
    """Tracks current workflow state for items"""
    item = models.OneToOneField('items.Item', on_delete=models.CASCADE, related_name='workflow_state')
    workflow = models.ForeignKey(Workflow, on_delete=models.PROTECT)
    current_state = models.ForeignKey(WorkflowState, on_delete=models.PROTECT)
    entered_state_at = models.DateTimeField(auto_now_add=True)
    
class ItemWorkflowHistory(models.Model):
    """Records workflow state transitions"""
    item = models.ForeignKey('items.Item', on_delete=models.CASCADE, related_name='workflow_history')
    from_state = models.ForeignKey(WorkflowState, on_delete=models.PROTECT, related_name='history_from')
    to_state = models.ForeignKey(WorkflowState, on_delete=models.PROTECT, related_name='history_to')
    transition = models.ForeignKey(WorkflowTransition, on_delete=models.PROTECT)
    transitioned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    transitioned_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
```

**Key Interfaces**:
- `WorkflowEngine`: Service class to execute workflow transitions
- `get_available_transitions(item, user)`: Returns transitions available to user
- `execute_transition(item, transition, user, data)`: Performs state transition
- `validate_transition_conditions()`: Checks if conditions are met


### 8. Notifications App

**Purpose**: Handle multi-channel notifications

**Key Models**:

```python
class NotificationTemplate(models.Model):
    """Templates for notifications"""
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    event_type = models.CharField(max_length=100)  # low_stock, workflow_transition, etc.
    channel = models.CharField(max_length=20, choices=[
        ('email', 'Email'),
        ('in_app', 'In-App'),
        ('webhook', 'Webhook')
    ])
    subject_template = models.CharField(max_length=255)
    body_template = models.TextField()
    is_active = models.BooleanField(default=True)

class Notification(models.Model):
    """Individual notification instance"""
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    event_type = models.CharField(max_length=100)
    title = models.CharField(max_length=255)
    message = models.TextField()
    link = models.URLField(blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['user', 'created_at']),
        ]

class UserNotificationPreference(models.Model):
    """User preferences for notifications"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event_type = models.CharField(max_length=100)
    email_enabled = models.BooleanField(default=True)
    in_app_enabled = models.BooleanField(default=True)
    webhook_enabled = models.BooleanField(default=False)
    
class WebhookEndpoint(models.Model):
    """Webhook endpoints for external integrations"""
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    url = models.URLField()
    secret = models.CharField(max_length=64)  # For HMAC signature
    event_types = models.JSONField(default=list)
    is_active = models.BooleanField(default=True)
```

**Key Interfaces**:
- `NotificationService`: Service class to send notifications
- `send_notification(users, event_type, context)`: Sends notifications
- `WebhookDelivery`: Celery task for async webhook delivery


### 9. Reports App

**Purpose**: Generate reports and dashboards

**Key Models**:

```python
class ReportDefinition(models.Model):
    """Defines a report template"""
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    description = models.TextField()
    report_type = models.CharField(max_length=50)  # inventory, transactions, etc.
    query_config = models.JSONField()  # Stores query parameters
    is_public = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

class ScheduledReport(models.Model):
    """Scheduled report execution"""
    report_definition = models.ForeignKey(ReportDefinition, on_delete=models.CASCADE)
    schedule = models.CharField(max_length=20, choices=[
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly')
    ])
    recipients = models.JSONField()  # List of email addresses
    is_active = models.BooleanField(default=True)
    last_run = models.DateTimeField(null=True)
    next_run = models.DateTimeField()

class DashboardWidget(models.Model):
    """User dashboard widget configuration"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    widget_type = models.CharField(max_length=50)  # chart, table, kpi, etc.
    config = models.JSONField()  # Widget-specific configuration
    position_x = models.IntegerField()
    position_y = models.IntegerField()
    width = models.IntegerField()
    height = models.IntegerField()
```

**Key Interfaces**:
- `ReportGenerator`: Service class to generate reports
- `DashboardService`: Provides dashboard data
- `generate_report_task`: Celery task for async report generation


### 10. Core App

**Purpose**: Shared utilities and base classes

**Key Components**:

```python
class TenantAwareModel(models.Model):
    """Abstract base model for tenant-aware models"""
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    
    objects = TenantManager()  # Custom manager
    
    class Meta:
        abstract = True

class TenantManager(models.Manager):
    """Manager that automatically filters by current tenant"""
    def get_queryset(self):
        tenant = get_current_tenant()
        if tenant:
            return super().get_queryset().filter(tenant=tenant)
        return super().get_queryset()

class AuditLog(models.Model):
    """Immutable audit log for all changes"""
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=50)  # create, update, delete
    model_name = models.CharField(max_length=100)
    object_id = models.CharField(max_length=100)
    changes = models.JSONField()  # Before/after values
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['tenant', 'created_at']),
            models.Index(fields=['tenant', 'model_name', 'object_id']),
            models.Index(fields=['tenant', 'user']),
        ]

class FileAttachment(models.Model):
    """Generic file attachment model"""
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    file = models.FileField(upload_to='attachments/%Y/%m/%d/')
    filename = models.CharField(max_length=255)
    file_size = models.BigIntegerField()
    content_type = models.CharField(max_length=100)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    # Generic foreign key for attaching to any model
    content_type_fk = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField()
    content_object = GenericForeignKey('content_type_fk', 'object_id')
```

**Key Utilities**:
- `get_current_tenant()`: Thread-local storage for current tenant
- `AuditLogMiddleware`: Automatically logs all model changes
- `TenantMiddleware`: Sets current tenant from request
- `CustomFieldMixin`: Mixin for models with custom fields


## Data Models

### Entity Relationship Diagram

```
┌─────────────┐
│   Tenant    │
└──────┬──────┘
       │
       ├──────────────────────────────────────────────┐
       │                                              │
       ▼                                              ▼
┌─────────────┐                              ┌──────────────┐
│    User     │◄─────────────────────────────│     Role     │
└──────┬──────┘                              └──────┬───────┘
       │                                              │
       │                                              ▼
       │                                      ┌──────────────┐
       │                                      │  Permission  │
       │                                      └──────────────┘
       │
       ▼
┌─────────────┐         ┌──────────────┐
│  ItemType   │◄────────│ CustomField  │
└──────┬──────┘         └──────────────┘
       │
       ▼
┌─────────────┐         ┌──────────────┐
│    Item     │◄────────│   Location   │
└──────┬──────┘         └──────────────┘
       │
       ├──────────────────┬──────────────────┐
       │                  │                  │
       ▼                  ▼                  ▼
┌─────────────┐   ┌──────────────┐   ┌──────────────┐
│ Transaction │   │   Workflow   │   │ CustomField  │
│             │   │    State     │   │    Value     │
└─────────────┘   └──────────────┘   └──────────────┘
```

### Database Indexes Strategy

**Primary Indexes**:
- All foreign keys automatically indexed
- Composite indexes on (tenant, frequently_queried_field)
- Indexes on datetime fields for range queries

**Search Optimization**:
- Full-text indexes on Item.name, Item.description
- GIN indexes on JSONField columns for custom field queries

**Performance Considerations**:
- Partition large tables (AuditLog, Transaction) by tenant or date
- Use database connection pooling (Django's CONN_MAX_AGE)
- Implement query result caching with Redis


## API Design

### REST API Structure

**Base URL**: `/api/v1/`

**Authentication**: 
- Session-based for web UI
- Token-based (JWT) for API clients
- API key for service-to-service

**Endpoints**:

```
# Items
GET    /api/v1/items/                    # List items (paginated, filterable)
POST   /api/v1/items/                    # Create item
GET    /api/v1/items/{id}/               # Get item details
PUT    /api/v1/items/{id}/               # Update item
PATCH  /api/v1/items/{id}/               # Partial update
DELETE /api/v1/items/{id}/               # Delete item
POST   /api/v1/items/bulk/               # Bulk create/update
GET    /api/v1/items/{id}/history/       # Get item history

# Item Types
GET    /api/v1/item-types/               # List item types
POST   /api/v1/item-types/               # Create item type
GET    /api/v1/item-types/{id}/          # Get item type
PUT    /api/v1/item-types/{id}/          # Update item type
DELETE /api/v1/item-types/{id}/          # Delete item type

# Transactions
GET    /api/v1/transactions/             # List transactions
POST   /api/v1/transactions/             # Create transaction
GET    /api/v1/transactions/{id}/        # Get transaction
POST   /api/v1/transactions/{id}/reverse/ # Reverse transaction
POST   /api/v1/transactions/{id}/approve/ # Approve transaction
POST   /api/v1/transactions/{id}/reject/  # Reject transaction

# Locations
GET    /api/v1/locations/                # List locations
POST   /api/v1/locations/                # Create location
GET    /api/v1/locations/{id}/           # Get location
PUT    /api/v1/locations/{id}/           # Update location
GET    /api/v1/locations/{id}/tree/      # Get location hierarchy

# Workflows
GET    /api/v1/workflows/                # List workflows
POST   /api/v1/workflows/                # Create workflow
GET    /api/v1/workflows/{id}/           # Get workflow
POST   /api/v1/items/{id}/transition/    # Execute workflow transition

# Reports
GET    /api/v1/reports/                  # List report definitions
POST   /api/v1/reports/                  # Create report
POST   /api/v1/reports/{id}/generate/    # Generate report
GET    /api/v1/reports/{id}/download/    # Download report

# Dashboard
GET    /api/v1/dashboard/widgets/        # Get user's dashboard widgets
POST   /api/v1/dashboard/widgets/        # Add widget
PUT    /api/v1/dashboard/widgets/{id}/   # Update widget
DELETE /api/v1/dashboard/widgets/{id}/   # Remove widget

# Users & Permissions
GET    /api/v1/users/                    # List users
POST   /api/v1/users/                    # Create user
GET    /api/v1/users/{id}/               # Get user
PUT    /api/v1/users/{id}/               # Update user
GET    /api/v1/roles/                    # List roles
POST   /api/v1/roles/                    # Create role
```

**Response Format**:

```json
{
  "success": true,
  "data": { ... },
  "meta": {
    "page": 1,
    "page_size": 25,
    "total_count": 150,
    "total_pages": 6
  }
}
```

**Error Format**:

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "quantity": ["This field must be a positive number"]
    }
  }
}
```

**Filtering & Search**:
- Query parameters: `?search=keyword&item_type=uuid&status=active&page=1&page_size=25`
- Sorting: `?ordering=-created_at,name`
- Field selection: `?fields=id,name,quantity`

**Rate Limiting**:
- 1000 requests per hour per API key
- 100 requests per minute for bulk operations
- Headers: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`


## Frontend Architecture

### Technology Choices

- **HTML5**: Semantic markup with accessibility support
- **CSS3**: Modern CSS with CSS Grid and Flexbox
- **JavaScript (ES6+)**: Vanilla JS with minimal dependencies
- **AJAX**: Fetch API for asynchronous requests
- **Django Templates**: Server-side rendering for initial page load

### UI Component Structure

```
templates/
├── base.html                    # Base template with common layout
├── components/
│   ├── navbar.html             # Navigation bar
│   ├── sidebar.html            # Sidebar menu
│   ├── pagination.html         # Pagination component
│   ├── modal.html              # Modal dialog
│   └── table.html              # Data table
├── items/
│   ├── item_list.html          # Item listing page
│   ├── item_detail.html        # Item detail page
│   ├── item_form.html          # Item create/edit form
│   └── item_search.html        # Advanced search
├── transactions/
│   ├── transaction_list.html
│   ├── transaction_form.html
│   └── transaction_detail.html
├── dashboard/
│   └── dashboard.html          # Main dashboard
└── auth/
    ├── login.html
    └── password_reset.html

static/
├── css/
│   ├── base.css                # Base styles
│   ├── components.css          # Component styles
│   ├── forms.css               # Form styles
│   └── responsive.css          # Responsive breakpoints
├── js/
│   ├── app.js                  # Main application JS
│   ├── api.js                  # API client wrapper
│   ├── components/
│   │   ├── datatable.js        # Interactive data tables
│   │   ├── modal.js            # Modal dialogs
│   │   ├── notifications.js    # Toast notifications
│   │   └── charts.js           # Chart rendering
│   └── pages/
│       ├── items.js            # Item-specific JS
│       ├── transactions.js     # Transaction-specific JS
│       └── dashboard.js        # Dashboard widgets
└── img/
    └── icons/                  # SVG icons
```

### JavaScript Architecture

**Module Pattern**:

```javascript
// api.js - API client
const API = {
    baseURL: '/api/v1',
    
    async request(endpoint, options = {}) {
        const response = await fetch(`${this.baseURL}${endpoint}`, {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCSRFToken(),
                ...options.headers
            }
        });
        return response.json();
    },
    
    getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]').value;
    },
    
    items: {
        list: (params) => API.request(`/items/?${new URLSearchParams(params)}`),
        get: (id) => API.request(`/items/${id}/`),
        create: (data) => API.request('/items/', { method: 'POST', body: JSON.stringify(data) }),
        update: (id, data) => API.request(`/items/${id}/`, { method: 'PUT', body: JSON.stringify(data) }),
        delete: (id) => API.request(`/items/${id}/`, { method: 'DELETE' })
    }
};

// components/datatable.js - Reusable data table
class DataTable {
    constructor(element, options) {
        this.element = element;
        this.options = options;
        this.currentPage = 1;
        this.init();
    }
    
    async init() {
        await this.loadData();
        this.attachEventListeners();
    }
    
    async loadData() {
        const data = await this.options.dataSource({
            page: this.currentPage,
            page_size: this.options.pageSize
        });
        this.render(data);
    }
    
    render(data) {
        // Render table rows
    }
}
```

### CSS Architecture

**BEM Methodology**:

```css
/* Block */
.item-card {
    border: 1px solid #ddd;
    border-radius: 4px;
    padding: 16px;
}

/* Element */
.item-card__title {
    font-size: 18px;
    font-weight: bold;
}

/* Modifier */
.item-card--highlighted {
    border-color: #007bff;
    background-color: #f0f8ff;
}
```

**CSS Variables for Theming**:

```css
:root {
    --primary-color: #007bff;
    --secondary-color: #6c757d;
    --success-color: #28a745;
    --danger-color: #dc3545;
    --warning-color: #ffc107;
    
    --font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    --border-radius: 4px;
    --spacing-unit: 8px;
}
```

### Progressive Enhancement

1. **Base Layer**: Server-rendered HTML works without JavaScript
2. **Enhancement Layer**: JavaScript adds interactivity (AJAX, real-time updates)
3. **Accessibility**: ARIA labels, keyboard navigation, screen reader support


## Error Handling

### Error Categories

1. **Validation Errors**: Invalid input data
2. **Permission Errors**: Unauthorized access attempts
3. **Business Logic Errors**: Violations of business rules
4. **System Errors**: Database failures, external service failures

### Error Handling Strategy

**Django Views**:

```python
from django.core.exceptions import ValidationError, PermissionDenied
from django.db import transaction

class ItemCreateView(View):
    def post(self, request):
        try:
            with transaction.atomic():
                # Validate input
                form = ItemForm(request.POST)
                if not form.is_valid():
                    return JsonResponse({
                        'success': False,
                        'error': {
                            'code': 'VALIDATION_ERROR',
                            'message': 'Invalid input data',
                            'details': form.errors
                        }
                    }, status=400)
                
                # Check permissions
                if not has_permission(request.user, 'items.create'):
                    raise PermissionDenied("You don't have permission to create items")
                
                # Business logic
                item = form.save(commit=False)
                item.tenant = get_current_tenant()
                item.created_by = request.user
                item.save()
                
                return JsonResponse({
                    'success': True,
                    'data': ItemSerializer(item).data
                }, status=201)
                
        except PermissionDenied as e:
            return JsonResponse({
                'success': False,
                'error': {
                    'code': 'PERMISSION_DENIED',
                    'message': str(e)
                }
            }, status=403)
            
        except ValidationError as e:
            return JsonResponse({
                'success': False,
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': 'Validation failed',
                    'details': e.message_dict
                }
            }, status=400)
            
        except Exception as e:
            logger.exception("Unexpected error creating item")
            return JsonResponse({
                'success': False,
                'error': {
                    'code': 'INTERNAL_ERROR',
                    'message': 'An unexpected error occurred'
                }
            }, status=500)
```

**Custom Exception Classes**:

```python
class InventoryException(Exception):
    """Base exception for inventory operations"""
    pass

class InsufficientQuantityError(InventoryException):
    """Raised when trying to decrease quantity below zero"""
    pass

class WorkflowTransitionError(InventoryException):
    """Raised when workflow transition is not allowed"""
    pass

class TenantIsolationError(InventoryException):
    """Raised when cross-tenant access is attempted"""
    pass
```

**Frontend Error Handling**:

```javascript
async function createItem(data) {
    try {
        const response = await API.items.create(data);
        
        if (response.success) {
            showNotification('Item created successfully', 'success');
            return response.data;
        } else {
            handleAPIError(response.error);
        }
    } catch (error) {
        showNotification('Network error. Please try again.', 'error');
        console.error('Error creating item:', error);
    }
}

function handleAPIError(error) {
    switch (error.code) {
        case 'VALIDATION_ERROR':
            displayValidationErrors(error.details);
            break;
        case 'PERMISSION_DENIED':
            showNotification(error.message, 'error');
            break;
        default:
            showNotification('An error occurred. Please try again.', 'error');
    }
}
```

### Logging Strategy

**Log Levels**:
- **DEBUG**: Detailed diagnostic information
- **INFO**: General informational messages
- **WARNING**: Warning messages for potentially harmful situations
- **ERROR**: Error messages for serious problems
- **CRITICAL**: Critical messages for very serious errors

**Logging Configuration**:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/inventory/app.log',
            'maxBytes': 1024 * 1024 * 100,  # 100 MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/inventory/error.log',
            'maxBytes': 1024 * 1024 * 100,
            'backupCount': 10,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
        'apps': {
            'handlers': ['file', 'error_file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
```


## Testing Strategy

### Testing Approach

The platform will use a dual testing approach combining unit tests and property-based tests:

**Unit Tests**:
- Test specific examples and edge cases
- Test integration points between components
- Test error conditions and validation logic
- Use Django's built-in testing framework

**Property-Based Tests**:
- Test universal properties across all inputs
- Use Hypothesis library for Python property-based testing
- Each property test runs minimum 100 iterations
- Focus on invariants, round-trip properties, and business rules

### Test Organization

```
tests/
├── unit/
│   ├── test_models.py
│   ├── test_views.py
│   ├── test_api.py
│   └── test_services.py
├── integration/
│   ├── test_transaction_flow.py
│   ├── test_workflow_engine.py
│   └── test_multi_tenant.py
├── properties/
│   ├── test_tenant_isolation.py
│   ├── test_inventory_math.py
│   ├── test_workflow_transitions.py
│   └── test_data_integrity.py
└── fixtures/
    ├── tenants.json
    ├── users.json
    └── items.json
```

### Property-Based Testing Configuration

```python
from hypothesis import given, settings, strategies as st

# Configure Hypothesis
settings.register_profile("ci", max_examples=100, deadline=None)
settings.register_profile("dev", max_examples=20, deadline=None)
settings.load_profile("ci")
```


## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Tenant Data Isolation

*For any* two different tenants and any database query, the query results for one tenant should never include data belonging to the other tenant.

**Validates: Requirements 2.1, 2.4**

### Property 2: Item Code Uniqueness Within Tenant

*For any* tenant, all items within that tenant should have unique item codes, but items in different tenants may have the same codes.

**Validates: Requirements 9.3**

### Property 3: Transaction Quantity Arithmetic

*For any* item and any sequence of transactions, the final quantity should equal the initial quantity plus all increases minus all decreases.

**Validates: Requirements 11.2, 11.3**

### Property 4: Non-Negative Inventory

*For any* item, attempting a transaction that would result in negative quantity should be rejected with an error.

**Validates: Requirements 18.5**

### Property 5: Transaction Atomicity

*For any* transaction involving multiple items, either all item quantities are updated or none are updated (no partial updates).

**Validates: Requirements 19.4**

### Property 6: Transaction Reversal Round-Trip

*For any* completed transaction, creating a reversal transaction should restore all affected items to their pre-transaction quantities and locations.

**Validates: Requirements 21.4**

### Property 7: Hierarchy Acyclicity (Item Types)

*For any* item type hierarchy, following parent references should never form a cycle.

**Validates: Requirements 5.3**

### Property 8: Hierarchy Acyclicity (Locations)

*For any* location hierarchy, following parent references should never form a cycle.

**Validates: Requirements 36.3**

### Property 9: Workflow Transition Validity

*For any* item in a workflow state, only transitions defined from that state should be available, and executing an undefined transition should be rejected.

**Validates: Requirements 26.3**

### Property 10: Required Field Validation

*For any* item type with required custom fields, attempting to create an item without values for all required fields should be rejected.

**Validates: Requirements 6.6**

### Property 11: Permission Enforcement

*For any* user and any action, if the user's roles do not grant the required permission, the action should be denied with a permission error.

**Validates: Requirements 33.1**

### Property 12: Custom Field Type Validation

*For any* custom field with a specific data type, attempting to store a value that doesn't match the data type should be rejected.

**Validates: Requirements 7.3**

### Property 13: Import-Export Round-Trip

*For any* set of items, exporting them to CSV/JSON and then importing the exported data should produce equivalent items with the same attributes.

**Validates: Requirements 95.1, 99.1**

### Property 14: Role Permission Inheritance

*For any* role with a parent role, the child role should have at least all the permissions of the parent role.

**Validates: Requirements 31.2**

### Property 15: Audit Log Immutability

*For any* audit log entry, once created, it should never be modified or deleted through normal application operations.

**Validates: Requirements 59.6**


## Security Considerations

### Authentication

- Password hashing using Django's PBKDF2 algorithm
- Optional multi-factor authentication (TOTP)
- Session management with secure cookies (HttpOnly, Secure, SameSite)
- Account lockout after failed login attempts
- Password complexity requirements enforced

### Authorization

- Role-based access control (RBAC) at all layers
- Permission checks in views, API endpoints, and model managers
- Tenant context validation on every request
- Row-level security through custom model managers

### Data Protection

- TLS 1.3 for all connections
- AES-256 encryption for sensitive data at rest
- Tenant-specific encryption keys
- Secure file upload handling with virus scanning
- SQL injection prevention through Django ORM
- XSS prevention through template auto-escaping
- CSRF protection on all state-changing operations

### Audit and Compliance

- Immutable audit logs for all data changes
- User action tracking with IP address and user agent
- Compliance reporting capabilities
- Data retention policies
- GDPR-compliant data export and deletion

## Performance Optimization

### Database Optimization

- Appropriate indexes on foreign keys and frequently queried fields
- Composite indexes for multi-column queries
- Query optimization using select_related() and prefetch_related()
- Database connection pooling
- Read replicas for reporting queries

### Caching Strategy

- Redis for session storage
- Cache frequently accessed configuration data
- Cache user permissions (15-minute TTL)
- Cache dashboard widget data (30-second TTL)
- Cache invalidation on data updates

### Asynchronous Processing

- Celery for background tasks:
  - Report generation
  - Bulk data import/export
  - Email notifications
  - Webhook deliveries
- Celery Beat for scheduled tasks:
  - Scheduled reports
  - Low stock alerts
  - Workflow time limit checks

### Frontend Optimization

- Minified and bundled CSS/JS
- Lazy loading for large data tables
- Pagination for all list views
- Debounced search inputs
- Progressive enhancement for better perceived performance

## Deployment Architecture

### Production Environment

```
┌─────────────────┐
│   Load Balancer │
│     (Nginx)     │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
┌───▼───┐ ┌──▼────┐
│ Web 1 │ │ Web 2 │  (Gunicorn + Django)
└───┬───┘ └──┬────┘
    │         │
    └────┬────┘
         │
    ┌────▼────┐
    │  MySQL  │
    │ Primary │
    └────┬────┘
         │
    ┌────▼────┐
    │  MySQL  │
    │ Replica │
    └─────────┘

┌─────────────┐
│    Redis    │  (Cache + Sessions)
└─────────────┘

┌─────────────┐
│   Celery    │  (Background Workers)
│   Workers   │
└─────────────┘
```

### Scalability Considerations

- Horizontal scaling of web servers behind load balancer
- Database read replicas for query distribution
- Redis cluster for distributed caching
- Celery workers can be scaled independently
- File storage on S3 or compatible object storage
- CDN for static assets

## Migration and Deployment Strategy

### Database Migrations

- Use Django migrations for schema changes
- Test migrations on staging environment first
- Backup database before production migrations
- Support for zero-downtime migrations using:
  - Additive changes first (add columns, tables)
  - Deploy code that works with both old and new schema
  - Remove old schema elements in subsequent release

### Deployment Process

1. Run automated tests (unit, integration, property tests)
2. Build and tag Docker images
3. Deploy to staging environment
4. Run smoke tests on staging
5. Deploy to production with rolling updates
6. Monitor error rates and performance metrics
7. Rollback capability if issues detected

### Monitoring and Alerting

- Application performance monitoring (APM)
- Error tracking and logging aggregation
- Database performance monitoring
- Infrastructure metrics (CPU, memory, disk)
- Custom business metrics (transactions/hour, active users)
- Alerts for:
  - High error rates
  - Slow response times
  - Database connection pool exhaustion
  - Celery queue backlog
  - Disk space warnings

## Summary

This design provides a comprehensive, scalable architecture for a multi-tenant inventory and logistics management platform. Key design decisions include:

1. **Multi-tenancy**: Row-level isolation with tenant identifier provides good balance of cost, performance, and security
2. **Flexibility**: Custom fields, workflows, and transaction types allow adaptation to diverse industries
3. **Django Framework**: Leverages Django's built-in features (ORM, admin, auth) for rapid development
4. **Property-Based Testing**: Ensures correctness of critical business logic through formal properties
5. **Scalability**: Horizontal scaling, caching, and asynchronous processing support growth
6. **Security**: Multiple layers of security from authentication to data encryption
7. **Maintainability**: Clean architecture, comprehensive logging, and monitoring

The design addresses all 120 requirements while maintaining simplicity and following Django best practices.
