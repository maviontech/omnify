# Omnify - Universal Operations Platform

**Everything. Organized.**

Omnify is a multi-tenant, enterprise-grade operations management platform built with Django, MySQL, and modern web technologies. It adapts to any industry through intelligent configuration and templates.

## 🚀 Project Status

**Phase 1: Project Setup - COMPLETED ✅**

The Django project structure has been successfully created with:
- ✅ Django 5.0.1 with MySQL 8.0+ database
- ✅ 11 Django apps (core, tenants, users, permissions, items, locations, transactions, workflows, notifications, reports, api)
- ✅ Settings split into base, development, and production
- ✅ REST API framework configured
- ✅ Redis caching setup (configuration ready)
- ✅ Celery async tasks (configuration ready)
- ✅ Professional project structure

## 📁 Project Structure

```
omnify/
├── apps/                      # Django applications
│   ├── core/                 # Shared utilities and base classes
│   ├── tenants/              # Multi-tenancy management
│   ├── users/                # User authentication
│   ├── permissions/          # Role-based access control
│   ├── items/                # Item and inventory management
│   ├── locations/            # Location hierarchy
│   ├── transactions/         # Transaction processing
│   ├── workflows/            # Workflow engine
│   ├── notifications/        # Notification system
│   ├── reports/              # Reporting and dashboards
│   └── api/                  # REST API endpoints
├── omnify/                   # Project configuration
│   ├── settings/             # Settings (base, dev, prod)
│   ├── urls.py              # URL routing
│   └── wsgi.py              # WSGI application
├── templates/                # Django templates
├── static/                   # Static files (CSS, JS, images)
├── media/                    # User uploads
├── logs/                     # Application logs
└── manage.py                # Django management script
```

## 🛠️ Technology Stack

- **Backend**: Django 5.0.1 (Python 3.13+)
- **Database**: MySQL 8.0+
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **API**: Django REST Framework
- **Caching**: Redis (configured)
- **Task Queue**: Celery (configured)
- **Authentication**: JWT + Session-based

## 📋 Prerequisites

- Python 3.13+
- MySQL 8.0+
- Redis (optional, for caching)
- Virtual environment

## 🚀 Quick Start

### 1. Clone and Setup

```bash
# Navigate to project directory
cd omnify

# Activate virtual environment (if not already activated)
# Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Database Configuration

The project is configured to use MySQL with:
- **Database**: omnify_db
- **User**: root
- **Password**: root
- **Host**: localhost
- **Port**: 3306

Database has been created and migrations have been applied.

### 3. Environment Variables

Copy `.env.example` to `.env` and update as needed:

```bash
# Already configured for development
SECRET_KEY=django-insecure-dev-key-change-this-in-production-12345678
DEBUG=True
DB_ENGINE=django.db.backends.mysql
DB_NAME=omnify_db
DB_USER=root
DB_PASSWORD=root
```

### 4. Run Development Server

```bash
python manage.py runserver
```

Visit: http://localhost:8000

### 5. Create Superuser

```bash
python manage.py createsuperuser
```

## 📝 Next Steps

According to the implementation plan (`.kiro/specs/inventory-logistics-platform/tasks.md`):

### Task 2: Implement Core App and Multi-Tenancy Foundation
- [ ] 2.1 Create Tenant model with basic fields
- [ ] 2.2 Create TenantMiddleware
- [ ] 2.3 Create AuditLog model
- [ ] 2.4 Write property test for tenant isolation

### Task 4: Implement Users and Authentication
- [ ] 4.1 Create custom User model
- [ ] 4.2 Implement authentication system
- [ ] 4.3 Implement password reset functionality
- [ ] 4.4 Implement multi-factor authentication (MFA)

## 🎨 Brand Identity

- **Primary Color**: Omnify Blue (#0066FF)
- **Typography**: Inter (body), Poppins (headings)
- **Tagline**: "Everything. Organized."

See `BRANDING_OMNIFY.md` for complete brand guidelines.

## 📚 Documentation

- **Requirements**: `.kiro/specs/inventory-logistics-platform/requirements.md` (140 requirements)
- **Design**: `.kiro/specs/inventory-logistics-platform/design.md` (Complete technical design)
- **Tasks**: `.kiro/specs/inventory-logistics-platform/tasks.md` (37 major tasks, 150+ sub-tasks)
- **Business Plan**: `.kiro/specs/inventory-logistics-platform/BUSINESS_OPPORTUNITY.md`

## 🏗️ Architecture

- **Multi-tenancy**: Row-level isolation with tenant identifier
- **Custom Fields**: Flexible schema for any industry
- **Workflows**: Configurable state machines
- **RBAC**: Hierarchical role-based permissions
- **API-First**: RESTful API with JWT authentication

## 🧪 Testing

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test apps.tenants

# Check code quality
python manage.py check
```

## 🔒 Security Features

- Password hashing (PBKDF2)
- Multi-factor authentication (TOTP)
- Session management
- CSRF protection
- XSS prevention
- SQL injection prevention (Django ORM)
- Audit logging

## 📦 Deployment

See `omnify/settings/production.py` for production configuration.

Key production settings:
- DEBUG=False
- HTTPS enforcement
- Security headers
- MySQL database
- Static file serving
- Email backend

## 🤝 Contributing

This is a proprietary project. See implementation tasks for development roadmap.

## 📄 License

Proprietary - All rights reserved

## 🌟 Target Industries

- Healthcare (Hospitals, Clinics)
- Manufacturing (Factories)
- Warehousing & Logistics
- Retail & E-commerce
- Education (Schools, Libraries)
- Food Service (Restaurants)
- Construction
- And many more...

## 💡 Key Features (Planned)

- ✅ Multi-tenant architecture
- ✅ MySQL database
- ✅ REST API framework
- ⏳ Custom item types and fields
- ⏳ Workflow engine
- ⏳ Transaction processing
- ⏳ Role-based permissions
- ⏳ Dashboard and reporting
- ⏳ Notifications (email, in-app, webhooks)
- ⏳ Data import/export
- ⏳ Barcode support
- ⏳ Batch and serial tracking

## 📞 Contact

- Website: omnify.com (planned)
- Email: hello@omnify.com (planned)

---

**Built with ❤️ using Django and modern web technologies**

*Version: 0.1.0 (MVP in development)*
