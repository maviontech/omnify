"""
Management command to create sample items for all tenants.
"""
from django.core.management.base import BaseCommand
from apps.tenants.models import Tenant
from apps.items.models import ItemType, CustomField, Item
from apps.locations.models import Location
from decimal import Decimal


class Command(BaseCommand):
    help = 'Create sample items for all tenants'

    def handle(self, *args, **options):
        tenants = Tenant.objects.all()
        
        for tenant in tenants:
            self.stdout.write(f"Creating items for {tenant.name}...")
            
            # Create industry-specific item types and items
            if tenant.industry == 'hospital':
                self.create_hospital_items(tenant)
            elif tenant.industry == 'factory':
                self.create_factory_items(tenant)
            elif tenant.industry == 'clinic':
                self.create_clinic_items(tenant)
            elif tenant.industry == 'library':
                self.create_library_items(tenant)
            elif tenant.industry == 'school':
                self.create_school_items(tenant)
            elif tenant.industry == 'retail':
                self.create_retail_items(tenant)
            elif tenant.industry == 'restaurant':
                self.create_restaurant_items(tenant)
            elif tenant.industry == 'construction':
                self.create_construction_items(tenant)
            
            self.stdout.write(self.style.SUCCESS(f"✓ Created items for {tenant.name}"))
        
        self.stdout.write(self.style.SUCCESS('\n✓ All sample items created successfully!'))

    def create_hospital_items(self, tenant):
        """Create hospital-specific items."""
        # Item Types
        medical_supplies = ItemType.objects.create(
            tenant=tenant, name='Medical Supplies', description='General medical supplies'
        )
        medications = ItemType.objects.create(
            tenant=tenant, name='Medications', description='Pharmaceutical products'
        )
        equipment = ItemType.objects.create(
            tenant=tenant, name='Medical Equipment', description='Medical devices and equipment'
        )
        
        # Custom Fields for Medications
        CustomField.objects.create(
            item_type=medications, name='Dosage', field_type='text',
            is_required=True, display_order=1
        )
        CustomField.objects.create(
            item_type=medications, name='Expiration Date', field_type='date',
            is_required=True, display_order=2
        )
        
        # Get locations
        locations = Location.objects.filter(tenant=tenant, location_type='room')
        if not locations.exists():
            locations = Location.objects.filter(tenant=tenant)
        
        # Create items
        Item.objects.create(
            tenant=tenant, item_type=medical_supplies, code='GLOVE-001',
            name='Nitrile Gloves (Box of 100)', quantity=Decimal('50'),
            unit='boxes', unit_cost=Decimal('12.99'), selling_price=Decimal('19.99'),
            location=locations.first(), reorder_point=Decimal('10'), reorder_quantity=Decimal('20')
        )
        Item.objects.create(
            tenant=tenant, item_type=medical_supplies, code='MASK-001',
            name='Surgical Masks (Box of 50)', quantity=Decimal('100'),
            unit='boxes', unit_cost=Decimal('8.99'), selling_price=Decimal('14.99'),
            location=locations.first(), reorder_point=Decimal('20'), reorder_quantity=Decimal('50')
        )
        Item.objects.create(
            tenant=tenant, item_type=equipment, code='BP-001',
            name='Blood Pressure Monitor', quantity=Decimal('5'),
            unit='units', unit_cost=Decimal('89.99'), selling_price=Decimal('149.99'),
            location=locations.first()
        )

    def create_factory_items(self, tenant):
        """Create factory-specific items."""
        raw_materials = ItemType.objects.create(
            tenant=tenant, name='Raw Materials', description='Manufacturing raw materials'
        )
        finished_goods = ItemType.objects.create(
            tenant=tenant, name='Finished Goods', description='Completed products'
        )
        
        locations = Location.objects.filter(tenant=tenant, location_type='shelf')
        if not locations.exists():
            locations = Location.objects.filter(tenant=tenant)
        
        Item.objects.create(
            tenant=tenant, item_type=raw_materials, code='STEEL-001',
            name='Steel Sheet 4x8ft', quantity=Decimal('200'),
            unit='sheets', unit_cost=Decimal('45.00'), location=locations.first(),
            reorder_point=Decimal('50'), reorder_quantity=Decimal('100')
        )
        Item.objects.create(
            tenant=tenant, item_type=raw_materials, code='BOLT-001',
            name='M10 Bolts', quantity=Decimal('5000'),
            unit='pieces', unit_cost=Decimal('0.25'), location=locations.first(),
            reorder_point=Decimal('1000'), reorder_quantity=Decimal('2000')
        )
        Item.objects.create(
            tenant=tenant, item_type=finished_goods, code='WIDGET-001',
            name='Standard Widget', quantity=Decimal('150'),
            unit='units', unit_cost=Decimal('12.50'), selling_price=Decimal('24.99'),
            location=locations.last()
        )

    def create_clinic_items(self, tenant):
        """Create clinic-specific items."""
        supplies = ItemType.objects.create(
            tenant=tenant, name='Medical Supplies', description='Clinic supplies'
        )
        
        locations = Location.objects.filter(tenant=tenant)
        
        Item.objects.create(
            tenant=tenant, item_type=supplies, code='SYRINGE-001',
            name='Disposable Syringes 10ml', quantity=Decimal('200'),
            unit='pieces', unit_cost=Decimal('0.50'), location=locations.first(),
            reorder_point=Decimal('50'), reorder_quantity=Decimal('100')
        )
        Item.objects.create(
            tenant=tenant, item_type=supplies, code='BANDAGE-001',
            name='Adhesive Bandages', quantity=Decimal('100'),
            unit='boxes', unit_cost=Decimal('3.99'), location=locations.first(),
            reorder_point=Decimal('20'), reorder_quantity=Decimal('50')
        )

    def create_library_items(self, tenant):
        """Create library-specific items."""
        books = ItemType.objects.create(
            tenant=tenant, name='Books', description='Library books'
        )
        media = ItemType.objects.create(
            tenant=tenant, name='Media', description='DVDs, CDs, etc.'
        )
        
        # Custom Fields for Books
        CustomField.objects.create(
            item_type=books, name='ISBN', field_type='text',
            is_required=True, display_order=1
        )
        CustomField.objects.create(
            item_type=books, name='Author', field_type='text',
            is_required=True, display_order=2
        )
        CustomField.objects.create(
            item_type=books, name='Publication Year', field_type='number',
            display_order=3
        )
        
        locations = Location.objects.filter(tenant=tenant, location_type='shelf')
        if not locations.exists():
            locations = Location.objects.filter(tenant=tenant)
        
        Item.objects.create(
            tenant=tenant, item_type=books, code='BOOK-001',
            name='The Great Gatsby', quantity=Decimal('3'),
            unit='copies', location=locations.first()
        )
        Item.objects.create(
            tenant=tenant, item_type=books, code='BOOK-002',
            name='To Kill a Mockingbird', quantity=Decimal('5'),
            unit='copies', location=locations.first()
        )
        Item.objects.create(
            tenant=tenant, item_type=media, code='DVD-001',
            name='Documentary Collection', quantity=Decimal('10'),
            unit='discs', location=locations.last()
        )

    def create_school_items(self, tenant):
        """Create school-specific items."""
        supplies = ItemType.objects.create(
            tenant=tenant, name='School Supplies', description='Educational supplies'
        )
        equipment = ItemType.objects.create(
            tenant=tenant, name='Lab Equipment', description='Science lab equipment'
        )
        
        locations = Location.objects.filter(tenant=tenant)
        
        Item.objects.create(
            tenant=tenant, item_type=supplies, code='PENCIL-001',
            name='No. 2 Pencils (Box of 12)', quantity=Decimal('50'),
            unit='boxes', unit_cost=Decimal('2.99'), location=locations.first(),
            reorder_point=Decimal('10'), reorder_quantity=Decimal('30')
        )
        Item.objects.create(
            tenant=tenant, item_type=supplies, code='PAPER-001',
            name='Printer Paper (Ream)', quantity=Decimal('30'),
            unit='reams', unit_cost=Decimal('4.99'), location=locations.first(),
            reorder_point=Decimal('10'), reorder_quantity=Decimal('20')
        )
        Item.objects.create(
            tenant=tenant, item_type=equipment, code='MICRO-001',
            name='Student Microscope', quantity=Decimal('15'),
            unit='units', unit_cost=Decimal('89.99'), location=locations.last()
        )

    def create_retail_items(self, tenant):
        """Create retail-specific items."""
        clothing = ItemType.objects.create(
            tenant=tenant, name='Clothing', description='Apparel items'
        )
        accessories = ItemType.objects.create(
            tenant=tenant, name='Accessories', description='Fashion accessories'
        )
        
        # Custom Fields for Clothing
        CustomField.objects.create(
            item_type=clothing, name='Size', field_type='dropdown',
            dropdown_options=['XS', 'S', 'M', 'L', 'XL', 'XXL'],
            is_required=True, display_order=1
        )
        CustomField.objects.create(
            item_type=clothing, name='Color', field_type='text',
            is_required=True, display_order=2
        )
        
        locations = Location.objects.filter(tenant=tenant)
        
        Item.objects.create(
            tenant=tenant, item_type=clothing, code='SHIRT-001',
            name='Cotton T-Shirt', quantity=Decimal('100'),
            unit='pieces', unit_cost=Decimal('8.99'), selling_price=Decimal('19.99'),
            location=locations.first(), reorder_point=Decimal('20'), reorder_quantity=Decimal('50')
        )
        Item.objects.create(
            tenant=tenant, item_type=clothing, code='JEANS-001',
            name='Denim Jeans', quantity=Decimal('75'),
            unit='pieces', unit_cost=Decimal('24.99'), selling_price=Decimal('49.99'),
            location=locations.first(), reorder_point=Decimal('15'), reorder_quantity=Decimal('30')
        )
        Item.objects.create(
            tenant=tenant, item_type=accessories, code='HAT-001',
            name='Baseball Cap', quantity=Decimal('50'),
            unit='pieces', unit_cost=Decimal('5.99'), selling_price=Decimal('14.99'),
            location=locations.last()
        )

    def create_restaurant_items(self, tenant):
        """Create restaurant-specific items."""
        ingredients = ItemType.objects.create(
            tenant=tenant, name='Ingredients', description='Food ingredients'
        )
        beverages = ItemType.objects.create(
            tenant=tenant, name='Beverages', description='Drinks and beverages'
        )
        
        locations = Location.objects.filter(tenant=tenant)
        
        Item.objects.create(
            tenant=tenant, item_type=ingredients, code='FLOUR-001',
            name='All-Purpose Flour', quantity=Decimal('50'),
            unit='lbs', unit_cost=Decimal('0.89'), location=locations.first(),
            reorder_point=Decimal('10'), reorder_quantity=Decimal('30')
        )
        Item.objects.create(
            tenant=tenant, item_type=ingredients, code='TOMATO-001',
            name='Fresh Tomatoes', quantity=Decimal('25'),
            unit='lbs', unit_cost=Decimal('2.49'), location=locations.first(),
            reorder_point=Decimal('5'), reorder_quantity=Decimal('20')
        )
        Item.objects.create(
            tenant=tenant, item_type=beverages, code='SODA-001',
            name='Cola (24-pack)', quantity=Decimal('20'),
            unit='cases', unit_cost=Decimal('8.99'), selling_price=Decimal('14.99'),
            location=locations.last(), reorder_point=Decimal('5'), reorder_quantity=Decimal('15')
        )

    def create_construction_items(self, tenant):
        """Create construction-specific items."""
        tools = ItemType.objects.create(
            tenant=tenant, name='Tools', description='Construction tools'
        )
        materials = ItemType.objects.create(
            tenant=tenant, name='Building Materials', description='Construction materials'
        )
        
        locations = Location.objects.filter(tenant=tenant)
        
        Item.objects.create(
            tenant=tenant, item_type=tools, code='HAMMER-001',
            name='Claw Hammer', quantity=Decimal('10'),
            unit='pieces', unit_cost=Decimal('19.99'), location=locations.first()
        )
        Item.objects.create(
            tenant=tenant, item_type=tools, code='DRILL-001',
            name='Cordless Drill', quantity=Decimal('5'),
            unit='pieces', unit_cost=Decimal('89.99'), location=locations.first()
        )
        Item.objects.create(
            tenant=tenant, item_type=materials, code='LUMBER-001',
            name='2x4 Lumber 8ft', quantity=Decimal('200'),
            unit='pieces', unit_cost=Decimal('4.99'), location=locations.last(),
            reorder_point=Decimal('50'), reorder_quantity=Decimal('100')
        )
        Item.objects.create(
            tenant=tenant, item_type=materials, code='CEMENT-001',
            name='Portland Cement (Bag)', quantity=Decimal('50'),
            unit='bags', unit_cost=Decimal('12.99'), location=locations.last(),
            reorder_point=Decimal('10'), reorder_quantity=Decimal('30')
        )
