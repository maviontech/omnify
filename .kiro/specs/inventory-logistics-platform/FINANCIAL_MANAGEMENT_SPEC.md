# Financial Management Module Specification

## Overview

The Financial Management module provides comprehensive financial operations for Omnify tenants. It covers invoicing, payment tracking, purchase orders, sales orders, pricing management, and financial reporting. This module is a key differentiator — most inventory platforms stop at inventory tracking, while Omnify provides a complete business operations suite.

**Module Identifier:** `financial` (encompasses sub-modules: `invoicing`, `payments`, `purchase_orders`, `sales_orders`)

**Available on Tiers:** Professional, Enterprise

**Dependencies:** `items`, `transactions`

---

## 1. Invoice Management

### 1.1 Invoice Model

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| tenant | FK(Tenant) | Tenant isolation |
| invoice_number | CharField | Auto-generated, sequential per tenant (e.g., INV-2026-00001) |
| status | CharField | draft, sent, paid, partially_paid, overdue, cancelled, refunded |
| customer_name | CharField | Customer/client name |
| customer_email | EmailField | For sending invoices |
| customer_address | TextField | Billing address |
| customer_tax_id | CharField | Tax/VAT registration number (optional) |
| related_transaction | FK(Transaction) | Optional link to originating transaction |
| related_sales_order | FK(SalesOrder) | Optional link to originating sales order |
| subtotal | DecimalField | Sum of line items before tax/discount |
| discount_type | CharField | percentage, fixed_amount, none |
| discount_value | DecimalField | Discount amount or percentage |
| discount_amount | DecimalField | Calculated discount in currency |
| tax_rate | DecimalField | Tax percentage (e.g., 18.00 for 18%) |
| tax_amount | DecimalField | Calculated tax amount |
| total_amount | DecimalField | Final amount (subtotal - discount + tax) |
| amount_paid | DecimalField | Total payments received |
| amount_due | DecimalField | Calculated: total_amount - amount_paid |
| currency | CharField | Currency code (from tenant config, e.g., USD) |
| issue_date | DateField | Invoice creation date |
| due_date | DateField | Payment due date |
| paid_date | DateField | Date fully paid (nullable) |
| payment_terms | CharField | net_30, net_60, net_90, due_on_receipt, custom |
| notes | TextField | Internal notes |
| customer_notes | TextField | Notes visible to customer on invoice |
| created_by | FK(User) | Invoice creator |
| created_at | DateTimeField | Timestamp |
| updated_at | DateTimeField | Timestamp |

### 1.2 InvoiceLineItem Model

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| invoice | FK(Invoice) | Parent invoice |
| item | FK(Item) | Optional link to inventory item |
| description | CharField | Line item description |
| quantity | DecimalField | Quantity |
| unit | CharField | Unit of measurement |
| unit_price | DecimalField | Price per unit |
| discount_percent | DecimalField | Line-level discount (optional) |
| tax_rate | DecimalField | Line-level tax rate (optional, overrides invoice tax) |
| line_total | DecimalField | Calculated: (quantity * unit_price) - discount + tax |
| display_order | IntegerField | Order within invoice |

### 1.3 Invoice Number Generation

Each tenant gets its own sequential numbering. The format is configurable per tenant:

```
Default Format: INV-{YEAR}-{SEQUENCE:05d}
Examples:
  INV-2026-00001
  INV-2026-00002

Custom Formats (configured in TenantConfiguration):
  {PREFIX}-{YEAR}{MONTH}-{SEQUENCE}  →  SALE-202601-001
  {PREFIX}/{SEQUENCE}                 →  INV/00042
```

Implementation: Use a `TenantSequence` model to track the next number per tenant per document type (invoice, PO, SO). Use `select_for_update()` to prevent race conditions.

```python
class TenantSequence(TenantAwareModel):
    document_type = models.CharField(max_length=20)  # invoice, purchase_order, sales_order
    prefix = models.CharField(max_length=20, default='INV')
    format_string = models.CharField(max_length=100, default='{prefix}-{year}-{seq:05d}')
    next_number = models.IntegerField(default=1)

    class Meta:
        unique_together = ['tenant', 'document_type']
```

### 1.4 Invoice Status Transitions

```
draft → sent           (user sends invoice to customer)
sent → paid            (full payment received)
sent → partially_paid  (partial payment received)
partially_paid → paid  (remaining payment received)
sent → overdue         (auto: due_date passed without full payment)
partially_paid → overdue (auto: due_date passed)
draft → cancelled      (user cancels draft)
sent → cancelled       (user cancels sent invoice)
paid → refunded        (user issues refund)
```

### 1.5 Invoice PDF Generation

Generate printable PDF invoices with:
- Tenant branding (logo, primary color, company info)
- Invoice details (number, dates, payment terms)
- Customer information
- Line items table with totals
- Tax breakdown
- Payment instructions
- Footer with terms and conditions

Use: `reportlab` or `weasyprint` for PDF generation. Store generated PDFs as `FileAttachment` records.

### 1.6 Invoice Aging Reports

Track overdue invoices in aging buckets:
- Current (not yet due)
- 1-30 days overdue
- 31-60 days overdue
- 61-90 days overdue
- 90+ days overdue

---

## 2. Payment Tracking

### 2.1 Payment Model

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| tenant | FK(Tenant) | Tenant isolation |
| invoice | FK(Invoice) | Associated invoice |
| payment_number | CharField | Auto-generated reference (PAY-2026-00001) |
| amount | DecimalField | Payment amount |
| payment_method | CharField | cash, bank_transfer, credit_card, check, online, other |
| payment_date | DateField | Date payment was received |
| reference_number | CharField | External reference (check number, transfer ID) |
| notes | TextField | Payment notes |
| recorded_by | FK(User) | Who recorded the payment |
| created_at | DateTimeField | Timestamp |

### 2.2 Payment Processing Rules

1. **Partial payments allowed** — Multiple payments can be recorded against one invoice
2. **Auto-status update** — When payment recorded:
   - If `amount_paid == total_amount` → status = `paid`, set `paid_date`
   - If `amount_paid < total_amount` → status = `partially_paid`
3. **Overpayment prevention** — Total payments cannot exceed invoice total
4. **Payment reversal** — Reversing a payment updates invoice status back

### 2.3 Outstanding Balance Calculation

```python
def get_outstanding_balance(tenant):
    """Calculate total outstanding across all invoices."""
    return Invoice.objects.filter(
        tenant=tenant,
        status__in=['sent', 'partially_paid', 'overdue']
    ).aggregate(
        total_due=Sum('amount_due')
    )['total_due'] or Decimal('0.00')
```

---

## 3. Purchase Orders

### 3.1 PurchaseOrder Model

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| tenant | FK(Tenant) | Tenant isolation |
| po_number | CharField | Auto-generated (PO-2026-00001) |
| status | CharField | draft, sent, confirmed, partially_received, received, cancelled |
| supplier_name | CharField | Supplier/vendor name |
| supplier_email | EmailField | Supplier contact |
| supplier_address | TextField | Supplier address |
| order_date | DateField | Date order was placed |
| expected_delivery_date | DateField | Expected delivery |
| received_date | DateField | Date fully received (nullable) |
| subtotal | DecimalField | Sum of line items |
| tax_rate | DecimalField | Tax percentage |
| tax_amount | DecimalField | Calculated tax |
| shipping_cost | DecimalField | Shipping/freight charges |
| total_amount | DecimalField | Final total |
| notes | TextField | Internal notes |
| created_by | FK(User) | Order creator |
| created_at | DateTimeField | Timestamp |
| updated_at | DateTimeField | Timestamp |

### 3.2 PurchaseOrderLineItem Model

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| purchase_order | FK(PurchaseOrder) | Parent PO |
| item | FK(Item) | Inventory item being ordered |
| description | CharField | Item description |
| ordered_quantity | DecimalField | Quantity ordered |
| received_quantity | DecimalField | Quantity received so far (default 0) |
| unit_price | DecimalField | Price per unit |
| line_total | DecimalField | ordered_quantity * unit_price |
| display_order | IntegerField | Order within PO |

### 3.3 PO Status Transitions

```
draft → sent              (PO sent to supplier)
sent → confirmed          (supplier confirms order)
confirmed → partially_received  (some items received)
partially_received → received   (all items received)
confirmed → received           (all items received at once)
draft → cancelled              (cancel before sending)
sent → cancelled               (cancel after sending)
```

### 3.4 Goods Receipt Process

When items arrive against a PO:

1. User selects PO and enters received quantities per line item
2. System validates: `received_quantity <= ordered_quantity`
3. System creates an inward `Transaction` (type: `increase`)
4. Updates `PurchaseOrderLineItem.received_quantity`
5. If all lines fully received → PO status = `received`
6. Otherwise → PO status = `partially_received`
7. Item quantities updated via transaction processing
8. Audit log records the receipt

---

## 4. Sales Orders

### 4.1 SalesOrder Model

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| tenant | FK(Tenant) | Tenant isolation |
| so_number | CharField | Auto-generated (SO-2026-00001) |
| status | CharField | draft, confirmed, processing, partially_fulfilled, fulfilled, shipped, delivered, cancelled |
| customer_name | CharField | Customer name |
| customer_email | EmailField | Customer contact |
| customer_address | TextField | Shipping address |
| order_date | DateField | Date order was placed |
| required_date | DateField | Requested delivery date |
| fulfilled_date | DateField | Date fully fulfilled (nullable) |
| shipped_date | DateField | Date shipped (nullable) |
| subtotal | DecimalField | Sum of line items |
| tax_rate | DecimalField | Tax percentage |
| tax_amount | DecimalField | Calculated tax |
| shipping_cost | DecimalField | Shipping charges |
| total_amount | DecimalField | Final total |
| notes | TextField | Internal notes |
| created_by | FK(User) | Order creator |
| created_at | DateTimeField | Timestamp |
| updated_at | DateTimeField | Timestamp |

### 4.2 SalesOrderLineItem Model

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| sales_order | FK(SalesOrder) | Parent SO |
| item | FK(Item) | Inventory item being sold |
| description | CharField | Item description |
| ordered_quantity | DecimalField | Quantity ordered by customer |
| fulfilled_quantity | DecimalField | Quantity picked/packed (default 0) |
| reserved_quantity | DecimalField | Quantity reserved from available stock |
| unit_price | DecimalField | Selling price per unit |
| discount_percent | DecimalField | Line-level discount |
| line_total | DecimalField | Calculated total |
| display_order | IntegerField | Order within SO |

### 4.3 SO Status Transitions

```
draft → confirmed           (order accepted)
confirmed → processing      (fulfillment started)
processing → partially_fulfilled  (some items picked)
partially_fulfilled → fulfilled    (all items picked)
processing → fulfilled            (all items picked at once)
fulfilled → shipped               (shipment dispatched)
shipped → delivered               (delivery confirmed)
draft → cancelled                 (cancel before confirming)
confirmed → cancelled             (cancel after confirming, release reservations)
```

### 4.4 Inventory Reservation on Confirmation

When a sales order is confirmed:

1. For each line item, check available quantity: `item.quantity - existing_reservations`
2. If sufficient → create reservation, reduce available quantity
3. If insufficient → flag the line item, optionally allow backorder
4. Reservation holds inventory for this order
5. On fulfillment → reservation is consumed, actual transaction recorded
6. On cancellation → reservation is released

```python
class InventoryReservation(TenantAwareModel):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    sales_order_line = models.ForeignKey(SalesOrderLineItem, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=15, decimal_places=3)
    reserved_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(choices=[
        ('active', 'Active'),
        ('fulfilled', 'Fulfilled'),
        ('released', 'Released'),
        ('expired', 'Expired'),
    ], default='active')
```

### 4.5 Auto-Invoice Generation

When a sales order is fulfilled (or shipped), automatically generate an invoice:

1. Create Invoice from SO data (customer info, line items, totals)
2. Link invoice to sales order (`related_sales_order` FK)
3. Set invoice status to `draft` (user reviews before sending)
4. Copy line items with quantities and prices

---

## 5. Pricing Management

### 5.1 PricingRule Model

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| tenant | FK(Tenant) | Tenant isolation |
| item | FK(Item) | Item this rule applies to (nullable for type-level rules) |
| item_type | FK(ItemType) | Item type this rule applies to (nullable) |
| rule_type | CharField | base_price, customer_specific, quantity_tier, promotional |
| customer_name | CharField | For customer-specific pricing (nullable) |
| min_quantity | DecimalField | Minimum quantity for tier pricing (nullable) |
| max_quantity | DecimalField | Maximum quantity for tier pricing (nullable) |
| price | DecimalField | The price for this rule |
| discount_percent | DecimalField | Alternative: percentage discount from base (nullable) |
| valid_from | DateField | Start date for promotional pricing (nullable) |
| valid_until | DateField | End date for promotional pricing (nullable) |
| is_active | BooleanField | Whether this rule is currently active |
| priority | IntegerField | Higher priority rules take precedence |
| created_at | DateTimeField | Timestamp |

### 5.2 Price Resolution Order

When determining the price for an item in a transaction:

1. **Customer-specific price** (highest priority) — if a rule exists for this customer + item
2. **Promotional price** — if an active promotion exists for this item within date range
3. **Quantity tier price** — based on the quantity being ordered
4. **Base price** — the item's `selling_price` field (fallback)

```python
class PricingService:
    def get_price(self, item, customer_name=None, quantity=1, date=None):
        """Resolve the best price for an item given context."""
        date = date or timezone.now().date()

        # 1. Check customer-specific
        customer_price = self._get_customer_price(item, customer_name)
        if customer_price:
            return customer_price

        # 2. Check promotions
        promo_price = self._get_promotional_price(item, date)
        if promo_price:
            return promo_price

        # 3. Check quantity tiers
        tier_price = self._get_tier_price(item, quantity)
        if tier_price:
            return tier_price

        # 4. Fallback to base price
        return item.selling_price
```

---

## 6. Financial Reporting

### 6.1 Built-in Financial Reports

| Report | Description | Data Sources |
|--------|-------------|-------------|
| Sales Summary | Revenue by period (daily/weekly/monthly) | Invoices (paid) |
| Sales by Item Type | Revenue breakdown by item category | InvoiceLineItems |
| Sales by Customer | Revenue per customer | Invoices |
| Accounts Receivable Aging | Outstanding invoices by age bucket | Invoices (unpaid) |
| Purchase Summary | Spending by period | PurchaseOrders (received) |
| Purchase by Supplier | Spending per supplier | PurchaseOrders |
| Accounts Payable | Outstanding purchase obligations | PurchaseOrders (unpaid) |
| Profit & Loss | Revenue - COGS for period | Invoices, Items (unit_cost) |
| Inventory Valuation | Total value of current inventory | Items (quantity * unit_cost) |
| COGS Report | Cost of goods sold by period | Transactions (outward) |
| Cash Flow | Payments received vs payments made | Payments |
| Tax Summary | Tax collected and owed by period | Invoices, PurchaseOrders |

### 6.2 Financial Dashboard Widgets

- **Revenue This Month** — Total paid invoices this month
- **Outstanding Receivables** — Total unpaid invoice amounts
- **Overdue Invoices Count** — Number of overdue invoices
- **Top Customers** — Highest-spending customers this period
- **Inventory Value** — Total value of current stock
- **Pending Purchase Orders** — POs awaiting delivery
- **Monthly Revenue Chart** — Line chart of revenue over 12 months
- **Revenue vs Expenses** — Bar chart comparing income and spending

---

## 7. Module Configuration

### 7.1 Financial Module Feature Flags

These are stored in `TenantConfiguration.enabled_modules`:

```python
FINANCIAL_SUBMODULES = {
    'invoicing': 'Invoice generation and management',
    'payments': 'Payment tracking and recording',
    'purchase_orders': 'Purchase order management',
    'sales_orders': 'Sales order management with reservations',
    'pricing': 'Advanced pricing rules and tiers',
    'financial_reports': 'Financial analytics and reporting',
}
```

Tenants can enable individual sub-modules. For example, a library might enable `invoicing` (for late fees) but not `purchase_orders`.

### 7.2 Currency Configuration

Stored in `TenantConfiguration`:

```python
currency = models.CharField(max_length=3, default='USD')
currency_symbol = models.CharField(max_length=5, default='$')
currency_position = models.CharField(
    choices=[('before', 'Before amount ($100)'), ('after', 'After amount (100$)')],
    default='before'
)
decimal_places = models.IntegerField(default=2)
thousand_separator = models.CharField(max_length=1, default=',')
decimal_separator = models.CharField(max_length=1, default='.')
```

### 7.3 Tax Configuration

```python
class TaxRate(TenantAwareModel):
    name = models.CharField(max_length=100)  # e.g., "VAT", "GST", "Sales Tax"
    rate = models.DecimalField(max_digits=5, decimal_places=2)  # e.g., 18.00
    is_default = models.BooleanField(default=False)
    is_inclusive = models.BooleanField(default=False)  # Tax included in price?
    applies_to = models.CharField(
        choices=[('all', 'All Items'), ('specific', 'Specific Item Types')],
        default='all'
    )
    item_types = models.ManyToManyField(ItemType, blank=True)  # If specific
    is_active = models.BooleanField(default=True)
```

---

## 8. API Endpoints

### 8.1 Invoice API

```
GET    /api/v1/invoices/                    # List invoices (with filters)
POST   /api/v1/invoices/                    # Create invoice
GET    /api/v1/invoices/{id}/               # Get invoice detail
PUT    /api/v1/invoices/{id}/               # Update invoice
DELETE /api/v1/invoices/{id}/               # Delete draft invoice
POST   /api/v1/invoices/{id}/send/          # Send invoice to customer
POST   /api/v1/invoices/{id}/cancel/        # Cancel invoice
GET    /api/v1/invoices/{id}/pdf/           # Download PDF
POST   /api/v1/invoices/{id}/payments/      # Record payment
GET    /api/v1/invoices/aging/              # Aging report
GET    /api/v1/invoices/summary/            # Summary statistics
```

### 8.2 Purchase Order API

```
GET    /api/v1/purchase-orders/             # List POs
POST   /api/v1/purchase-orders/             # Create PO
GET    /api/v1/purchase-orders/{id}/        # Get PO detail
PUT    /api/v1/purchase-orders/{id}/        # Update PO
POST   /api/v1/purchase-orders/{id}/send/   # Send to supplier
POST   /api/v1/purchase-orders/{id}/receive/ # Record goods receipt
POST   /api/v1/purchase-orders/{id}/cancel/ # Cancel PO
```

### 8.3 Sales Order API

```
GET    /api/v1/sales-orders/                # List SOs
POST   /api/v1/sales-orders/                # Create SO
GET    /api/v1/sales-orders/{id}/           # Get SO detail
PUT    /api/v1/sales-orders/{id}/           # Update SO
POST   /api/v1/sales-orders/{id}/confirm/   # Confirm & reserve inventory
POST   /api/v1/sales-orders/{id}/fulfill/   # Record fulfillment
POST   /api/v1/sales-orders/{id}/ship/      # Mark as shipped
POST   /api/v1/sales-orders/{id}/cancel/    # Cancel & release reservations
POST   /api/v1/sales-orders/{id}/invoice/   # Generate invoice from SO
```

### 8.4 Pricing API

```
GET    /api/v1/pricing/rules/               # List pricing rules
POST   /api/v1/pricing/rules/               # Create pricing rule
GET    /api/v1/pricing/resolve/             # Resolve price for item+customer+quantity
GET    /api/v1/pricing/history/{item_id}/   # Price history for item
```

---

## 9. Integration Points

### 9.1 Transaction Integration

When a transaction is processed with financial implications:
- **Outward transaction** (decrease) → Optionally auto-create invoice
- **Inward transaction** (increase from PO) → Update PO received quantities

### 9.2 Notification Integration

- **Invoice overdue** → Send notification to tenant admin and customer
- **Payment received** → Send confirmation notification
- **PO delivery overdue** → Send notification to purchaser
- **Low stock + pending SO** → Alert about potential fulfillment issues

### 9.3 Report Integration

Financial data feeds into the reporting module:
- Financial reports use Invoice, Payment, PO, SO data
- Dashboard widgets show financial KPIs
- Scheduled reports can include financial summaries

---

## 10. Data Isolation & Security

- All financial models extend `TenantAwareModel` for row-level isolation
- Financial data is never accessible across tenants
- Payment details are logged but sensitive data (card numbers) is never stored
- Audit trail records all financial document changes
- PDF invoices are stored in tenant-specific paths

---

## 11. Acceptance Criteria

1. Tenant can create, send, and manage invoices with auto-calculated totals
2. Payments can be recorded (partial/full) with automatic invoice status updates
3. Purchase orders can be created and goods receipt recorded with inventory updates
4. Sales orders can be confirmed with inventory reservation, fulfilled, and auto-invoiced
5. Pricing rules resolve correctly in priority order
6. Financial reports generate accurate data from financial documents
7. All financial operations respect module enablement (hidden when disabled)
8. All financial data is tenant-isolated
9. Invoice PDFs render correctly with tenant branding
10. Sequential numbering works correctly under concurrent requests
