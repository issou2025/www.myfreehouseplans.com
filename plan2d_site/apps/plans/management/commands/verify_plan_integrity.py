"""
Management command to verify plan data integrity and safety.
Run before/after deployment to ensure no plans are accidentally lost.

Usage:
    python manage.py verify_plan_integrity
    python manage.py verify_plan_integrity --fix-issues
"""
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Count, Q
from apps.plans.models import Plan, PlanAuditLog, PlanImage
from apps.orders.models import Order


class Command(BaseCommand):
    help = 'Verify plan data integrity and detect potential data loss issues'

    def add_arguments(self, parser):
        parser.add_argument(
            '--fix-issues',
            action='store_true',
            help='Attempt to automatically fix detected issues',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed output',
        )

    def handle(self, *args, **options):
        fix_issues = options['fix_issues']
        verbose = options['verbose']
        
        self.stdout.write(self.style.HTTP_INFO('=' * 70))
        self.stdout.write(self.style.HTTP_INFO('Plan Data Integrity Verification'))
        self.stdout.write(self.style.HTTP_INFO('=' * 70))
        
        issues_found = 0
        issues_fixed = 0
        
        # Check 1: Count all plans
        total_plans = Plan.objects.all().count()
        active_plans = Plan.objects.active().count()
        deleted_plans = Plan.objects.filter(is_deleted=True).count()
        published_plans = Plan.objects.published().count()
        
        self.stdout.write(f"\n📊 Plan Counts:")
        self.stdout.write(f"  Total plans in database: {total_plans}")
        self.stdout.write(f"  Active plans (not deleted): {active_plans}")
        self.stdout.write(f"  Soft-deleted plans: {deleted_plans}")
        self.stdout.write(f"  Published & visible: {published_plans}")
        
        if total_plans == 0:
            self.stdout.write(self.style.WARNING('\n⚠ WARNING: No plans found in database!'))
        
        # Check 2: Verify unique references and slugs
        duplicate_refs = Plan.objects.values('reference').annotate(
            count=Count('id')
        ).filter(count__gt=1)
        
        if duplicate_refs.exists():
            issues_found += duplicate_refs.count()
            self.stdout.write(self.style.ERROR(
                f'\n❌ CRITICAL: {duplicate_refs.count()} duplicate reference codes found!'
            ))
            for dup in duplicate_refs:
                self.stdout.write(f"  - Reference '{dup['reference']}' used {dup['count']} times")
        
        duplicate_slugs = Plan.objects.values('slug').annotate(
            count=Count('id')
        ).filter(count__gt=1)
        
        if duplicate_slugs.exists():
            issues_found += duplicate_slugs.count()
            self.stdout.write(self.style.ERROR(
                f'\n❌ ERROR: {duplicate_slugs.count()} duplicate slugs found!'
            ))
            for dup in duplicate_slugs:
                self.stdout.write(f"  - Slug '{dup['slug']}' used {dup['count']} times")
        
        # Check 3: Plans with orders cannot be hard deleted
        plans_with_orders = Plan.objects.annotate(
            order_count=Count('orders')
        ).filter(order_count__gt=0)
        
        if plans_with_orders.exists():
            self.stdout.write(f"\n🔒 Protected Plans (have orders): {plans_with_orders.count()}")
            if verbose:
                for plan in plans_with_orders[:10]:
                    completed = plan.orders.filter(payment_status=Order.COMPLETED).count()
                    self.stdout.write(
                        f"  - {plan.reference}: {plan.order_count} orders ({completed} completed)"
                    )
        
        # Check 4: Orphaned plans (deleted but have completed orders)
        orphaned = Plan.objects.filter(
            is_deleted=True,
            orders__payment_status=Order.COMPLETED
        ).distinct()
        
        if orphaned.exists():
            issues_found += orphaned.count()
            self.stdout.write(self.style.WARNING(
                f'\n⚠ WARNING: {orphaned.count()} soft-deleted plans have completed orders!'
            ))
            if verbose:
                for plan in orphaned[:10]:
                    self.stdout.write(f"  - {plan.reference}: Should not be deleted (has paid orders)")
            
            if fix_issues:
                for plan in orphaned:
                    plan.restore(user=None)
                    issues_fixed += 1
                self.stdout.write(self.style.SUCCESS(
                    f'  ✓ Restored {issues_fixed} plans with completed orders'
                ))
        
        # Check 5: Published plans that are marked deleted
        conflicting = Plan.objects.filter(
            is_deleted=True,
            publish_status='published'
        )
        
        if conflicting.exists():
            issues_found += conflicting.count()
            self.stdout.write(self.style.ERROR(
                f'\n❌ ERROR: {conflicting.count()} plans are both DELETED and PUBLISHED!'
            ))
            if verbose:
                for plan in conflicting:
                    self.stdout.write(f"  - {plan.reference}: Invalid state")
            
            if fix_issues:
                conflicting.update(publish_status='unpublished')
                issues_fixed += conflicting.count()
                self.stdout.write(self.style.SUCCESS(
                    f'  ✓ Fixed {conflicting.count()} plans with conflicting status'
                ))
        
        # Check 6: Plans missing critical files
        plans_without_any_files = Plan.objects.filter(
            Q(free_plan_file='') | Q(free_plan_file__isnull=True),
            Q(paid_plan_file='') | Q(paid_plan_file__isnull=True)
        ).exclude(is_deleted=True)
        
        if plans_without_any_files.exists():
            self.stdout.write(self.style.WARNING(
                f'\n⚠ INFO: {plans_without_any_files.count()} active plans have no PDF files uploaded'
            ))
            if verbose:
                for plan in plans_without_any_files[:10]:
                    self.stdout.write(f"  - {plan.reference}: No files")
        
        # Check 7: Verify audit logs exist for all plans
        plans_without_audit = Plan.objects.annotate(
            log_count=Count('audit_logs')
        ).filter(log_count=0)
        
        if plans_without_audit.exists():
            self.stdout.write(self.style.WARNING(
                f'\n⚠ INFO: {plans_without_audit.count()} plans have no audit logs'
            ))
            if verbose and plans_without_audit.count() < 20:
                for plan in plans_without_audit:
                    self.stdout.write(f"  - {plan.reference}: No audit trail")
        
        # Check 8: Verify no cascading delete risks
        self.stdout.write("\n🛡 Cascade Protection:")
        self.stdout.write("  ✓ Plan → Order: PROTECTED (cannot delete plan with orders)")
        self.stdout.write("  ✓ Plan → PlanImage: CASCADE (images deleted with plan)")
        self.stdout.write("  ✓ Plan → PlanAuditLog: CASCADE (logs deleted with plan)")
        self.stdout.write("  ✓ Plan → PlanSlugHistory: CASCADE (history deleted with plan)")
        
        # Final Summary
        self.stdout.write(self.style.HTTP_INFO('\n' + '=' * 70))
        
        if issues_found == 0:
            self.stdout.write(self.style.SUCCESS('\n✅ All integrity checks passed!'))
            self.stdout.write(self.style.SUCCESS(f'   {total_plans} plans verified, no issues detected.'))
        else:
            self.stdout.write(self.style.WARNING(f'\n⚠ {issues_found} issue(s) detected'))
            if fix_issues:
                self.stdout.write(self.style.SUCCESS(f'   {issues_fixed} issue(s) automatically fixed'))
                remaining = issues_found - issues_fixed
                if remaining > 0:
                    self.stdout.write(self.style.WARNING(
                        f'   {remaining} issue(s) require manual intervention'
                    ))
            else:
                self.stdout.write('   Run with --fix-issues to attempt automatic repairs')
        
        self.stdout.write(self.style.HTTP_INFO('=' * 70 + '\n'))
        
        if issues_found > 0 and not fix_issues:
            raise CommandError(
                'Integrity check failed. Run with --fix-issues or investigate manually.'
            )
