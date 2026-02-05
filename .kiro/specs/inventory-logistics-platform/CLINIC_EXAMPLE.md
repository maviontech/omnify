# Omnify - Medical Clinic Example

## Overview

This document demonstrates how **Omnify** can be used by a **medical clinic** to manage not just inventory, but also prescriptions, payment receipts, doctors, patients, and appointments.

**Omnify: Everything. Organized.**

## Key Insight: "Items" Can Represent Anything

Omnify's **Item** concept is intentionally generic and flexible. An "Item" can be:
- ✅ A physical product (medicine, equipment)
- ✅ A service (consultation, procedure)
- ✅ A person (doctor, patient, staff)
- ✅ A document (prescription, report, certificate)
- ✅ An appointment or booking
- ✅ Anything you need to track and manage!

This flexibility allows the same platform to handle diverse use cases within a single tenant.

---

## Clinic Use Cases

### 1. **Inventory Management** ✅ Already Covered
- Medical supplies (syringes, bandages, gloves)
- Pharmaceuticals (medicines, vaccines)
- Medical equipment (BP monitors, thermometers)

### 2. **Prescription Management** ✅ Using Custom Item Types
- Create an Item Type called "Prescription"
- Track prescription lifecycle
- Link to patients and doctors
- Manage dispensing workflow

### 3. **Payment & Billing** ✅ Using Financial Module
- Generate invoices for consultations, procedures, tests
- Record payments (cash, card, insurance)
- Print receipts automatically
- Track outstanding payments
- Financial reports

### 4. **Doctor Management** ✅ Using Custom Item Types
- Track doctor information
- Manage schedules and availability
- Record specializations and fees
- Monitor performance

### 5. **Patient Management** ✅ Using Custom Item Types
- Patient registration
- Medical history
- Contact information
- Appointment history

### 6. **Appointment Scheduling** ✅ Using Custom Item Types + Workflows
- Book appointments
- Confirm and reschedule
- Track appointment status
- Send reminders

---

## Clinic Template Configuration


### Complete Template JSON

```json
{
  "template_id": "clinic-v1",
  "name": "Medical Clinic",
  "version": "1.0.0",
  "description": "Complete management system for medical clinics including inventory, prescriptions, billing, and patient management",
  "industry": "Healthcare - Clinic",
  "author": "Platform Team",
  
  "item_types": [
    {
      "name": "Medical Supplies",
      "description": "Consumable medical supplies",
      "icon": "medical-box",
      "color": "#2196F3",
      "custom_fields": [
        {
          "name": "Item Code",
          "field_type": "text",
          "is_required": true,
          "is_searchable": true
        },
        {
          "name": "Supplier",
          "field_type": "text",
          "is_searchable": true
        },
        {
          "name": "Expiry Date",
          "field_type": "date",
          "is_required": true
        },
        {
          "name": "Reorder Level",
          "field_type": "number",
          "default_value": "10"
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
          "name": "Dosage Form",
          "field_type": "dropdown",
          "dropdown_options": ["Tablet", "Capsule", "Syrup", "Injection", "Cream", "Drops"]
        },
        {
          "name": "Strength",
          "field_type": "text"
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
          "dropdown_options": ["Room Temperature (15-25°C)", "Refrigerated (2-8°C)", "Frozen (-20°C or below)"]
        },
        {
          "name": "Prescription Required",
          "field_type": "boolean",
          "default_value": true
        }
      ]
    },
    {
      "name": "Doctors",
      "description": "Medical practitioners",
      "icon": "doctor",
      "color": "#9C27B0",
      "custom_fields": [
        {
          "name": "Full Name",
          "field_type": "text",
          "is_required": true,
          "is_searchable": true
        },
        {
          "name": "Specialization",
          "field_type": "dropdown",
          "is_required": true,
          "dropdown_options": [
            "General Physician",
            "Pediatrician",
            "Cardiologist",
            "Dermatologist",
            "Orthopedic",
            "Gynecologist",
            "ENT Specialist",
            "Ophthalmologist"
          ]
        },
        {
          "name": "License Number",
          "field_type": "text",
          "is_required": true,
          "is_searchable": true
        },
        {
          "name": "Phone",
          "field_type": "text",
          "is_required": true
        },
        {
          "name": "Email",
          "field_type": "text"
        },
        {
          "name": "Consultation Fee",
          "field_type": "number",
          "is_required": true
        },
        {
          "name": "Available Days",
          "field_type": "multiselect",
          "dropdown_options": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        },
        {
          "name": "Consultation Hours",
          "field_type": "text",
          "help_text": "e.g., 9:00 AM - 5:00 PM"
        },
        {
          "name": "Status",
          "field_type": "dropdown",
          "dropdown_options": ["Active", "On Leave", "Inactive"],
          "default_value": "Active"
        }
      ]
    },
    {
      "name": "Patients",
      "description": "Registered patients",
      "icon": "patient",
      "color": "#FF9800",
      "custom_fields": [
        {
          "name": "Patient ID",
          "field_type": "text",
          "is_required": true,
          "is_searchable": true
        },
        {
          "name": "Full Name",
          "field_type": "text",
          "is_required": true,
          "is_searchable": true
        },
        {
          "name": "Date of Birth",
          "field_type": "date",
          "is_required": true
        },
        {
          "name": "Gender",
          "field_type": "dropdown",
          "dropdown_options": ["Male", "Female", "Other"]
        },
        {
          "name": "Phone",
          "field_type": "text",
          "is_required": true
        },
        {
          "name": "Email",
          "field_type": "text"
        },
        {
          "name": "Address",
          "field_type": "text"
        },
        {
          "name": "Blood Group",
          "field_type": "dropdown",
          "dropdown_options": ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
        },
        {
          "name": "Allergies",
          "field_type": "text",
          "help_text": "List any known allergies"
        },
        {
          "name": "Emergency Contact Name",
          "field_type": "text"
        },
        {
          "name": "Emergency Contact Phone",
          "field_type": "text"
        },
        {
          "name": "Insurance Provider",
          "field_type": "text"
        },
        {
          "name": "Insurance Number",
          "field_type": "text"
        }
      ]
    },
    {
      "name": "Prescriptions",
      "description": "Medical prescriptions",
      "icon": "prescription",
      "color": "#00BCD4",
      "custom_fields": [
        {
          "name": "Prescription Number",
          "field_type": "text",
          "is_required": true,
          "is_searchable": true
        },
        {
          "name": "Patient Name",
          "field_type": "text",
          "is_required": true,
          "is_searchable": true
        },
        {
          "name": "Patient ID",
          "field_type": "text",
          "is_required": true,
          "is_searchable": true
        },
        {
          "name": "Doctor Name",
          "field_type": "text",
          "is_required": true,
          "is_searchable": true
        },
        {
          "name": "Diagnosis",
          "field_type": "text"
        },
        {
          "name": "Medications",
          "field_type": "text",
          "is_required": true,
          "help_text": "List of prescribed medications"
        },
        {
          "name": "Dosage Instructions",
          "field_type": "text",
          "is_required": true
        },
        {
          "name": "Issue Date",
          "field_type": "date",
          "is_required": true
        },
        {
          "name": "Valid Until",
          "field_type": "date"
        },
        {
          "name": "Notes",
          "field_type": "text"
        }
      ]
    },
    {
      "name": "Appointments",
      "description": "Patient appointments",
      "icon": "calendar",
      "color": "#E91E63",
      "custom_fields": [
        {
          "name": "Appointment Number",
          "field_type": "text",
          "is_required": true,
          "is_searchable": true
        },
        {
          "name": "Patient Name",
          "field_type": "text",
          "is_required": true,
          "is_searchable": true
        },
        {
          "name": "Patient ID",
          "field_type": "text",
          "is_required": true,
          "is_searchable": true
        },
        {
          "name": "Doctor Name",
          "field_type": "text",
          "is_required": true,
          "is_searchable": true
        },
        {
          "name": "Appointment Date",
          "field_type": "datetime",
          "is_required": true
        },
        {
          "name": "Duration (minutes)",
          "field_type": "number",
          "default_value": "30"
        },
        {
          "name": "Reason for Visit",
          "field_type": "text",
          "is_required": true
        },
        {
          "name": "Type",
          "field_type": "dropdown",
          "dropdown_options": ["Consultation", "Follow-up", "Emergency", "Routine Checkup"]
        },
        {
          "name": "Notes",
          "field_type": "text"
        }
      ]
    }
  ],
  
  "workflows": [
    {
      "name": "Prescription Workflow",
      "description": "Lifecycle of a prescription from creation to completion",
      "item_types": ["Prescriptions"],
      "states": [
        {
          "name": "Draft",
          "is_initial": true,
          "is_final": false,
          "color": "#9E9E9E",
          "description": "Prescription being prepared"
        },
        {
          "name": "Reviewed",
          "is_initial": false,
          "is_final": false,
          "color": "#2196F3",
          "description": "Prescription reviewed by doctor"
        },
        {
          "name": "Issued",
          "is_initial": false,
          "is_final": false,
          "color": "#4CAF50",
          "description": "Prescription issued to patient"
        },
        {
          "name": "Dispensed",
          "is_initial": false,
          "is_final": false,
          "color": "#FF9800",
          "description": "Medications dispensed"
        },
        {
          "name": "Completed",
          "is_initial": false,
          "is_final": true,
          "color": "#8BC34A",
          "description": "Prescription completed"
        },
        {
          "name": "Cancelled",
          "is_initial": false,
          "is_final": true,
          "color": "#F44336",
          "description": "Prescription cancelled"
        }
      ],
      "transitions": [
        {
          "name": "Submit for Review",
          "from_state": "Draft",
          "to_state": "Reviewed",
          "required_roles": ["Doctor", "Nurse"]
        },
        {
          "name": "Issue to Patient",
          "from_state": "Reviewed",
          "to_state": "Issued",
          "required_roles": ["Doctor"]
        },
        {
          "name": "Dispense Medications",
          "from_state": "Issued",
          "to_state": "Dispensed",
          "required_roles": ["Pharmacist"],
          "auto_create_transaction": true,
          "transaction_type": "Dispense Medicine"
        },
        {
          "name": "Mark Complete",
          "from_state": "Dispensed",
          "to_state": "Completed"
        },
        {
          "name": "Cancel",
          "from_state": "Draft",
          "to_state": "Cancelled",
          "required_roles": ["Doctor"]
        }
      ]
    },
    {
      "name": "Appointment Workflow",
      "description": "Lifecycle of a patient appointment",
      "item_types": ["Appointments"],
      "states": [
        {
          "name": "Scheduled",
          "is_initial": true,
          "is_final": false,
          "color": "#2196F3",
          "description": "Appointment scheduled"
        },
        {
          "name": "Confirmed",
          "is_initial": false,
          "is_final": false,
          "color": "#4CAF50",
          "description": "Appointment confirmed by patient"
        },
        {
          "name": "In Progress",
          "is_initial": false,
          "is_final": false,
          "color": "#FF9800",
          "description": "Consultation in progress"
        },
        {
          "name": "Completed",
          "is_initial": false,
          "is_final": true,
          "color": "#8BC34A",
          "description": "Appointment completed"
        },
        {
          "name": "Cancelled",
          "is_initial": false,
          "is_final": true,
          "color": "#F44336",
          "description": "Appointment cancelled"
        },
        {
          "name": "No Show",
          "is_initial": false,
          "is_final": true,
          "color": "#9E9E9E",
          "description": "Patient did not show up"
        }
      ],
      "transitions": [
        {
          "name": "Confirm Appointment",
          "from_state": "Scheduled",
          "to_state": "Confirmed"
        },
        {
          "name": "Start Consultation",
          "from_state": "Confirmed",
          "to_state": "In Progress",
          "required_roles": ["Doctor", "Receptionist"]
        },
        {
          "name": "Complete Consultation",
          "from_state": "In Progress",
          "to_state": "Completed",
          "required_roles": ["Doctor"],
          "auto_create_transaction": true,
          "transaction_type": "Complete Appointment"
        },
        {
          "name": "Cancel",
          "from_state": "Scheduled",
          "to_state": "Cancelled"
        },
        {
          "name": "Cancel",
          "from_state": "Confirmed",
          "to_state": "Cancelled"
        },
        {
          "name": "Mark No Show",
          "from_state": "Confirmed",
          "to_state": "No Show",
          "required_roles": ["Receptionist"]
        }
      ]
    }
  ],
  
  "transaction_types": [
    {
      "name": "Dispense Medicine",
      "description": "Dispense medication to patient",
      "affects_quantity": "decrease",
      "icon": "pill",
      "color": "#4CAF50",
      "requires_approval": false,
      "required_fields": ["Patient Name", "Prescription Number"]
    },
    {
      "name": "Receive Stock",
      "description": "Receive new stock from supplier",
      "affects_quantity": "increase",
      "icon": "plus",
      "color": "#2196F3",
      "requires_approval": false
    },
    {
      "name": "Issue Prescription",
      "description": "Issue prescription to patient",
      "affects_quantity": "none",
      "icon": "prescription",
      "color": "#00BCD4",
      "requires_approval": false
    },
    {
      "name": "Complete Appointment",
      "description": "Complete patient appointment",
      "affects_quantity": "none",
      "icon": "check",
      "color": "#8BC34A",
      "requires_approval": false
    },
    {
      "name": "Return Medicine",
      "description": "Return unused medicine",
      "affects_quantity": "increase",
      "icon": "arrow-left",
      "color": "#FF9800",
      "requires_approval": true
    },
    {
      "name": "Dispose Expired",
      "description": "Dispose expired medications",
      "affects_quantity": "decrease",
      "icon": "trash",
      "color": "#F44336",
      "requires_approval": true
    }
  ],
  
  "locations": [
    {
      "name": "Main Clinic",
      "location_type": "building",
      "children": [
        {
          "name": "Reception",
          "location_type": "area"
        },
        {
          "name": "Consultation Rooms",
          "location_type": "area",
          "children": [
            {"name": "Room 1", "location_type": "room"},
            {"name": "Room 2", "location_type": "room"},
            {"name": "Room 3", "location_type": "room"}
          ]
        },
        {
          "name": "Pharmacy",
          "location_type": "area",
          "children": [
            {"name": "Dispensing Counter", "location_type": "counter"},
            {"name": "Medicine Storage", "location_type": "storage"},
            {"name": "Refrigerated Storage", "location_type": "storage"}
          ]
        },
        {
          "name": "Laboratory",
          "location_type": "area"
        },
        {
          "name": "Supplies Storage",
          "location_type": "storage"
        }
      ]
    }
  ],
  
  "roles": [
    {
      "name": "Clinic Administrator",
      "description": "Full access to all clinic operations",
      "permissions": [
        "items.view",
        "items.create",
        "items.update",
        "items.delete",
        "transactions.view",
        "transactions.create",
        "workflows.execute",
        "reports.view",
        "reports.export",
        "invoicing.view",
        "invoicing.create",
        "payments.view",
        "payments.create",
        "users.manage"
      ]
    },
    {
      "name": "Doctor",
      "description": "Medical practitioner",
      "permissions": [
        "items.view",
        "items.create",
        "items.update",
        "transactions.view",
        "transactions.create",
        "workflows.execute",
        "reports.view",
        "invoicing.view",
        "invoicing.create"
      ]
    },
    {
      "name": "Pharmacist",
      "description": "Manages pharmacy and dispenses medications",
      "permissions": [
        "items.view",
        "items.create",
        "items.update",
        "transactions.view",
        "transactions.create",
        "workflows.execute",
        "reports.view"
      ]
    },
    {
      "name": "Receptionist",
      "description": "Manages appointments and patient registration",
      "permissions": [
        "items.view",
        "items.create",
        "items.update",
        "transactions.view",
        "workflows.execute",
        "invoicing.view",
        "invoicing.create",
        "payments.view",
        "payments.create"
      ]
    },
    {
      "name": "Nurse",
      "description": "Assists doctors and manages patient care",
      "permissions": [
        "items.view",
        "items.create",
        "items.update",
        "transactions.view",
        "transactions.create",
        "workflows.execute"
      ]
    }
  ],
  
  "enabled_modules": [
    "items",
    "transactions",
    "workflows",
    "locations",
    "reports",
    "notifications",
    "invoicing",
    "payments"
  ],
  
  "disabled_modules": [
    "purchase_orders",
    "sales_orders"
  ],
  
  "configuration": {
    "default_currency": "USD",
    "date_format": "MM/DD/YYYY",
    "timezone": "America/New_York",
    "low_stock_threshold": 10,
    "enable_barcode_scanning": true,
    "require_approval_for_disposal": true,
    "appointment_reminder_hours": 24
  }
}
```

---


## What the Clinic Admin Sees

When a clinic administrator logs in, they see:

```
┌─────────────────────────────────────────────────────────────┐
│  City Medical Clinic - Management System                    │
├─────────────────────────────────────────────────────────────┤
│  📊 Dashboard                                                │
│                                                              │
│  👨‍⚕️ Doctors (8 active)                                      │
│  👥 Patients (1,234 registered)                             │
│  💊 Pharmaceuticals (456 items)                             │
│  🏥 Medical Supplies (234 items)                            │
│  📋 Prescriptions (45 active)                               │
│  📅 Appointments (12 today)                                 │
│                                                              │
│  Today's Schedule:                                           │
│  - 9:00 AM - Dr. Smith - John Doe (Consultation)           │
│  - 10:00 AM - Dr. Johnson - Jane Smith (Follow-up)         │
│  - 11:30 AM - Dr. Smith - Bob Wilson (Routine Checkup)     │
│                                                              │
│  Recent Activities:                                          │
│  - Prescription #P-2024-001 issued to John Doe              │
│  - Appointment confirmed for Jane Smith                     │
│  - Medicine dispensed: Amoxicillin 500mg                    │
│  - Payment received: $150 (Consultation)                    │
│                                                              │
│  Alerts:                                                     │
│  ⚠️ 5 medications expiring in 30 days                       │
│  ⚠️ 3 appointments need confirmation                        │
│  ⚠️ 2 prescriptions pending review                          │
│  💰 5 invoices pending payment                              │
└─────────────────────────────────────────────────────────────┘

Main Menu:
├─ 👨‍⚕️ Doctors
│  ├─ View All Doctors
│  ├─ Add New Doctor
│  ├─ Doctor Schedules
│  └─ Performance Reports
│
├─ 👥 Patients
│  ├─ View All Patients
│  ├─ Register New Patient
│  ├─ Patient History
│  └─ Search Patients
│
├─ 📅 Appointments
│  ├─ Today's Appointments
│  ├─ Schedule New Appointment
│  ├─ Calendar View
│  └─ Appointment History
│
├─ 📋 Prescriptions
│  ├─ Active Prescriptions
│  ├─ Create Prescription
│  ├─ Prescription History
│  └─ Pending Reviews
│
├─ 💊 Pharmacy
│  ├─ Pharmaceuticals
│  ├─ Dispense Medicine
│  ├─ Stock Management
│  └─ Expiry Alerts
│
├─ 🏥 Inventory
│  ├─ Medical Supplies
│  ├─ Equipment
│  ├─ Stock Levels
│  └─ Reorder Management
│
├─ 💰 Billing & Payments
│  ├─ Generate Invoice
│  ├─ Record Payment
│  ├─ Payment History
│  ├─ Outstanding Invoices
│  └─ Financial Reports
│
└─ 📊 Reports
   ├─ Daily Summary
   ├─ Doctor Performance
   ├─ Patient Statistics
   ├─ Revenue Reports
   ├─ Inventory Reports
   └─ Custom Reports
```

---

## Typical Workflows

### Workflow 1: Patient Visit - Complete Flow

**Step 1: Patient Arrives**
- Receptionist checks appointment
- Updates appointment status: Scheduled → Confirmed

**Step 2: Consultation**
- Doctor starts consultation
- Updates appointment status: Confirmed → In Progress
- Doctor examines patient
- Doctor creates prescription (Draft)

**Step 3: Prescription**
- Doctor reviews prescription (Draft → Reviewed)
- Doctor issues prescription (Reviewed → Issued)
- System generates prescription document

**Step 4: Pharmacy**
- Patient goes to pharmacy with prescription
- Pharmacist dispenses medicine (Issued → Dispensed)
- System automatically reduces medicine stock
- Prescription marked as Dispensed

**Step 5: Billing**
- Receptionist generates invoice:
  - Consultation fee: $100
  - Medicines: $50
  - Total: $150
- Patient pays
- Receptionist records payment
- System generates receipt

**Step 6: Completion**
- Appointment marked as Completed
- Prescription marked as Completed
- Patient record updated with visit history

### Workflow 2: Inventory Management

**Low Stock Alert**
- System detects Paracetamol below reorder level
- Notification sent to pharmacist

**Reorder Process**
- Pharmacist creates purchase order (if module enabled)
- Or manually orders from supplier

**Stock Receipt**
- New stock arrives
- Pharmacist creates "Receive Stock" transaction
- Enters batch number, expiry date
- System increases stock quantity

**Expiry Monitoring**
- System monitors expiry dates
- Sends alerts 30 days before expiry
- Pharmacist creates "Dispose Expired" transaction
- System reduces stock quantity

### Workflow 3: Doctor Schedule Management

**Setting Up Doctor Schedule**
- Admin creates "Doctor" item for Dr. Smith
- Sets:
  - Specialization: General Physician
  - Consultation Fee: $100
  - Available Days: Monday, Wednesday, Friday
  - Hours: 9:00 AM - 5:00 PM

**Booking Appointment**
- Receptionist creates "Appointment" item
- Selects:
  - Patient: John Doe
  - Doctor: Dr. Smith
  - Date: Next Monday, 10:00 AM
  - Reason: Routine Checkup
- System checks doctor availability
- Appointment created with status: Scheduled

**Reminder System**
- 24 hours before appointment
- System sends notification to patient
- SMS/Email: "Reminder: You have an appointment with Dr. Smith tomorrow at 10:00 AM"

---

## Financial Management

### Invoice Generation

**Consultation Invoice Example:**
```
┌─────────────────────────────────────────────────┐
│  City Medical Clinic                             │
│  Invoice #INV-2024-001                          │
│  Date: January 15, 2024                         │
├─────────────────────────────────────────────────┤
│  Patient: John Doe                               │
│  Patient ID: P-001                               │
│  Doctor: Dr. Smith                               │
├─────────────────────────────────────────────────┤
│  Description              Qty    Rate    Amount  │
│  Consultation              1    $100     $100    │
│  Paracetamol 500mg        10     $2      $20     │
│  Amoxicillin 250mg        15     $3      $45     │
│                                                   │
│  Subtotal:                               $165    │
│  Tax (5%):                               $8.25   │
│  Total:                                  $173.25 │
├─────────────────────────────────────────────────┤
│  Payment Method: Cash                            │
│  Amount Paid: $173.25                            │
│  Balance: $0.00                                  │
│                                                   │
│  Thank you for visiting City Medical Clinic!     │
└─────────────────────────────────────────────────┘
```

### Payment Receipt

```
┌─────────────────────────────────────────────────┐
│  City Medical Clinic                             │
│  Payment Receipt #REC-2024-001                  │
│  Date: January 15, 2024                         │
├─────────────────────────────────────────────────┤
│  Received from: John Doe                         │
│  Patient ID: P-001                               │
│                                                   │
│  Amount: $173.25                                 │
│  Payment Method: Cash                            │
│  For: Invoice #INV-2024-001                     │
│                                                   │
│  Received by: Sarah (Receptionist)               │
│  Signature: _______________                      │
│                                                   │
│  Thank you for your payment!                     │
└─────────────────────────────────────────────────┘
```

### Financial Reports

**Daily Revenue Report:**
```
Date: January 15, 2024

Consultations:
- Dr. Smith: 5 patients × $100 = $500
- Dr. Johnson: 3 patients × $120 = $360
Total Consultations: $860

Pharmacy Sales:
- Prescriptions dispensed: 8
- Total medicine sales: $340

Total Revenue: $1,200
Payments Received: $1,050
Outstanding: $150
```

---

## Key Benefits for Clinics

### 1. **All-in-One Solution**
- No need for separate systems for inventory, appointments, billing
- Single platform for everything
- Unified data and reports

### 2. **Flexible & Customizable**
- Add custom fields as needed
- Create custom workflows
- Adapt to clinic's specific needs

### 3. **Cost-Effective**
- $199-$999/month vs $50K+ for custom clinic management software
- No separate costs for inventory, billing, appointment systems

### 4. **Easy to Use**
- Web-based interface
- No installation required
- Access from anywhere
- Mobile-friendly

### 5. **Comprehensive Tracking**
- Complete patient history
- Prescription tracking
- Inventory management
- Financial records
- All in one place

### 6. **Automated Workflows**
- Automatic stock reduction when dispensing
- Automatic invoice generation
- Appointment reminders
- Expiry alerts
- Low stock notifications

### 7. **Compliance & Audit Trail**
- Complete history of all transactions
- Who did what, when
- Immutable audit logs
- Helps with regulatory compliance

---

## Comparison: Clinic vs Hospital

| Feature | Clinic Template | Hospital Template |
|---------|----------------|-------------------|
| **Focus** | Outpatient care | Inpatient + Outpatient |
| **Doctors** | 5-20 doctors | 50-500 doctors |
| **Patients** | Outpatient only | Inpatient + Outpatient |
| **Pharmacy** | Small pharmacy | Large pharmacy + multiple locations |
| **Equipment** | Basic equipment | Complex medical equipment + calibration |
| **Billing** | Simple invoicing | Complex billing + insurance claims |
| **Appointments** | Daily scheduling | Complex scheduling + emergency |
| **Inventory** | Medicines + basic supplies | Extensive inventory + equipment tracking |

Both use the same platform, just different configurations!

---

## Technical Implementation Notes

### How "Doctors" Work as Items

```python
# When clinic creates a doctor
doctor = Item.objects.create(
    tenant=clinic_tenant,
    item_type=ItemType.objects.get(name="Doctors"),
    code="DOC-001",
    name="Dr. John Smith",
    quantity=1,  # 1 doctor
    location=Location.objects.get(name="Main Clinic")
)

# Custom field values
ItemCustomFieldValue.objects.create(
    item=doctor,
    custom_field=CustomField.objects.get(name="Specialization"),
    value_text="General Physician"
)

ItemCustomFieldValue.objects.create(
    item=doctor,
    custom_field=CustomField.objects.get(name="Consultation Fee"),
    value_number=100.00
)
```

### How Prescriptions Link to Patients

```python
# When creating a prescription
prescription = Item.objects.create(
    tenant=clinic_tenant,
    item_type=ItemType.objects.get(name="Prescriptions"),
    code="P-2024-001",
    name="Prescription for John Doe"
)

# Link to patient via custom fields
ItemCustomFieldValue.objects.create(
    item=prescription,
    custom_field=CustomField.objects.get(name="Patient ID"),
    value_text="P-001"  # References the patient item
)

ItemCustomFieldValue.objects.create(
    item=prescription,
    custom_field=CustomField.objects.get(name="Doctor Name"),
    value_text="Dr. John Smith"
)
```

### How Dispensing Reduces Stock

```python
# When pharmacist dispenses medicine
transaction = Transaction.objects.create(
    tenant=clinic_tenant,
    transaction_type=TransactionType.objects.get(name="Dispense Medicine"),
    reference_number="DISP-2024-001"
)

# Add medicine to transaction
TransactionItem.objects.create(
    transaction=transaction,
    item=Item.objects.get(code="MED-001"),  # Paracetamol
    quantity=10,  # 10 tablets
    from_location=Location.objects.get(name="Pharmacy"),
    to_location=None  # Dispensed to patient
)

# System automatically reduces stock
medicine.quantity -= 10
medicine.save()
```

---

## Conclusion

Omnify's flexibility allows a **medical clinic** to manage:
- ✅ Inventory (medicines, supplies, equipment)
- ✅ Prescriptions (creation, review, dispensing)
- ✅ Billing & Payments (invoices, receipts, financial reports)
- ✅ Doctors (profiles, schedules, fees)
- ✅ Patients (registration, history, contact info)
- ✅ Appointments (scheduling, reminders, tracking)

**All using the same core platform with different configurations!**

The key insight: **"Items" can represent anything** - physical products, people, documents, appointments, or any entity you need to track and manage.

This makes Omnify incredibly versatile and applicable to countless industries beyond traditional inventory management.

---

*Document Version: 1.0*  
*Created: [Current Date]*  
*Purpose: Reference example for clinic use case*

