"""
Management command to bulk-publish all unpublished plans.
Useful for migrating existing plans to the new publish_status system.
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from apps.plans.models import Plan, PlanPublishStatus
import logging

logger = logging.getLogger('plans')


class Command(BaseCommand):
    help = 'Publish all unpublished plans (for migration purposes)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be published without making changes',
        )
        parser.add_argument(
            '--reference',
            type=str,
            help='Publish only a specific plan by reference',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        reference = options.get('reference')

        self.stdout.write("=" * 70)
        self.stdout.write(self.style.HTTP_INFO("Plan Publishing Utility"))
        self.stdout.write("=" * 70)
        self.stdout.write()

        # Get unpublished or draft plans
        queryset = Plan.objects.filter(
            publish_status__in=[PlanPublishStatus.UNPUBLISHED, PlanPublishStatus.DRAFT],
            is_deleted=False
        )
        
        if reference:
            queryset = queryset.filter(reference=reference)
            if not queryset.exists():
                self.stdout.write(self.style.ERROR(f"✗ No plan found with reference: {reference}"))
                return

        unpublished_count = queryset.count()

        if unpublished_count == 0:
            self.stdout.write(self.style.SUCCESS("✓ All plans are already published!"))
            return

        self.stdout.write(f"📊 Found {unpublished_count} unpublished plan(s):")
        self.stdout.write()

        for plan in queryset:
            status_info = []
            if not plan.images.exists():
                status_info.append("⚠ No images")
            if not plan.category:
                status_info.append("⚠ No category")
            
            status_str = f" ({', '.join(status_info)})" if status_info else " ✓ Ready"
            self.stdout.write(f"  - {plan.reference}: {plan.title}{status_str}")

        self.stdout.write()

        if dry_run:
            self.stdout.write(self.style.WARNING("🔍 DRY RUN - No changes will be made"))
            self.stdout.write()
            self.stdout.write("To actually publish these plans, run without --dry-run flag:")
            self.stdout.write(f"  python manage.py publish_all_plans")
            return

        # Confirm action
        if unpublished_count > 5:
            confirm = input(f"\n⚠ About to publish {unpublished_count} plans. Continue? [y/N]: ")
            if confirm.lower() != 'y':
                self.stdout.write(self.style.WARNING("Cancelled by user"))
                return

        # Publish all plans
        published_count = 0
        errors = []

        with transaction.atomic():
            for plan in queryset:
                try:
                    plan.publish()
                    published_count += 1
                    logger.info(f"Published plan: {plan.reference}")
                except Exception as e:
                    error_msg = f"Failed to publish {plan.reference}: {str(e)}"
                    errors.append(error_msg)
                    logger.error(error_msg)

        self.stdout.write()
        self.stdout.write("=" * 70)
        self.stdout.write(self.style.SUCCESS(f"✓ Published {published_count} plan(s)"))
        
        if errors:
            self.stdout.write(self.style.ERROR(f"✗ Failed to publish {len(errors)} plan(s):"))
            for error in errors:
                self.stdout.write(f"  - {error}")
        
        self.stdout.write("=" * 70)
        self.stdout.write()

        # Show final status
        total_visible = Plan.objects.visible().count()
        total_published = Plan.objects.published().count()
        total_all = Plan.objects.count()

        self.stdout.write(self.style.HTTP_INFO("📊 Current Status:"))
        self.stdout.write(f"  Total plans: {total_all}")
        self.stdout.write(f"  Published: {total_published}")
        self.stdout.write(f"  Visible (published + not deleted): {total_visible}")
        self.stdout.write()
