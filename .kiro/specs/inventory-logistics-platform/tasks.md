# Implementation Plan: Omnify - Universal Operations Platform

## Overview

This implementation plan breaks down the development of Omnify into discrete, manageable tasks. The approach follows an incremental development strategy, building core functionality first and then adding advanced features. Each task builds on previous work, ensuring the system remains functional at each stage.

## Status Legend

| Symbol | Meaning |
|--------|---------|
| ✅ | Completed |
| 🔄 | Partially completed — needs finishing |
| ⬜ | Not started |
| `*` | Optional — can be skipped for faster MVP |

---

## Phase 1: Foundation & Infrastructure

- ✅ 1. Project Setup and Core Infrastructure
  - ✅ Set up Django project structure with apps (tenants, users, items, transactions, workflows, locations, permissions, notifications, reports, core, api)
  - ✅ Configure MySQL database connection
  - ✅ Set up Redis for caching (configured, using LocMemCache for MVP)
  - ✅ Configure Celery for background tasks (configured, not active for MVP)
  - ✅ Create base settings files (base.py, development.py, production.py)
  - ✅ Set up static files and media handling
  - ✅ Configure logging (rotating file handler, 100MB, 10 backups)
  - _Requirements: Technical Constraints_

- ⬜* 1.1 Write unit tests for project configuration
  - ⬜ Test database connectivity
  - ⬜ Test Redis connectivity
  - ⬜ Test static file serving
  - _Requirements: Technical Constraints_

- ✅ 2. Implement Core App and Multi-Tenancy Foundation
  - ✅ 2.1 Create Tenant model with basic fields
    - ✅ Implement TenantAwareModel abstract base class
    - ✅ Create TenantManager custom manager with automatic tenant filtering
    - ✅ Implement get_current_tenant() utility using thread-local storage
    - _Requirements: 1.1, 1.2, 2.1_

  - ✅ 2.2 Create TenantMiddleware
    - ✅ Extract tenant from subdomain or header (X-Tenant-Slug)
    - ✅ Set current tenant in thread-local storage
    - ✅ Handle tenant not found errors (403 Forbidden)
    - ✅ Define public paths exemption list
    - _Requirements: 2.2_

  - ✅ 2.3 Create AuditLog model
    - ✅ Implement immutable audit logging for all model changes (UUID, tenant, user, action, changes)
    - ✅ Create AuditLogMiddleware to automatically capture IP and User-Agent
    - _Requirements: 59.1, 59.6_

  - ⬜* 2.4 Write property test for tenant isolation
    - **Property 1: Tenant Data Isolation**
    - **Validates: Requirements 2.1, 2.4**
    - Generate multiple tenants with data
    - Verify queries never return cross-tenant data
    - _Requirements: 2.1, 2.4_

- ⬜ 3. Checkpoint - Verify multi-tenancy foundation
  - ⬜ Create conftest.py with test fixtures
  - ⬜ Ensure all tests pass, ask the user if questions arise.

---

## Phase 2: Authentication & Access Control

- 🔄 4. Implement Users and Authentication
  - ✅ 4.1 Create custom User model
    - ✅ Extend AbstractBaseUser with tenant foreign key
    - ✅ Add email, name, phone, MFA fields (mfa_enabled, mfa_secret)
    - ✅ Create UserManager with create_user/create_superuser
    - ✅ Implement account locking (failed_login_attempts, locked_until, is_locked())
    - ✅ Create UserSession model for session tracking
    - _Requirements: 73.1, 73.2_

  - 🔄 4.2 Implement authentication system
    - ⬜ Create CustomAuthBackend for email-based login
    - ⬜ Implement password validation with complexity requirements
    - ⬜ Create login, logout views
    - ⬜ Implement session management views
    - _Note: User model exists but auth views are not implemented_
    - _Requirements: 74.1, 74.2, 77.1_

  - ⬜ 4.3 Implement password reset functionality
    - ⬜ Create password reset request view
    - ⬜ Generate time-limited reset tokens
    - ⬜ Create password reset confirmation view
    - ⬜ Send reset emails
    - _Requirements: 75.1, 75.2, 75.3_

  - ⬜ 4.4 Implement multi-factor authentication (MFA)
    - ⬜ Add TOTP support using pyotp library (pyotp installed, fields exist on User model)
    - ⬜ Create MFA setup view with QR code (qrcode library installed)
    - ⬜ Create MFA verification view
    - ⬜ Generate backup codes
    - _Requirements: 76.1, 76.2, 76.3_

  - ⬜* 4.5 Write unit tests for authentication
    - ⬜ Test login with valid/invalid credentials
    - ⬜ Test password reset flow
    - ⬜ Test MFA setup and verification
    - ⬜ Test account lockout after failed attempts
    - _Requirements: 73.1, 74.1, 75.1, 76.1, 78.1_

- ⬜ 5. Implement Permissions and RBAC
  - ⬜ 5.1 Create Role and Permission models
    - ⬜ Create Role model with tenant and parent fields
    - ⬜ Create Permission model with resource and action
    - ⬜ Create RolePermission mapping model
    - ⬜ Create UserRole assignment model
    - _Note: App exists as stub, models not implemented_
    - _Requirements: 29.1, 30.1, 31.1, 32.1_

  - ⬜ 5.2 Implement permission checking system
    - ⬜ Create PermissionChecker service class
    - ⬜ Implement has_permission() function
    - ⬜ Create @require_permission decorator for views
    - _Requirements: 33.1_

  - ⬜* 5.3 Write property test for permission enforcement
    - **Property 11: Permission Enforcement**
    - **Validates: Requirements 33.1**
    - Generate users with various role combinations
    - Verify actions are denied without proper permissions
    - _Requirements: 33.1_

  - ⬜* 5.4 Write property test for role inheritance
    - **Property 14: Role Permission Inheritance**
    - **Validates: Requirements 31.2**
    - Generate role hierarchies
    - Verify child roles have all parent permissions
    - _Requirements: 31.2_

- ⬜ 6. Checkpoint - Verify authentication and permissions
  - ⬜ Ensure all tests pass, ask the user if questions arise.

---

## Phase 3: Core Data Models

- ✅ 7. Implement Locations App
  - ✅ 7.1 Create Location model
    - ✅ Add tenant, name, code (auto-generated), type, parent fields
    - ✅ Add capacity, capacity_unit, address, coordinates fields
    - ✅ Implement hierarchical structure support (self-referencing FK)
    - ✅ Location types: warehouse, building, floor, room, aisle, shelf, bin, zone, other
    - _Requirements: 35.1, 36.1_

  - ✅ 7.2 Implement location hierarchy utilities
    - ✅ Create get_full_path() method (e.g., "Warehouse > Aisle > Shelf")
    - ✅ Create get_ancestors() and get_descendants() methods
    - ✅ Implement cycle detection (has_cycle()) for parent relationships
    - ✅ Override save() to validate no cycles and auto-generate code
    - _Requirements: 36.2, 36.3_

  - ✅ 7.3 Implement location capacity tracking
    - ✅ Create calculate_utilization() method (returns percentage used)
    - ⬜ Add capacity warning thresholds
    - _Requirements: 37.1, 37.2_

  - ⬜* 7.4 Write property test for location hierarchy acyclicity
    - **Property 8: Hierarchy Acyclicity (Locations)**
    - **Validates: Requirements 36.3**
    - Generate random location hierarchies
    - Verify no cycles exist
    - _Requirements: 36.3_

  - ⬜* 7.5 Write unit tests for location operations
    - ⬜ Test location creation and hierarchy
    - ⬜ Test capacity calculations
    - ⬜ Test cycle prevention
    - _Requirements: 35.1, 36.3, 37.1_

- ✅ 8. Implement Items App - Core Models
  - ✅ 8.1 Create ItemType model
    - ✅ Add tenant, name, description, parent (self-FK), icon fields
    - ✅ Implement hierarchical structure support
    - ✅ Unique constraint: (tenant, name)
    - _Requirements: 4.1, 5.1_

  - ✅ 8.2 Create CustomField model
    - ✅ Add item_type, name, field_type fields
    - ✅ Support all 9 data types: text, number, date, datetime, boolean, dropdown, multiselect, file, url
    - ✅ Add validation rules (JSON), dropdown options (JSON), help_text, display_order
    - ✅ Add is_required, is_searchable, default_value flags
    - _Requirements: 6.1, 6.2_

  - ✅ 8.3 Create Item model
    - ✅ Add tenant, item_type, code, name, description fields
    - ✅ Add quantity (decimal), unit, unit_cost, selling_price, reorder_point, reorder_quantity
    - ✅ Add location FK, status (active/inactive/discontinued/pending)
    - ✅ Ensure code uniqueness within tenant via unique constraint
    - ✅ Implement is_low_stock() method
    - ✅ Indexes: (tenant, item_type), (tenant, status), (tenant, location), (tenant, code)
    - _Requirements: 9.1, 9.2, 9.3, 11.1_

  - ✅ 8.4 Create ItemCustomFieldValue model
    - ✅ Support storing values for all custom field types via polymorphic columns
    - ✅ Add value_text, value_number, value_date, value_datetime, value_boolean, value_json fields
    - ✅ Implement get_value() method based on field type
    - ✅ Unique constraint: (item, custom_field)
    - _Requirements: 6.1_

  - ⬜* 8.5 Write property test for item code uniqueness
    - **Property 2: Item Code Uniqueness Within Tenant**
    - **Validates: Requirements 9.3**
    - Generate items with random codes
    - Verify uniqueness within tenant, allow duplicates across tenants
    - _Requirements: 9.3_

  - ⬜* 8.6 Write property test for item type hierarchy acyclicity
    - **Property 7: Hierarchy Acyclicity (Item Types)**
    - **Validates: Requirements 5.3**
    - Generate random item type hierarchies
    - Verify no cycles exist
    - _Requirements: 5.3_

- ⬜ 9. Implement Items App - Custom Fields and Validation
  - ⬜ 9.1 Create CustomFieldValidator service
    - ⬜ Implement validation for each data type
    - ⬜ Validate min/max constraints
    - ⬜ Validate dropdown options
    - ⬜ Validate file types and sizes
    - ⬜ Validate URL format
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7_

  - ⬜ 9.2 Implement required field validation
    - ⬜ Check required fields during item creation
    - ⬜ Validate custom field values match their types
    - _Requirements: 6.6_

  - ⬜* 9.3 Write property test for required field validation
    - **Property 10: Required Field Validation**
    - **Validates: Requirements 6.6**
    - Generate item types with required fields
    - Verify items without required fields are rejected
    - _Requirements: 6.6_

  - ⬜* 9.4 Write property test for custom field type validation
    - **Property 12: Custom Field Type Validation**
    - **Validates: Requirements 7.3**
    - Generate custom fields with various types
    - Verify invalid values are rejected
    - _Requirements: 7.3_

- ⬜ 10. Checkpoint - Verify items and locations foundation
  - ⬜ Ensure all tests pass, ask the user if questions arise.

---

## Phase 4: Transaction Processing

- ⬜ 11. Implement Transactions App - Core Models
  - ⬜ 11.1 Create TransactionType model
    - Add tenant, name, description fields
    - Add affects_quantity field (increase/decrease/none)
    - Add requires_approval flag
    - _Note: App exists as stub, models not implemented_
    - _Requirements: 16.1, 16.2, 16.3_

  - ⬜ 11.2 Create Transaction model
    - Add tenant, transaction_type, reference_number, status fields
    - Add created_by, created_at, completed_at fields
    - Support draft, pending, approved, rejected, completed, reversed statuses
    - _Requirements: 17.1, 17.2, 17.3_

  - ⬜ 11.3 Create TransactionItem model
    - Add transaction, item, quantity fields
    - Add from_location, to_location fields
    - Add batch_number, serial_number, expiry_date fields
    - _Requirements: 17.4, 17.5, 17.6_

  - ⬜ 11.4 Create TransactionApproval model
    - Add transaction, approver, status, comments fields
    - Track approval workflow
    - _Requirements: 108.4, 108.5_

- ⬜ 12. Implement Transaction Processing Logic
  - ⬜ 12.1 Create TransactionProcessor service
    - Implement validate_transaction() method
    - Check required fields, permissions, item/location existence
    - Validate sufficient quantity for decreases
    - _Requirements: 18.1, 18.2, 18.3, 18.4, 18.5_

  - ⬜ 12.2 Implement process_transaction() method
    - Update item quantities atomically
    - Update item locations
    - Update item status if configured
    - Use database transactions for atomicity
    - Create audit log entries
    - _Requirements: 19.1, 19.2, 19.3, 19.4, 19.6_

  - ⬜ 12.3 Implement transaction reversal
    - Create reverse_transaction() method
    - Generate compensating transaction
    - Link reversal to original transaction
    - Restore quantities and locations
    - _Requirements: 21.1, 21.2, 21.3, 21.4_

  - ⬜* 12.4 Write property test for transaction quantity arithmetic
    - **Property 3: Transaction Quantity Arithmetic**
    - **Validates: Requirements 11.2, 11.3**
    - Generate random transaction sequences
    - Verify final quantity equals initial + increases - decreases
    - _Requirements: 11.2, 11.3_

  - ⬜* 12.5 Write property test for non-negative inventory
    - **Property 4: Non-Negative Inventory**
    - **Validates: Requirements 18.5**
    - Generate transactions that would cause negative quantities
    - Verify they are rejected
    - _Requirements: 18.5_

  - ⬜* 12.6 Write property test for transaction atomicity
    - **Property 5: Transaction Atomicity**
    - **Validates: Requirements 19.4**
    - Simulate failures during transaction processing
    - Verify either all updates succeed or none do
    - _Requirements: 19.4_

  - ⬜* 12.7 Write property test for transaction reversal round-trip
    - **Property 6: Transaction Reversal Round-Trip**
    - **Validates: Requirements 21.4**
    - Generate random transactions
    - Verify reversal restores original state
    - _Requirements: 21.4_

- ⬜ 13. Checkpoint - Verify transaction processing
  - ⬜ Ensure all tests pass, ask the user if questions arise.

---

## Phase 5: Workflows & Notifications

- ⬜ 14. Implement Workflows App
  - ⬜ 14.1 Create Workflow and WorkflowState models
    - Create Workflow model with tenant, name, item_type fields
    - Create WorkflowState model with workflow, name, is_initial, is_final fields
    - Add time_limit_hours for state duration tracking
    - _Note: App exists as stub, models not implemented_
    - _Requirements: 23.1, 23.2, 24.1_

  - ⬜ 14.2 Create WorkflowTransition model
    - Add from_state, to_state, name fields
    - Add conditions and required_fields JSON fields
    - Add auto_create_transaction flag
    - _Requirements: 25.1, 25.3, 25.5_

  - ⬜ 14.3 Create WorkflowTransitionPermission model
    - Map transitions to roles
    - _Requirements: 25.2_

  - ⬜ 14.4 Create ItemWorkflowState and ItemWorkflowHistory models
    - Track current state for each item
    - Record all state transitions
    - _Requirements: 26.1, 27.1_

  - ⬜ 14.5 Implement WorkflowEngine service
    - Create get_available_transitions() method
    - Create execute_transition() method
    - Validate transition conditions
    - Check user permissions
    - Update item state and create history record
    - _Requirements: 26.2, 26.3, 26.4, 26.7_

  - ⬜* 14.6 Write property test for workflow transition validity
    - **Property 9: Workflow Transition Validity**
    - **Validates: Requirements 26.3**
    - Generate workflows with states and transitions
    - Verify only defined transitions are allowed
    - _Requirements: 26.3_

  - ⬜* 14.7 Write unit tests for workflow execution
    - Test state initialization
    - Test transition execution
    - Test condition validation
    - Test permission checks
    - _Requirements: 26.1, 26.3, 26.4_

- ⬜ 15. Implement Notifications App
  - ⬜ 15.1 Create notification models
    - Create NotificationTemplate model
    - Create Notification model
    - Create UserNotificationPreference model
    - Create WebhookEndpoint model
    - _Note: App exists as stub, models not implemented_
    - _Requirements: 82.1, 83.1, 84.1, 88.1_

  - ⬜ 15.2 Implement NotificationService
    - Create send_notification() method
    - Support in-app, email, and webhook channels
    - Respect user preferences
    - _Requirements: 83.1, 84.1, 88.3_

  - ⬜ 15.3 Create Celery tasks for async delivery
    - Create send_email_task
    - Create send_webhook_task with retry logic
    - _Requirements: 84.7, 88.5_

  - ⬜* 15.4 Write unit tests for notifications
    - Test notification creation
    - Test preference filtering
    - Test email sending
    - Test webhook delivery
    - _Requirements: 83.1, 84.1, 88.3_

- ⬜ 16. Checkpoint - Verify workflows and notifications
  - ⬜ Ensure all tests pass, ask the user if questions arise.

---

## Phase 6: Reporting & API

- ⬜ 17. Implement Reports and Dashboard
  - ⬜ 17.1 Create report models
    - Create ReportDefinition model
    - Create ScheduledReport model
    - Create DashboardWidget model
    - _Note: App exists as stub, models not implemented_
    - _Requirements: 49.1, 51.1, 46.1_

  - ⬜ 17.2 Implement ReportGenerator service
    - Support inventory summary reports
    - Support transaction history reports
    - Support location utilization reports
    - Generate CSV, Excel, PDF exports
    - _Requirements: 49.3, 49.5_

  - ⬜ 17.3 Implement DashboardService
    - Provide data for various widget types
    - Calculate inventory metrics
    - Aggregate transaction data
    - _Requirements: 46.1, 47.1, 47.2, 47.3_

  - ⬜ 17.4 Create Celery tasks for scheduled reports
    - Create generate_scheduled_report_task
    - Send reports via email
    - _Requirements: 51.4, 51.5_

  - ⬜* 17.5 Write unit tests for reports
    - Test report generation
    - Test data aggregation
    - Test export formats
    - _Requirements: 49.3, 49.5_

- ⬜ 18. Implement REST API
  - ⬜ 18.1 Set up Django REST Framework
    - ✅ DRF is installed and configured (JWT + Session auth, pagination 25/page)
    - ⬜ Set up rate limiting middleware
    - ⬜ Configure API key authentication
    - _Requirements: 65.1, 66.1, 72.1_

  - ⬜ 18.2 Create API serializers
    - ItemSerializer with custom fields
    - TransactionSerializer
    - LocationSerializer
    - WorkflowSerializer
    - UserSerializer
    - _Requirements: 65.1_

  - ⬜ 18.3 Create API viewsets
    - ItemViewSet with CRUD operations
    - TransactionViewSet with approval actions
    - LocationViewSet with hierarchy endpoints
    - WorkflowViewSet with transition endpoint
    - ReportViewSet with generate action
    - _Requirements: 68.1, 68.2, 68.3_

  - ⬜ 18.4 Implement bulk operations endpoints
    - Bulk create/update items
    - Validate and process in batches
    - Return detailed results
    - _Requirements: 69.1, 69.2, 69.5_

  - ⬜* 18.5 Write API integration tests
    - Test CRUD operations
    - Test authentication and authorization
    - Test filtering and pagination
    - Test bulk operations
    - _Requirements: 65.1, 66.1, 68.1, 69.1_

- ⬜ 19. Checkpoint - Verify API and reports
  - ⬜ Ensure all tests pass, ask the user if questions arise.

---

## Phase 7: Template System & Onboarding (NEW)

- ⬜ 38. Implement Template System - Core Models
  - ⬜ 38.1 Create Template model
    - Add id (UUID), name, slug (unique), description, industry_category fields
    - Add configuration (JSONField) for full template data
    - Add version (semver string), status (draft/active/deprecated)
    - Add usage_count, created_by, created_at, updated_at
    - _See: TEMPLATE_SYSTEM_GUIDE.md, TEMPLATE_SYSTEM_IMPLEMENTATION.md_

  - ⬜ 38.2 Create TemplateApplication model
    - Track which templates were applied to which tenants
    - Add template_id, tenant_id, applied_at, template_version
    - Add customizations_made (JSONField) for post-application changes
    - _See: TEMPLATE_SYSTEM_GUIDE.md_

  - ⬜ 38.3 Create TemplateCategory model
    - Organize templates by industry (hospital, factory, library, etc.)
    - Add name, slug, icon, description, display_order
    - _See: CUSTOMIZATION_APPROACH.md_

- ⬜ 39. Implement Template System - Application Engine
  - ⬜ 39.1 Create TemplateEngine service
    - Implement validate_template(template_json) method
    - Implement apply_template(tenant, template) method
    - Create item types with custom fields from template
    - Create workflows with states and transitions
    - Create transaction types
    - Create location hierarchies
    - Create roles with permissions
    - Configure modules (enable/disable)
    - Apply tenant configuration settings
    - Optionally create sample data
    - _See: TEMPLATE_SYSTEM_GUIDE.md (apply_template_to_tenant code example)_

  - ⬜ 39.2 Implement template versioning
    - Support semantic versioning (major.minor.patch)
    - Track template version at application time
    - Allow template updates without breaking existing tenants
    - _See: TEMPLATE_SYSTEM_GUIDE.md_

  - ⬜ 39.3 Create template cloning from existing tenant
    - Extract configuration from a tenant (exclude actual data)
    - Generalize tenant-specific values
    - Package as reusable template
    - _See: TEMPLATE_SYSTEM_GUIDE.md (Method 3: Clone from Existing Tenant)_

  - ⬜* 39.4 Write unit tests for template application
    - Test template validation
    - Test full template application (item types, workflows, transactions, locations, roles)
    - Test template versioning
    - Test cloning from tenant

- ⬜ 40. Implement Template System - Seed Templates
  - ⬜ 40.1 Create Hospital & Healthcare template
  - ⬜ 40.2 Create Manufacturing & Factory template
  - ⬜ 40.3 Create Warehouse & Distribution template
  - ⬜ 40.4 Create Library & Media template
  - ⬜ 40.5 Create Retail Store template
  - ⬜ 40.6 Create Food & Beverage template
  - ⬜ 40.7 Create Medical Clinic template (see CLINIC_EXAMPLE.md)
  - ⬜ 40.8 Create Education & School template
  - ⬜ 40.9 Create Construction & Equipment template
  - ⬜ 40.10 Create management command: load_seed_templates
  - _See: CUSTOMIZATION_APPROACH.md, CLINIC_EXAMPLE.md, TEMPLATE_SYSTEM_GUIDE.md_

- ⬜ 41. Implement Onboarding Wizard
  - ⬜ 41.1 Create tenant signup flow
    - Registration form (organization name, admin email, password)
    - Email verification
    - Tenant provisioning (create Tenant + TenantConfiguration + admin User)

  - ⬜ 41.2 Create template selection step
    - Display available templates grouped by industry
    - Template preview (show what item types, workflows, modules will be created)
    - "Start from scratch" option

  - ⬜ 41.3 Create configuration wizard
    - Post-template customization step
    - Allow renaming item types, adjusting fields
    - Configure branding (logo, primary color)
    - Set timezone, currency, date format

  - ⬜ 41.4 Create onboarding completion
    - Summary of configured features
    - Quick-start guide / walkthrough
    - Redirect to dashboard

  - ⬜* 41.5 Write integration tests for onboarding
    - Test full signup-to-dashboard flow
    - Test template application during onboarding
    - Test "start from scratch" path

- ⬜ 42. Checkpoint - Verify template system and onboarding
  - ⬜ Ensure all tests pass, ask the user if questions arise.

---

## Phase 8: Financial Management (NEW)

- ⬜ 43. Implement Financial Module - Core Models
  - ⬜ 43.1 Create Invoice model
    - Add tenant, invoice_number (auto-generated), customer_name, customer_email
    - Add status (draft/sent/paid/partially_paid/overdue/cancelled/refunded)
    - Add subtotal, tax_rate, tax_amount, discount, total_amount
    - Add issue_date, due_date, paid_date
    - Add payment_terms, notes, created_by
    - Link to Transaction (optional FK)
    - _See: FINANCIAL_MANAGEMENT_SPEC.md_

  - ⬜ 43.2 Create InvoiceLineItem model
    - Add invoice FK, item FK (optional), description
    - Add quantity, unit_price, discount, tax_rate, line_total
    - Auto-calculate line_total on save

  - ⬜ 43.3 Create Payment model
    - Add tenant, invoice FK, amount, payment_method
    - Add payment_date, reference_number, notes
    - Methods: update invoice status on save (paid/partially_paid)

  - ⬜ 43.4 Create PurchaseOrder model
    - Add tenant, po_number, supplier_name, supplier_email
    - Add status (draft/sent/confirmed/partially_received/received/cancelled)
    - Add order_date, expected_delivery_date, received_date
    - Add subtotal, tax, total, notes

  - ⬜ 43.5 Create PurchaseOrderLineItem model
    - Add purchase_order FK, item FK, description
    - Add ordered_quantity, received_quantity, unit_price, line_total

  - ⬜ 43.6 Create SalesOrder model
    - Add tenant, so_number, customer_name, customer_email
    - Add status (draft/confirmed/processing/partially_fulfilled/fulfilled/shipped/cancelled)
    - Add order_date, required_date, fulfilled_date
    - Add subtotal, tax, total, notes

  - ⬜ 43.7 Create SalesOrderLineItem model
    - Add sales_order FK, item FK, description
    - Add ordered_quantity, fulfilled_quantity, reserved_quantity, unit_price, line_total

- ⬜ 44. Implement Financial Module - Services
  - ⬜ 44.1 Create InvoiceService
    - Generate invoices from transactions or sales orders
    - Auto-calculate totals (subtotal, tax, discount, total)
    - Auto-generate sequential invoice numbers per tenant
    - Generate printable PDF invoices with tenant branding
    - _See: FINANCIAL_MANAGEMENT_SPEC.md_

  - ⬜ 44.2 Create PaymentService
    - Record payments against invoices
    - Support partial payments and multiple payment methods
    - Auto-update invoice status (partially_paid → paid)
    - Calculate outstanding balances
    - Generate aging reports (30/60/90 day buckets)

  - ⬜ 44.3 Create PurchaseOrderService
    - Create and manage purchase orders
    - Track goods receipt against PO line items
    - Auto-create inward transactions on receipt
    - Match supplier invoices to POs

  - ⬜ 44.4 Create SalesOrderService
    - Create and manage sales orders
    - Reserve inventory for confirmed orders
    - Track fulfillment progress
    - Auto-generate invoices from fulfilled orders
    - Auto-release expired reservations

  - ⬜ 44.5 Create PricingService
    - Base price management per item
    - Customer-specific pricing overrides
    - Quantity-based pricing tiers
    - Time-based promotional pricing
    - Price history tracking

- ⬜ 45. Implement Financial Module - Views & UI
  - ⬜ 45.1 Invoice management pages (list, detail, create, edit, PDF preview)
  - ⬜ 45.2 Payment recording pages
  - ⬜ 45.3 Purchase order management pages
  - ⬜ 45.4 Sales order management pages
  - ⬜ 45.5 Financial dashboard widgets (revenue, outstanding, aging)
  - ⬜ 45.6 Financial reports (sales, purchases, COGS, inventory valuation)

  - ⬜* 45.7 Write unit tests for financial module
    - Test invoice generation and calculation
    - Test payment recording and status updates
    - Test PO goods receipt flow
    - Test SO fulfillment and inventory reservation
    - Test pricing tier calculations

- ⬜ 46. Checkpoint - Verify financial module
  - ⬜ Ensure all tests pass, ask the user if questions arise.

---

## Phase 9: Data Import/Export

- ⬜ 20. Implement Data Import/Export
  - ⬜ 20.1 Create import functionality
    - Support CSV and Excel file parsing
    - Validate import data
    - Map columns to custom fields
    - Process imports asynchronously with Celery
    - _Requirements: 95.1, 95.2, 96.1, 97.1_

  - ⬜ 20.2 Create export functionality
    - Support CSV, Excel, JSON formats
    - Apply current filters to exports
    - Include custom field values
    - Format dates and numbers per tenant settings
    - _Requirements: 99.1, 99.2, 100.1, 100.2_

  - ⬜ 20.3 Implement scheduled exports
    - Create scheduled_export_task
    - Support email and SFTP delivery
    - _Requirements: 101.1, 101.4_

  - ⬜* 20.4 Write property test for import-export round-trip
    - **Property 13: Import-Export Round-Trip**
    - **Validates: Requirements 95.1, 99.1**
    - Generate random items
    - Export then import
    - Verify data integrity
    - _Requirements: 95.1, 99.1_

  - ⬜* 20.5 Write unit tests for import/export
    - Test CSV parsing
    - Test validation errors
    - Test format conversion
    - _Requirements: 95.1, 96.1, 99.1_

---

## Phase 10: Frontend

- 🔄 21. Implement Frontend - Base Templates and Components
  - ✅ 21.1 Create base HTML templates
    - ✅ Create base.html with common layout (header, nav, footer, messages)
    - ✅ Create home.html landing page with hero, features, industries
    - ✅ Create dashboard.html with stat cards and quick actions
    - ⬜ Create sidebar.html component
    - ⬜ Create pagination.html reusable component
    - ⬜ Create modal.html reusable component
    - _Requirements: 103.1_

  - ✅ 21.2 Create CSS stylesheets
    - ✅ Create base.css with CSS variables for theming (722 lines, Omnify brand)
    - ✅ Implement responsive grid system (grid-2/3/4 with breakpoints)
    - ✅ Component styles: buttons, cards, tables, forms, badges, messages
    - ⬜ Create separate forms.css for advanced form styling
    - _Requirements: 103.1, 103.2_

  - 🔄 21.3 Create JavaScript utilities
    - ✅ Create app.js with basic functionality
    - ⬜ Create api.js for API client wrapper
    - ⬜ Create notifications.js for toast messages
    - ⬜ Create modal.js for modal dialogs
    - ⬜ Create datatable.js for interactive tables
    - _Requirements: 103.1_

  - ⬜* 21.4 Write frontend unit tests
    - ⬜ Test API client methods
    - ⬜ Test component initialization
    - ⬜ Test event handlers
    - _Requirements: 103.1_

- 🔄 22. Implement Frontend - Item Management Pages
  - ✅ 22.1 Create item list page
    - ✅ Display items in paginated table
    - ✅ Implement search and filtering (by type, status, location)
    - ✅ Show stats (total items, total quantity, low stock)
    - ⬜ Add bulk selection
    - _Requirements: 14.1, 14.6, 58.1_

  - ✅ 22.2 Create item detail page
    - ✅ Display all item information with custom field values
    - ⬜ Display transaction history
    - ⬜ Show workflow state and history
    - _Requirements: 10.1, 20.2, 27.2_

  - ✅ 22.3 Create item form page
    - ✅ Form for create/edit with item type and location selection
    - ⬜ Dynamic form based on item type (render custom fields)
    - ⬜ Client-side validation
    - _Requirements: 9.1, 9.4, 9.5_

  - ⬜* 22.4 Write frontend integration tests
    - ⬜ Test item creation flow
    - ⬜ Test search and filtering
    - ⬜ Test form validation
    - _Requirements: 9.1, 14.1_

- ⬜ 23. Implement Frontend - Transaction Pages
  - ⬜ 23.1 Create transaction list page
    - Display transactions in table
    - Filter by type, status, date
    - Show approval status
    - _Requirements: 20.1, 20.3_

  - ⬜ 23.2 Create transaction form page
    - Select transaction type
    - Add items with quantities
    - Select locations
    - _Requirements: 17.1, 17.4, 17.5, 17.6_

  - ⬜ 23.3 Create transaction detail page
    - Show all transaction details
    - Display approval workflow
    - Show reversal information if applicable
    - _Requirements: 20.2, 21.3_

  - ⬜* 23.4 Write frontend integration tests
    - Test transaction creation
    - Test approval workflow
    - Test reversal
    - _Requirements: 17.1, 21.1_

- ⬜ 24. Checkpoint - Verify frontend implementation
  - ⬜ Ensure all tests pass, ask the user if questions arise.


- ⬜ 25. Implement Frontend - Dashboard and Reports
  - ⬜ 25.1 Create dashboard page
    - Display configurable widgets
    - Support drag-and-drop widget arrangement
    - Implement auto-refresh
    - _Requirements: 46.2, 46.3, 48.1_

  - ⬜ 25.2 Create dashboard widgets
    - Total inventory count widget
    - Low stock items widget
    - Recent transactions widget
    - Inventory value widgets
    - Chart widgets (bar, line, pie)
    - _Requirements: 47.1, 47.2, 47.3, 47.4, 47.5_

  - ⬜ 25.3 Create reports page
    - List available reports
    - Report parameter selection
    - Generate and download reports
    - _Requirements: 49.1, 49.2, 49.5_

  - ⬜* 25.4 Write frontend tests for dashboard
    - Test widget rendering
    - Test data refresh
    - Test widget configuration
    - _Requirements: 46.1, 48.1_

- ⬜ 26. Implement Frontend - Admin Configuration Pages
  - ⬜ 26.1 Create item type management page
    - List item types in hierarchy
    - Create/edit item types
    - Manage custom fields
    - _Requirements: 4.1, 5.4, 6.1_

  - ⬜ 26.2 Create workflow management page
    - List workflows
    - Create/edit workflows
    - Define states and transitions
    - Visual workflow diagram
    - _Requirements: 23.1, 24.1, 25.1_

  - ⬜ 26.3 Create role and permission management page
    - List roles in hierarchy
    - Create/edit roles
    - Assign permissions
    - Assign roles to users
    - _Requirements: 29.1, 30.1, 32.1_

  - 🔄 26.4 Create location management page
    - ✅ List locations with filtering and search
    - ✅ Create/edit locations with hierarchy support
    - ✅ View location details with children and items
    - ⬜ View capacity utilization visualization
    - _Requirements: 35.1, 36.4, 37.2_

  - ⬜* 26.5 Write frontend tests for admin pages
    - Test configuration forms
    - Test hierarchy displays
    - Test permission assignment
    - _Requirements: 4.1, 23.1, 29.1, 35.1_

---

## Phase 11: Advanced Features

- ⬜ 27. Implement Advanced Features - Barcode Support
  - ⬜ 27.1 Add barcode scanning support
    - Support barcode input in item code fields
    - Auto-submit on barcode scan
    - _Requirements: 106.1, 106.2_

  - ⬜ 27.2 Implement barcode label generation
    - Generate barcode images
    - Create printable label templates
    - Support batch printing
    - _Requirements: 106.4, 106.5, 106.6_

  - ⬜* 27.3 Write unit tests for barcode functionality
    - Test barcode generation
    - Test barcode validation
    - _Requirements: 106.1, 106.4_

- ⬜ 28. Implement Advanced Features - Batch and Serial Tracking
  - ⬜ 28.1 Add batch tracking
    - Track batch numbers in transactions
    - Track expiration dates
    - Implement FIFO allocation
    - Generate batch alerts
    - _Requirements: 111.1, 111.2, 111.3, 111.4_

  - ⬜ 28.2 Add serial number tracking
    - Enforce serial number uniqueness
    - Track individual item history
    - Support warranty tracking
    - _Requirements: 112.1, 112.2, 112.3, 112.4_

  - ⬜* 28.3 Write unit tests for batch/serial tracking
    - Test batch expiration alerts
    - Test serial number uniqueness
    - Test FIFO allocation
    - _Requirements: 111.1, 112.1_

- ⬜ 29. Implement Advanced Features - Inventory Management
  - ⬜ 29.1 Implement reorder point management
    - ✅ Reorder point fields exist on Item model (reorder_point, reorder_quantity)
    - ✅ is_low_stock() method implemented
    - ⬜ Generate reorder alerts (integrate with Notifications)
    - ⬜ Calculate suggested reorder quantities
    - _Requirements: 115.1, 115.2, 115.3_

  - ⬜ 29.2 Implement cycle counting
    - Create cycle count schedules
    - Generate cycle count tasks
    - Record counted quantities
    - Calculate and approve variances
    - _Requirements: 113.1, 113.2, 113.3, 113.4_

  - ⬜ 29.3 Implement inventory reservations
    - Create reservation model
    - Reduce available quantity
    - Auto-release expired reservations
    - _Requirements: 45.1, 45.2, 45.5_

  - ⬜* 29.4 Write unit tests for inventory management
    - Test reorder alerts
    - Test cycle count variance calculation
    - Test reservation logic
    - _Requirements: 115.1, 113.3, 45.1_

- ⬜ 30. Checkpoint - Verify advanced features
  - ⬜ Ensure all tests pass, ask the user if questions arise.

---

## Phase 12: Hardening & Production Readiness

- ⬜ 31. Implement Security Hardening
  - ⬜ 31.1 Implement security headers
    - ✅ Production settings include HSTS, X-Frame-Options DENY, SSL redirect, secure cookies
    - ⬜ Configure Content-Security-Policy
    - ⬜ Set X-Content-Type-Options
    - _Requirements: 80.1, 80.2, 80.3, 80.4_

  - ⬜ 31.2 Implement input validation and sanitization
    - Validate all input data
    - Sanitize text input for XSS prevention
    - Use parameterized queries (Django ORM)
    - Validate file uploads
    - _Requirements: 81.1, 81.2, 81.3, 81.4_

  - ⬜ 31.3 Implement data encryption
    - Configure TLS for all connections
    - Encrypt sensitive data at rest
    - Implement tenant-specific encryption keys
    - _Requirements: 79.1, 79.2, 79.3_

  - ⬜* 31.4 Write security tests
    - Test CSRF protection
    - Test XSS prevention
    - Test SQL injection prevention
    - Test file upload validation
    - _Requirements: 80.1, 81.1, 81.2, 81.3_

- ⬜ 32. Implement Performance Optimization
  - ⬜ 32.1 Add database indexes
    - ✅ Indexes already defined on core models (tenant, status, location, code combinations)
    - ⬜ Review and add indexes for new models (financial, template, workflow)
    - ⬜ Create indexes on datetime fields for reports
    - _Requirements: 91.1, 91.2_

  - ⬜ 32.2 Implement caching
    - ✅ LocMemCache configured for MVP
    - ⬜ Switch to Redis cache for production
    - ⬜ Cache item type definitions
    - ⬜ Cache user permissions
    - ⬜ Cache location hierarchies
    - ⬜ Cache dashboard widget data
    - ⬜ Implement cache invalidation
    - _Requirements: 92.1, 92.2, 92.3, 92.4, 92.5_

  - ⬜ 32.3 Optimize database queries
    - Use select_related() for foreign keys
    - Use prefetch_related() for reverse relations
    - Implement query result caching
    - _Requirements: 91.4_

  - ⬜* 32.4 Write performance tests
    - Test query performance with large datasets
    - Test cache hit rates
    - Test API response times
    - _Requirements: 90.1, 90.2, 92.7_

- ⬜ 33. Implement Monitoring and Logging
  - 🔄 33.1 Configure application logging
    - ✅ Rotating file handlers configured (100MB, 10 backups)
    - ✅ Console and file logging configured
    - ⬜ Structured logging format
    - ⬜ Log all errors and warnings
    - _Requirements: Error Handling section_

  - ⬜ 33.2 Implement monitoring
    - Collect application metrics
    - Monitor database performance
    - Monitor cache performance
    - Monitor Celery queue depths
    - _Requirements: 94.1, 94.2, 94.3, 94.4_

  - ⬜ 33.3 Create health check endpoint
    - Check database connectivity
    - Check Redis connectivity
    - Check Celery worker status
    - _Requirements: 94.7_

  - ⬜* 33.4 Write monitoring tests
    - Test health check endpoint
    - Test metric collection
    - _Requirements: 94.7_

- ⬜ 34. Implement Accessibility and Internationalization
  - ⬜ 34.1 Implement accessibility features
    - Add ARIA labels
    - Ensure keyboard navigation
    - Maintain color contrast ratios
    - Support text resizing
    - _Requirements: 104.1, 104.2, 104.3, 104.4_

  - ⬜ 34.2 Implement internationalization
    - Set up Django i18n
    - Mark strings for translation
    - Support multiple languages
    - Support RTL languages
    - Format dates/numbers per locale
    - _Requirements: 105.1, 105.2, 105.3, 105.4, 105.6_

  - ⬜* 34.3 Write accessibility tests
    - Test keyboard navigation
    - Test screen reader compatibility
    - Test color contrast
    - _Requirements: 104.2, 104.4_

---

## Phase 13: Final Integration & Launch

- ⬜ 35. Final Integration and Testing
  - ⬜ 35.1 Run full test suite
    - Run all unit tests
    - Run all property-based tests
    - Run all integration tests
    - Verify all tests pass

  - ⬜ 35.2 Perform end-to-end testing
    - Test complete user workflows
    - Test multi-tenant isolation
    - Test data import/export
    - Test API integration

  - ⬜* 35.3 Write property test for audit log immutability
    - **Property 15: Audit Log Immutability**
    - **Validates: Requirements 59.6**
    - Attempt to modify/delete audit logs
    - Verify operations are prevented
    - _Requirements: 59.6_

  - ⬜ 35.4 Performance testing
    - Load test with concurrent users
    - Test with large datasets (1M items)
    - Verify response time targets
    - _Requirements: 90.1, 90.2, 90.3_

- ⬜ 36. Documentation and Deployment Preparation
  - ⬜ 36.1 Create API documentation
    - Generate OpenAPI/Swagger docs
    - Add endpoint descriptions
    - Add code examples
    - _Requirements: 71.1, 71.2, 71.3_

  - ⬜ 36.2 Create deployment documentation
    - Document environment setup
    - Document configuration options
    - Create deployment scripts
    - Document backup procedures

  - ⬜ 36.3 Create user documentation
    - Write user guide
    - Create admin guide
    - Document common workflows

  - ⬜ 36.4 Prepare production deployment
    - ✅ Production settings file exists with security hardening
    - ⬜ Set up database migrations strategy
    - ⬜ Configure web server (Nginx + Gunicorn)
    - ⬜ Set up SSL certificates
    - ⬜ Configure monitoring and alerting

- ⬜ 37. Final Checkpoint - Production Readiness
  - ⬜ Ensure all tests pass, verify documentation is complete, confirm deployment readiness.

---

## Progress Summary

| Phase | Description | Status |
|-------|-------------|--------|
| Phase 1 | Foundation & Infrastructure | ✅ Complete |
| Phase 2 | Authentication & Access Control | 🔄 Partial (User model done, auth views & RBAC pending) |
| Phase 3 | Core Data Models | 🔄 Partial (Items & Locations done, validation pending) |
| Phase 4 | Transaction Processing | ⬜ Not started |
| Phase 5 | Workflows & Notifications | ⬜ Not started |
| Phase 6 | Reporting & API | ⬜ Not started |
| Phase 7 | Template System & Onboarding | ⬜ Not started (NEW) |
| Phase 8 | Financial Management | ⬜ Not started (NEW) |
| Phase 9 | Data Import/Export | ⬜ Not started |
| Phase 10 | Frontend | 🔄 Partial (base templates, items, locations pages exist) |
| Phase 11 | Advanced Features | ⬜ Not started |
| Phase 12 | Hardening & Production | 🔄 Minimal (settings, logging partially configured) |
| Phase 13 | Final Integration & Launch | ⬜ Not started |

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Property tests validate universal correctness properties
- Unit tests validate specific examples and edge cases
- Checkpoints ensure incremental validation
- The implementation follows an incremental approach, building core functionality first
- **NEW phases 7 & 8** added for Template System, Onboarding, and Financial Management — these are core differentiators referenced extensively in business docs
