"""
Management command to validate frontend plan visibility.
Ensures all published plans are actually visible on the website.

Usage:
    python manage.py validate_frontend_visibility
    python manage.py validate_frontend_visibility --alert-threshold 10
"""
from django.core.management.base import BaseCommand
from django.test import Client
from django.urls import reverse
from apps.plans.models import Plan
from bs4 import BeautifulSoup


class Command(BaseCommand):
    help = 'Validate that all published plans are visible on the frontend'

    def add_arguments(self, parser):
        parser.add_argument(
            '--alert-threshold',
            type=int,
            default=5,
            help='Alert if more than N plans are missing from frontend',
        )

    def handle(self, *args, **options):
        alert_threshold = options['alert_threshold']
        
        self.stdout.write(self.style.HTTP_INFO('=' * 70))
        self.stdout.write(self.style.HTTP_INFO('Frontend Plan Visibility Validation'))
        self.stdout.write(self.style.HTTP_INFO('=' * 70))
        
        # Get all visible plans from database
        visible_plans = Plan.objects.visible()
        total_visible = visible_plans.count()
        
        self.stdout.write(f"\n📊 Database Status:")
        self.stdout.write(f"  Total visible plans (should appear on site): {total_visible}")
        
        if total_visible == 0:
            self.stdout.write(self.style.WARNING('\n⚠ WARNING: No visible plans found in database!'))
            self.stdout.write('  Plans must be published to appear on the website.')
            return
        
        # Test homepage
        self.stdout.write(f"\n🏠 Testing Homepage:")
        client = Client()
        # Use explicit host header to avoid DisallowedHost during test client requests
        try:
            response = client.get('/', HTTP_HOST='127.0.0.1')
            self.stdout.write(f"  Status: {response.status_code}")
            if response.status_code == 200:
                content = response.content.decode('utf-8')
                featured_count = content.count('href="/plans/')  # Basic check
                self.stdout.write(f"  Featured plan links found: ~{featured_count}")
            else:
                self.stdout.write(self.style.ERROR('  ❌ Homepage failed to load!'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ❌ Homepage error: {e}'))
        
        # Test plans listing page
        self.stdout.write(f"\n📋 Testing Plans Listing Page:")
        try:
            response = client.get('/plans/', HTTP_HOST='127.0.0.1')
            self.stdout.write(f"  Status: {response.status_code}")
            
            if response.status_code == 200:
                # Parse HTML to count displayed plans
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for plan cards/items (adjust selector based on your template)
                plan_cards = soup.find_all(class_='plan-card') or soup.find_all('article')
                displayed_count = len(plan_cards)
                
                self.stdout.write(f"  Plans displayed on page 1: {displayed_count}")
                self.stdout.write(f"  Expected visible plans: {total_visible}")
                
                # Check for pagination
                pagination = soup.find(class_='pagination')
                if pagination:
                    self.stdout.write(f"  ✓ Pagination detected (more plans on other pages)")
                
                # Calculate missing plans
                if displayed_count < total_visible and not pagination:
                    missing = total_visible - displayed_count
                    self.stdout.write(self.style.WARNING(
                        f"\n⚠ WARNING: {missing} plans missing from display!"
                    ))
                    
                    if missing > alert_threshold:
                        self.stdout.write(self.style.ERROR(
                            f"❌ ALERT: More than {alert_threshold} plans are hidden!"
                        ))
                elif displayed_count > 0:
                    self.stdout.write(self.style.SUCCESS(
                        f"\n✅ Plans are being displayed correctly"
                    ))
            else:
                self.stdout.write(self.style.ERROR('  ❌ Plans listing page failed to load!'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ❌ Plans listing error: {e}'))
        
        # Test individual plan pages
        self.stdout.write(f"\n🔍 Testing Individual Plan Pages:")
        sample_plans = visible_plans[:3]
        accessible_count = 0
        
        for plan in sample_plans:
            try:
                url = plan.get_absolute_url()
                response = client.get(url, HTTP_HOST='127.0.0.1')
                if response.status_code == 200:
                    accessible_count += 1
                    self.stdout.write(f"  ✓ {plan.reference}: Accessible")
                else:
                    self.stdout.write(self.style.WARNING(
                        f"  ⚠ {plan.reference}: Status {response.status_code}"
                    ))
            except Exception as e:
                self.stdout.write(self.style.ERROR(
                    f"  ❌ {plan.reference}: Error - {e}"
                ))
        
        self.stdout.write(f"\n  Tested {len(sample_plans)} sample plans, {accessible_count} accessible")
        
        # Check for common visibility issues
        self.stdout.write(f"\n🔍 Common Visibility Issues Check:")
        
        # Check for unpublished plans that admin might expect to see
        unpublished = Plan.objects.unpublished().count()
        if unpublished > 0:
            self.stdout.write(self.style.WARNING(
                f"  ⚠ {unpublished} unpublished plan(s) hidden from public"
            ))
            self.stdout.write("    Action: Publish plans in admin to make them visible")
        
        # Check for deleted plans
        deleted = Plan.objects.filter(is_deleted=True).count()
        if deleted > 0:
            self.stdout.write(self.style.WARNING(
                f"  ⚠ {deleted} soft-deleted plan(s) hidden from public"
            ))
            self.stdout.write("    Action: Restore plans in admin if needed")
        
        # Check for plans without images
        no_images = visible_plans.filter(images__isnull=True).distinct().count()
        if no_images > 0:
            self.stdout.write(self.style.WARNING(
                f"  ⚠ {no_images} visible plan(s) have no images"
            ))
            self.stdout.write("    Recommendation: Add images for better user experience")
        
        # Final summary
        self.stdout.write(self.style.HTTP_INFO('\n' + '=' * 70))
        
        if visible_plans.count() > 0:
            self.stdout.write(self.style.SUCCESS(
                f"\n✅ Frontend visibility check complete"
            ))
            self.stdout.write(f"   {total_visible} plan(s) should be visible to users")
        else:
            self.stdout.write(self.style.WARNING(
                f"\n⚠ No visible plans found - users will see empty listing"
            ))
        
        self.stdout.write(self.style.HTTP_INFO('=' * 70 + '\n'))
