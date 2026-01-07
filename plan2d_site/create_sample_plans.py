"""
Script to create sample plans for testing the plans browsing feature.
Run with: python manage.py shell < create_sample_plans.py
"""
from apps.plans.models import Category, Plan, PlanPublishStatus

# Create categories
categories_data = [
    {'name': 'Modern', 'description': 'Contemporary designs with clean lines'},
    {'name': 'Traditional', 'description': 'Classic architectural styles'},
    {'name': 'Bungalow', 'description': 'Single-story comfortable homes'},
    {'name': 'Two-Story', 'description': 'Efficient two-level designs'},
]

print("Creating categories...")
for cat_data in categories_data:
    category, created = Category.objects.get_or_create(
        name=cat_data['name'],
        defaults={'description': cat_data['description']}
    )
    if created:
        print(f"✓ Created category: {category.name}")
    else:
        print(f"- Category already exists: {category.name}")

# Create sample plans
plans_data = [
    {
        'title': 'Modern Family Home',
        'reference': 'PL-2026-001',
        'category': 'Modern',
        'bedrooms': 4,
        'bathrooms': 2.5,
        'total_area_sqm': 180.00,
        'price': 299.00,
        'description': '''A spacious modern family home designed for comfortable living. Features an open-concept main floor with large windows for natural light. The kitchen flows seamlessly into the dining and living areas, perfect for entertaining. Four bedrooms upstairs include a master suite with ensuite bathroom.

Ideal for growing families who value both style and functionality.''',
        'publish_status': PlanPublishStatus.PUBLISHED,
        'featured': True,
    },
    {
        'title': 'Compact Starter Home',
        'reference': 'PL-2026-002',
        'category': 'Bungalow',
        'bedrooms': 2,
        'bathrooms': 1.0,
        'total_area_sqm': 85.00,
        'price': 149.00,
        'description': '''Perfect starter home or retirement bungalow. Efficient single-story layout with two comfortable bedrooms and a full bathroom. Open living area combines kitchen, dining, and living room. Large windows provide excellent natural lighting throughout.

Great for first-time buyers or those looking to downsize.''',
        'publish_status': PlanPublishStatus.PUBLISHED,
        'featured': False,
    },
    {
        'title': 'Traditional Colonial',
        'reference': 'PL-2026-003',
        'category': 'Traditional',
        'bedrooms': 5,
        'bathrooms': 3.0,
        'total_area_sqm': 250.00,
        'price': 399.00,
        'description': '''Classic colonial design with timeless appeal. Grand entrance leads to a formal living and dining room. Large family room with fireplace opens to the kitchen. Five bedrooms across two floors, including a luxurious master suite.

Perfect for larger families who appreciate traditional architecture.''',
        'publish_status': PlanPublishStatus.PUBLISHED,
        'featured': True,
    },
    {
        'title': 'Contemporary Two-Story',
        'reference': 'PL-2026-004',
        'category': 'Two-Story',
        'bedrooms': 3,
        'bathrooms': 2.5,
        'total_area_sqm': 160.00,
        'price': 249.00,
        'description': '''Efficient two-story design maximizing space. Main floor features open-concept living with kitchen island and breakfast nook. Upper level houses three bedrooms and two full bathrooms. Covered patio off the main living area.

Ideal for families seeking efficient use of space.''',
    'publish_status': PlanPublishStatus.PUBLISHED,
        'featured': False,
    },
    {
        'title': 'Modern Studio Bungalow',
        'reference': 'PL-2026-005',
        'category': 'Modern',
        'bedrooms': 1,
        'bathrooms': 1.0,
        'total_area_sqm': 65.00,
        'price': 99.00,
        'description': '''Minimalist single-bedroom home with modern aesthetics. Open-plan living area with integrated kitchen. Large bedroom with ample storage. Perfect for individuals or couples.

Great for rental properties or guest houses.''',
    'publish_status': PlanPublishStatus.PUBLISHED,
        'featured': False,
    },
    {
        'title': 'Executive Traditional Home',
        'reference': 'PL-2026-006',
        'category': 'Traditional',
        'bedrooms': 6,
        'bathrooms': 4.0,
        'total_area_sqm': 320.00,
        'price': 499.00,
        'description': '''Luxury traditional home with premium features. Grand foyer, formal living and dining rooms, gourmet kitchen, and family room on main floor. Six spacious bedrooms including master suite with sitting area and spa-like bathroom.

For those seeking elegance and space.''',
    'publish_status': PlanPublishStatus.PUBLISHED,
        'featured': True,
    },
]

print("\nCreating sample plans...")
for plan_data in plans_data:
    category_name = plan_data.pop('category')
    category = Category.objects.get(name=category_name)
    
    plan, created = Plan.objects.get_or_create(
        reference=plan_data['reference'],
        defaults={**plan_data, 'category': category}
    )
    
    if created:
        print(f"✓ Created plan: {plan.reference} - {plan.title}")
    else:
        print(f"- Plan already exists: {plan.reference} - {plan.title}")

print("\n✅ Sample data creation complete!")
print(f"Total categories: {Category.objects.count()}")
print(f"Total plans: {Plan.objects.count()}")
print(f"Published plans: {Plan.objects.published().count()}")
print(f"Featured plans: {Plan.objects.filter(featured=True).count()}")
