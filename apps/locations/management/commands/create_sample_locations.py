"""
Management command to create sample locations for all tenants.
"""
from django.core.management.base import BaseCommand
from apps.tenants.models import Tenant
from apps.locations.models import Location


class Command(BaseCommand):
    help = 'Create sample locations for all tenants'

    def handle(self, *args, **options):
        tenants = Tenant.objects.all()
        
        for tenant in tenants:
            self.stdout.write(f"Creating locations for {tenant.name}...")
            
            # Create industry-specific locations
            if tenant.industry == 'hospital':
                self.create_hospital_locations(tenant)
            elif tenant.industry == 'factory':
                self.create_factory_locations(tenant)
            elif tenant.industry == 'clinic':
                self.create_clinic_locations(tenant)
            elif tenant.industry == 'library':
                self.create_library_locations(tenant)
            elif tenant.industry == 'school':
                self.create_school_locations(tenant)
            elif tenant.industry == 'retail':
                self.create_retail_locations(tenant)
            elif tenant.industry == 'restaurant':
                self.create_restaurant_locations(tenant)
            elif tenant.industry == 'construction':
                self.create_construction_locations(tenant)
            
            self.stdout.write(self.style.SUCCESS(f"✓ Created locations for {tenant.name}"))
        
        self.stdout.write(self.style.SUCCESS('\n✓ All sample locations created successfully!'))

    def create_hospital_locations(self, tenant):
        """Create hospital-specific locations."""
        main = Location.objects.create(
            tenant=tenant, name='Main Hospital Building', code='MAIN',
            location_type='building', address='123 Medical Center Dr',
            city='Healthcare City', state='CA', postal_code='90001', country='USA'
        )
        
        floor1 = Location.objects.create(
            tenant=tenant, name='Floor 1 - Emergency', code='F1',
            location_type='floor', parent=main
        )
        floor2 = Location.objects.create(
            tenant=tenant, name='Floor 2 - Surgery', code='F2',
            location_type='floor', parent=main
        )
        
        Location.objects.create(
            tenant=tenant, name='ER Room 101', code='ER101',
            location_type='room', parent=floor1, capacity=50, capacity_unit='items'
        )
        Location.objects.create(
            tenant=tenant, name='ER Room 102', code='ER102',
            location_type='room', parent=floor1, capacity=50, capacity_unit='items'
        )
        Location.objects.create(
            tenant=tenant, name='OR 201', code='OR201',
            location_type='room', parent=floor2, capacity=100, capacity_unit='items'
        )
        Location.objects.create(
            tenant=tenant, name='OR 202', code='OR202',
            location_type='room', parent=floor2, capacity=100, capacity_unit='items'
        )
        
        # Pharmacy
        pharmacy = Location.objects.create(
            tenant=tenant, name='Central Pharmacy', code='PHARM',
            location_type='room', parent=floor1, capacity=1000, capacity_unit='items'
        )

    def create_factory_locations(self, tenant):
        """Create factory-specific locations."""
        warehouse = Location.objects.create(
            tenant=tenant, name='Main Warehouse', code='WH01',
            location_type='warehouse', address='456 Industrial Blvd',
            city='Factory Town', state='TX', postal_code='75001', country='USA',
            capacity=10000, capacity_unit='items'
        )
        
        zone_a = Location.objects.create(
            tenant=tenant, name='Zone A - Raw Materials', code='ZONE_A',
            location_type='zone', parent=warehouse
        )
        zone_b = Location.objects.create(
            tenant=tenant, name='Zone B - Finished Goods', code='ZONE_B',
            location_type='zone', parent=warehouse
        )
        
        for i in range(1, 6):
            aisle = Location.objects.create(
                tenant=tenant, name=f'Aisle {i}', code=f'A{i}',
                location_type='aisle', parent=zone_a
            )
            for j in range(1, 4):
                Location.objects.create(
                    tenant=tenant, name=f'Shelf {j}', code=f'A{i}S{j}',
                    location_type='shelf', parent=aisle, capacity=200, capacity_unit='items'
                )

    def create_clinic_locations(self, tenant):
        """Create clinic-specific locations."""
        clinic = Location.objects.create(
            tenant=tenant, name='Main Clinic', code='CLINIC',
            location_type='building', address='789 Health St',
            city='Wellness City', state='FL', postal_code='33101', country='USA'
        )
        
        Location.objects.create(
            tenant=tenant, name='Exam Room 1', code='EXAM1',
            location_type='room', parent=clinic, capacity=30, capacity_unit='items'
        )
        Location.objects.create(
            tenant=tenant, name='Exam Room 2', code='EXAM2',
            location_type='room', parent=clinic, capacity=30, capacity_unit='items'
        )
        Location.objects.create(
            tenant=tenant, name='Lab', code='LAB',
            location_type='room', parent=clinic, capacity=100, capacity_unit='items'
        )
        Location.objects.create(
            tenant=tenant, name='Supply Closet', code='SUPPLY',
            location_type='room', parent=clinic, capacity=200, capacity_unit='items'
        )

    def create_library_locations(self, tenant):
        """Create library-specific locations."""
        library = Location.objects.create(
            tenant=tenant, name='Central Library', code='LIB',
            location_type='building', address='321 Book Ave',
            city='Reading Town', state='NY', postal_code='10001', country='USA'
        )
        
        floor1 = Location.objects.create(
            tenant=tenant, name='Floor 1 - Fiction', code='F1',
            location_type='floor', parent=library
        )
        floor2 = Location.objects.create(
            tenant=tenant, name='Floor 2 - Non-Fiction', code='F2',
            location_type='floor', parent=library
        )
        
        for section in ['A', 'B', 'C', 'D']:
            aisle = Location.objects.create(
                tenant=tenant, name=f'Section {section}', code=f'SEC{section}',
                location_type='aisle', parent=floor1
            )
            for i in range(1, 6):
                Location.objects.create(
                    tenant=tenant, name=f'Shelf {i}', code=f'{section}S{i}',
                    location_type='shelf', parent=aisle, capacity=100, capacity_unit='books'
                )

    def create_school_locations(self, tenant):
        """Create school-specific locations."""
        school = Location.objects.create(
            tenant=tenant, name='Main School Building', code='SCHOOL',
            location_type='building', address='555 Education Rd',
            city='Learning City', state='MA', postal_code='02101', country='USA'
        )
        
        Location.objects.create(
            tenant=tenant, name='Science Lab', code='SCILAB',
            location_type='room', parent=school, capacity=50, capacity_unit='items'
        )
        Location.objects.create(
            tenant=tenant, name='Computer Lab', code='COMPLAB',
            location_type='room', parent=school, capacity=30, capacity_unit='items'
        )
        Location.objects.create(
            tenant=tenant, name='Supply Room', code='SUPPLY',
            location_type='room', parent=school, capacity=200, capacity_unit='items'
        )
        Location.objects.create(
            tenant=tenant, name='Library', code='LIBRARY',
            location_type='room', parent=school, capacity=500, capacity_unit='books'
        )

    def create_retail_locations(self, tenant):
        """Create retail-specific locations."""
        store = Location.objects.create(
            tenant=tenant, name='Main Store', code='STORE',
            location_type='building', address='888 Shopping Plaza',
            city='Retail City', state='IL', postal_code='60601', country='USA'
        )
        
        Location.objects.create(
            tenant=tenant, name='Sales Floor', code='SALES',
            location_type='zone', parent=store, capacity=500, capacity_unit='items'
        )
        
        backroom = Location.objects.create(
            tenant=tenant, name='Back Room', code='BACK',
            location_type='zone', parent=store
        )
        
        for i in range(1, 5):
            Location.objects.create(
                tenant=tenant, name=f'Storage Shelf {i}', code=f'SHELF{i}',
                location_type='shelf', parent=backroom, capacity=100, capacity_unit='items'
            )

    def create_restaurant_locations(self, tenant):
        """Create restaurant-specific locations."""
        restaurant = Location.objects.create(
            tenant=tenant, name='Main Restaurant', code='REST',
            location_type='building', address='999 Culinary Blvd',
            city='Food City', state='CA', postal_code='90210', country='USA'
        )
        
        Location.objects.create(
            tenant=tenant, name='Kitchen', code='KITCHEN',
            location_type='room', parent=restaurant, capacity=100, capacity_unit='items'
        )
        Location.objects.create(
            tenant=tenant, name='Walk-in Freezer', code='FREEZER',
            location_type='room', parent=restaurant, capacity=200, capacity_unit='items'
        )
        Location.objects.create(
            tenant=tenant, name='Walk-in Refrigerator', code='FRIDGE',
            location_type='room', parent=restaurant, capacity=200, capacity_unit='items'
        )
        Location.objects.create(
            tenant=tenant, name='Dry Storage', code='DRY',
            location_type='room', parent=restaurant, capacity=300, capacity_unit='items'
        )
        Location.objects.create(
            tenant=tenant, name='Bar', code='BAR',
            location_type='room', parent=restaurant, capacity=150, capacity_unit='items'
        )

    def create_construction_locations(self, tenant):
        """Create construction-specific locations."""
        yard = Location.objects.create(
            tenant=tenant, name='Main Yard', code='YARD',
            location_type='warehouse', address='777 Builder St',
            city='Construction City', state='AZ', postal_code='85001', country='USA',
            capacity=5000, capacity_unit='items'
        )
        
        Location.objects.create(
            tenant=tenant, name='Tool Shed', code='TOOLS',
            location_type='building', parent=yard, capacity=200, capacity_unit='items'
        )
        Location.objects.create(
            tenant=tenant, name='Materials Storage', code='MATERIALS',
            location_type='zone', parent=yard, capacity=1000, capacity_unit='items'
        )
        Location.objects.create(
            tenant=tenant, name='Equipment Garage', code='GARAGE',
            location_type='building', parent=yard, capacity=50, capacity_unit='items'
        )
        Location.objects.create(
            tenant=tenant, name='Office Trailer', code='OFFICE',
            location_type='building', parent=yard, capacity=30, capacity_unit='items'
        )
