# Plan Data Safety & Integrity Architecture

## 🛡️ Core Safety Principle
**Plans are permanent business-critical assets. They must NEVER be accidentally lost, hidden, or deleted.**

---

## 🔒 Multi-Layer Protection System

### Layer 1: Database-Level Protection
- **PROTECT Constraint**: `Order.plan` uses `on_delete=models.PROTECT`
  - Plans with orders **cannot** be deleted at database level
  - Django will raise `ProtectedError` if deletion is attempted
  - Ensures referential integrity is maintained

### Layer 2: Soft Delete (Default Behavior)
- All plan deletions are **soft deletes** by default
- Plan record remains in database with `is_deleted=True`
- Files are preserved on disk
- Visible only to admins; hidden from public frontend
- Can be restored at any time with full history

### Layer 3: Hard Delete Restrictions
Hard deletion is **disabled by default** and requires:
1. ✅ Explicit admin confirmation via dedicated action
2. ✅ Plan must be soft-deleted first
3. ✅ **Zero** orders (paid or unpaid) linked to plan
4. ✅ Superuser-only permission
5. ✅ Warning dialog with red alerts

### Layer 4: Audit Logging
- Every plan action is logged in `PlanAuditLog`
- Tracks: created, updated, published, unpublished, soft deleted, restored, hard deleted
- Records: timestamp, admin user, notes, metadata
- Immutable audit trail for compliance

### Layer 5: Slug History
- All previous slugs stored in `PlanSlugHistory`
- Enables safe redirects when plan URLs change
- Prevents broken links and 404 errors

---

## 📋 Plan Lifecycle States

| State | Visible to Public | Visible to Admin | Can Edit | Can Restore | Can Hard Delete |
|-------|------------------|------------------|----------|-------------|-----------------|
| **Unpublished** | ❌ No | ✅ Yes | ✅ Yes | N/A | ⚠️ Yes (if no orders) |
| **Published** | ✅ Yes | ✅ Yes | ✅ Yes | N/A | ⚠️ Yes (if no orders) |
| **Soft Deleted** | ❌ No | ✅ Yes | ⚠️ Limited | ✅ Yes | ⚠️ Yes (if no orders) |
| **Hard Deleted** | ❌ No | ❌ No | ❌ No | ❌ No | N/A (Permanent) |

---

## 🔧 Admin Operations & Safeguards

### Safe Operations (Non-Destructive)
- ✅ **Publish**: Makes plan visible to public
- ✅ **Unpublish**: Hides plan from public (still in database)
- ✅ **Edit**: Modify plan details, files, content
- ✅ **Soft Delete**: Archive plan (reversible)
- ✅ **Restore**: Recover soft-deleted plan

### Destructive Operations (Restricted)
- ⚠️ **Hard Delete**: Permanent removal
  - Requires explicit confirmation dialog
  - Blocked if any orders exist
  - Must be soft-deleted first
  - Only superusers can trigger

### Bulk Actions Protection
- ❌ Django's default "Delete selected" → **overridden to soft delete**
- ⚠️ Custom "Hard delete permanently" → requires confirmation page
- ✅ Bulk publish/unpublish/soft delete → safe operations
- 🔐 All bulk actions require superuser permission

---

## 📁 File Management Safety

### File Upload Rules
- Only **PDF** files accepted for plans
- Images: PNG, JPG, JPEG accepted
- File size limits enforced
- Virus scanning recommended (external service)

### File Replacement
- Old files are automatically deleted when replaced
- Uses `_cleanup_replaced_files()` method
- Prevents orphaned files accumulating
- Only happens on successful save

### File Deletion
- Files deleted only when:
  1. Plan is hard deleted (permanent)
  2. File is replaced with new version
- Soft delete **preserves** files
- Admin can download files from deleted plans

---

## 🚀 Deployment Safety Checklist

### Before Deployment
```bash
# 1. Run integrity verification
python manage.py verify_plan_integrity --verbose

# 2. Create database backup
python manage.py dumpdata plans orders > backup_plans.json

# 3. Check migration safety
python manage.py makemigrations --dry-run --verbosity 3
python manage.py migrate --plan

# 4. Verify plan count
python manage.py shell -c "from apps.plans.models import Plan; print(f'Total plans: {Plan.objects.count()}')"
```

### After Deployment
```bash
# 1. Verify plan count matches pre-deployment
python manage.py verify_plan_integrity --verbose

# 2. Check for orphaned plans
python manage.py verify_plan_integrity --fix-issues

# 3. Verify frontend visibility
curl http://yoursite.com/plans/ | grep "plan"

# 4. Test admin access
# Login and check plan list loads correctly
```

### Migration Safety Rules
- ✅ `makemigrations` reviewed before commit
- ✅ No `RemoveField` operations on critical fields
- ✅ No `DeleteModel` operations on Plan model
- ✅ Test migrations on staging first
- ✅ Backup before production deployment

---

## 🎯 Data Integrity Guarantees

### What Can NEVER Happen
1. ❌ Plans disappearing without admin action
2. ❌ Plans deleted when orders exist
3. ❌ Cascading deletion of plans
4. ❌ Accidental bulk hard delete
5. ❌ Loss of audit trail
6. ❌ Broken order references

### What CAN Happen (By Design)
1. ✅ Plans soft deleted (reversible)
2. ✅ Plans unpublished (hidden from public)
3. ✅ Files replaced (old version deleted)
4. ✅ Slug changes (old slug saved in history)
5. ✅ Admin editing plan content

---

## 📊 Monitoring & Alerts

### Integrity Verification Command
```bash
# Daily scheduled check (recommended)
python manage.py verify_plan_integrity

# With auto-fix (use cautiously)
python manage.py verify_plan_integrity --fix-issues

# Verbose output for debugging
python manage.py verify_plan_integrity --verbose
```

### Checks Performed
1. ✅ Unique reference codes
2. ✅ Unique slugs
3. ✅ No duplicate plans
4. ✅ Plans with orders are protected
5. ✅ No conflicting states (deleted + published)
6. ✅ Orphaned plans detection
7. ✅ Missing files detection
8. ✅ Audit log verification

### Recommended Monitoring
- Schedule daily integrity checks via cron/task scheduler
- Alert on plan count drops
- Monitor soft-deleted plan accumulation
- Review audit logs weekly
- Track hard deletion requests (should be rare)

---

## 🔐 Permission Model

| Role | View Plans | Edit Plans | Soft Delete | Hard Delete | Restore |
|------|-----------|-----------|-------------|-------------|---------|
| **Anonymous** | Published only | ❌ No | ❌ No | ❌ No | ❌ No |
| **Authenticated** | Published only | ❌ No | ❌ No | ❌ No | ❌ No |
| **Staff** | All plans | ❌ No | ❌ No | ❌ No | ❌ No |
| **Superuser** | All plans | ✅ Yes | ✅ Yes | ⚠️ Yes (with checks) | ✅ Yes |

**Note**: Only superusers can access the Plan admin interface.

---

## 🆘 Recovery Procedures

### Scenario 1: Accidentally Soft Deleted Plan
```python
# Via Django shell
from apps.plans.models import Plan
plan = Plan.objects.get(reference='PL-2024-001')
plan.restore(user=request.user)
```

### Scenario 2: Need to Restore from Backup
```bash
# Load plans from JSON backup
python manage.py loaddata backup_plans.json

# Verify restoration
python manage.py verify_plan_integrity --verbose
```

### Scenario 3: Plan Count Mismatch After Deployment
```bash
# Check what happened
python manage.py verify_plan_integrity --verbose

# Auto-fix detected issues
python manage.py verify_plan_integrity --fix-issues
```

### Scenario 4: Accidentally Hard Deleted Plan (UNRECOVERABLE)
```plaintext
⚠️ CRITICAL: Hard deletion is PERMANENT
- Plan record permanently removed from database
- All files permanently deleted from disk
- Cannot be restored via Django

Recovery options:
1. Restore from database backup (last resort)
2. Re-create plan manually (if details known)
3. Contact database administrator for transaction log recovery

Prevention:
- Always soft delete first
- Verify no orders exist
- Double-check confirmation dialog
- Use backups before risky operations
```

---

## ✅ Best Practices

### For Developers
1. **Never** use `Plan.objects.all().delete()` in code
2. Always use `plan.soft_delete()` for deletions
3. Test migrations on staging database first
4. Review all `on_delete` constraints carefully
5. Use integrity check command after code changes

### For Admins
1. **Always** soft delete first, review for 30 days
2. Only hard delete plans with zero orders
3. Download files before hard deletion
4. Check audit log before deletion
5. Run integrity check after bulk operations

### For Deployment
1. Backup database before deployment
2. Run integrity check before/after
3. Verify plan count consistency
4. Test frontend visibility post-deployment
5. Monitor error logs for 24 hours

---

## 📞 Support & Troubleshooting

### Common Issues

**Issue**: "Cannot delete plan - protected by orders"
- **Cause**: Plan has associated orders
- **Solution**: This is by design. Orders must reference valid plans.
- **Action**: Soft delete instead, or remove orders first (not recommended)

**Issue**: "Plan showing as both deleted and published"
- **Cause**: Data inconsistency
- **Solution**: Run `python manage.py verify_plan_integrity --fix-issues`

**Issue**: "Plan count dropped after deployment"
- **Cause**: Migration may have removed data
- **Solution**: Restore from backup, investigate migration

**Issue**: "Files missing but plan exists"
- **Cause**: Files deleted outside Django or server migration
- **Solution**: Re-upload files via admin interface

---

## 🎓 Training Checklist for New Admins

- [ ] Understand soft delete vs hard delete
- [ ] Know how to publish/unpublish plans
- [ ] Practice restoring soft-deleted plans
- [ ] Learn to run integrity checks
- [ ] Understand order protection mechanism
- [ ] Know backup/restore procedures
- [ ] Reviewed audit log interpretation
- [ ] Completed test delete on staging environment

---

## 📅 Maintenance Schedule

| Task | Frequency | Command/Action |
|------|-----------|----------------|
| Integrity Check | Daily | `verify_plan_integrity` |
| Database Backup | Daily | Automated backup script |
| Audit Log Review | Weekly | Admin panel review |
| Soft Delete Cleanup | Monthly | Review deleted plans, hard delete if appropriate |
| Full System Test | Before each deployment | Full checklist |

---

## 🏆 Success Metrics

- **Zero** accidental plan deletions since deployment
- **100%** of orders reference valid plans
- **< 1 minute** recovery time for soft-deleted plans
- **100%** audit trail coverage
- **Zero** data loss incidents

---

**Last Updated**: January 2, 2026  
**Version**: 1.0  
**Maintained By**: Senior Django Data Integrity & Safety Architect
