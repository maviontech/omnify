"""
Management command to create sample tenants and data for all industries.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.tenants.models import Tenant, TenantConfiguration

User = get_user_model()


class Command(BaseCommand):
    help = 'Create sample tenants for all supported industries'
    
    def handle(self, *args, **options):
        self.stdout.write('Creating sample tenants...')
        
        industries = [
            ('hospital', 'City General Hospital', 'A large metropolitan hospital'),
            ('factory', 'TechManufacturing Inc', 'Electronics manufacturing facility'),
            ('clinic', 'HealthCare Clinic', 'Family medical clinic'),
            ('library', 'Central Public Library', 'City public library system'),
            ('school', 'Lincoln High School', 'Public high school'),
            ('retail', 'Fashion Boutique', 'Clothing retail store'),
            ('restaurant', 'Gourmet Bistro', 'Fine dining restaurant'),
            ('construction', 'BuildRight Construction', 'Commercial construction company'),
        ]
        
        for industry_code, name, description in industries:
            # Create tenant
            tenant, created = Tenant.objects.get_or_create(
                slug=name.lower().replace(' ', '-'),
                defaults={
                    'name': name,
                    'industry': industry_code,
                    'subscription_tier': 'professional',
                }
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Created tenant: {name}'))
                
                # Create configuration
                TenantConfiguration.objects.create(
                    tenant=tenant,
                    primary_color='#0066FF',
                    enable_workflows=True,
                    enable_notifications=True,
                    enable_reports=True,
                    max_users=50,
                    max_items=10000,
                )
                
                # Create admin user for this tenant
                admin_email = f'admin@{tenant.slug}.com'
                user, user_created = User.objects.get_or_create(
                    email=admin_email,
                    defaults={
                        'tenant': tenant,
                        'first_name': 'Admin',
                        'last_name': name.split()[0],
                        'is_staff': True,
                        'is_active': True,
                    }
                )
                
                if user_created:
                    user.set_password('admin123')
                    user.save()
                    self.stdout.write(self.style.SUCCESS(f'  ✓ Created admin user: {admin_email} (password: admin123)'))
            else:
                self.stdout.write(self.style.WARNING(f'  - Tenant already exists: {name}'))
        
        # Create superuser if doesn't exist
        if not User.objects.filter(email='superadmin@omnify.com').exists():
            superuser = User.objects.create_superuser(
                email='superadmin@omnify.com',
                password='admin123',
                first_name='Super',
                last_name='Admin',
            )
            self.stdout.write(self.style.SUCCESS('\n✓ Created superuser: superadmin@omnify.com (password: admin123)'))
        
        self.stdout.write(self.style.SUCCESS('\n✅ Sample data created successfully!'))
        self.stdout.write('\nYou can now login with:')
        self.stdout.write('  - Superuser: superadmin@omnify.com / admin123')
        self.stdout.write('  - Hospital: admin@city-general-hospital.com / admin123')
        self.stdout.write('  - Factory: admin@techmanufacturing-inc.com / admin123')
        self.stdout.write('  - Clinic: admin@healthcare-clinic.com / admin123')
        self.stdout.write('  - Library: admin@central-public-library.com / admin123')
        self.stdout.write('  - School: admin@lincoln-high-school.com / admin123')
        self.stdout.write('  - Retail: admin@fashion-boutique.com / admin123')
        self.stdout.write('  - Restaurant: admin@gourmet-bistro.com / admin123')
        self.stdout.write('  - Construction: admin@buildright-construction.com / admin123')
