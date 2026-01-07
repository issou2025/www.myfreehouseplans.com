# Gumroad Payment Integration - Testing Guide

## Pre-Test Checklist

- [x] Migration applied successfully (`0005_add_gumroad_payment_fields`)
- [x] Server running without errors
- [x] Admin panel accessible
- [x] No Python syntax errors

## Test Plan

### Test 1: Admin Panel Access
**Objective**: Verify new fields appear in admin

**Steps**:
1. Navigate to `/admin/`
2. Go to Plans section
3. Click on any existing plan or "Add plan"
4. Scroll to "Payment Configuration" section

**Expected Results**:
- "Payment Configuration" fieldset is visible
- Fields present:
  - Price
  - Gumroad URL (text input with placeholder)
  - Enable Gumroad Payment (checkbox, checked by default)
  - Payment Status (read-only display)

**Status**: ⬜ Not Tested | ✓ Pass | ✗ Fail

---

### Test 2: URL Validation - Valid URLs
**Objective**: Confirm valid Gumroad URLs are accepted

**Test Cases**:
1. `https://gumroad.com/l/test-product`
2. `https://yourname.gumroad.com/l/test-product`
3. `https://gumroad.com/l/test-product/variant`

**Steps**:
1. Edit a plan
2. Enter each URL in "Gumroad URL" field
3. Save

**Expected Results**:
- All URLs save successfully
- No validation errors
- Payment status shows green "✓ Gumroad Payment Active"

**Status**: ⬜ Not Tested | ✓ Pass | ✗ Fail

---

### Test 3: URL Validation - Invalid URLs
**Objective**: Confirm invalid URLs are rejected

**Test Cases**:
1. `http://gumroad.com/l/test` (HTTP instead of HTTPS)
2. `gumroad.com/l/test` (no protocol)
3. `https://notgumroad.com/l/test` (wrong domain)

**Steps**:
1. Edit a plan
2. Enter each invalid URL
3. Attempt to save

**Expected Results**:
- Validation error displayed
- Error message: "Please enter a valid Gumroad URL..."
- Plan not saved

**Status**: ⬜ Not Tested | ✓ Pass | ✗ Fail

---

### Test 4: Payment Status Display
**Objective**: Verify payment status indicator works correctly

**Test Cases**:

| Gumroad URL | Enable Payment | Expected Status |
|-------------|----------------|-----------------|
| Filled | Checked | ✓ Gumroad Payment Active (Green) |
| Filled | Unchecked | ⏸ Gumroad Payment Disabled (Yellow) |
| Empty | Checked | ⚠ Warning: No Gumroad URL (Red) |
| Empty | Unchecked | — No Gumroad Payment (Gray) |

**Steps**:
1. Edit a plan
2. Set URL and checkbox as per each test case
3. Save and observe "Payment Status" field

**Expected Results**:
- Correct status icon and color for each combination
- Helpful description text below status

**Status**: ⬜ Not Tested | ✓ Pass | ✗ Fail

---

### Test 5: Admin List View
**Objective**: Verify Gumroad status column in plan list

**Steps**:
1. Create/edit multiple plans with different Gumroad configurations:
   - Plan A: URL + enabled
   - Plan B: URL + disabled
   - Plan C: No URL + enabled
   - Plan D: No URL + disabled
2. Go to Plans list view
3. Check "Gumroad" column

**Expected Results**:
- Column header shows "Gumroad"
- Plan A: "✓ Gumroad" (green)
- Plan B: "⏸ Disabled" (yellow)
- Plan C: "⚠ No URL" (red)
- Plan D: "—" (gray)

**Status**: ⬜ Not Tested | ✓ Pass | ✗ Fail

---

### Test 6: Frontend Display - Gumroad Enabled
**Objective**: Verify Gumroad button appears on plan page

**Setup**:
1. Edit a plan
2. Add Gumroad URL: `https://gumroad.com/l/test-product`
3. Check "Enable Gumroad Payment"
4. Save

**Steps**:
1. Visit plan detail page
2. Scroll to "Build-Ready" plan version section

**Expected Results**:
- Button text: "Buy Securely via Gumroad" (with lock icon)
- Price displayed below button
- Text: "One-time purchase • Secure checkout"
- Trust indicator: "🛡 Payment processed securely by Gumroad"
- Button links to Gumroad URL

**Status**: ⬜ Not Tested | ✓ Pass | ✗ Fail

---

### Test 7: Frontend Display - Gumroad Disabled
**Objective**: Verify default button shows when Gumroad disabled

**Setup**:
1. Edit a plan
2. Clear Gumroad URL OR uncheck "Enable Gumroad Payment"
3. Save

**Steps**:
1. Visit plan detail page
2. Scroll to "Build-Ready" plan version section

**Expected Results**:
- Button text: "Get Dimensioned Plan" (with cart icon)
- Price displayed below button
- Text: "One-time purchase" (no Gumroad mention)
- No trust indicator
- Button links to default checkout: `/orders/checkout/{slug}`

**Status**: ⬜ Not Tested | ✓ Pass | ✗ Fail

---

### Test 8: Form Validation Warning
**Objective**: Verify warning when payment enabled but URL missing

**Steps**:
1. Edit a plan
2. Clear "Gumroad URL" field
3. Check "Enable Gumroad Payment"
4. Attempt to save

**Expected Results**:
- Validation error on "Enable Gumroad Payment" field
- Error message: "Payment is enabled but no Gumroad URL is provided..."
- Suggests adding URL or disabling payment
- Plan not saved

**Status**: ⬜ Not Tested | ✓ Pass | ✗ Fail

---

### Test 9: URL Update
**Objective**: Verify URL can be updated without issues

**Steps**:
1. Edit a plan with existing Gumroad URL
2. Change URL to different valid URL
3. Save
4. Visit plan page and test button

**Expected Results**:
- New URL saves successfully
- Payment status remains green
- Button on plan page redirects to new URL
- No orphaned data

**Status**: ⬜ Not Tested | ✓ Pass | ✗ Fail

---

### Test 10: Toggle Payment On/Off
**Objective**: Verify toggle preserves URL

**Steps**:
1. Edit a plan with Gumroad URL
2. Uncheck "Enable Gumroad Payment"
3. Save and verify default button shows
4. Re-edit plan
5. Check "Enable Gumroad Payment"
6. Save and verify Gumroad button shows

**Expected Results**:
- URL preserved when disabled
- Frontend correctly shows/hides Gumroad button
- No data loss
- Status indicators update correctly

**Status**: ⬜ Not Tested | ✓ Pass | ✗ Fail

---

### Test 11: Multiple Plans
**Objective**: Verify each plan can have different Gumroad config

**Setup**:
1. Plan 1: Gumroad URL A
2. Plan 2: Gumroad URL B
3. Plan 3: No Gumroad

**Steps**:
1. Configure three plans as above
2. Visit each plan page
3. Click buy buttons

**Expected Results**:
- Plan 1 redirects to Gumroad URL A
- Plan 2 redirects to Gumroad URL B
- Plan 3 uses default checkout
- No cross-contamination

**Status**: ⬜ Not Tested | ✓ Pass | ✗ Fail

---

### Test 12: Database Persistence
**Objective**: Verify data persists across server restarts

**Steps**:
1. Configure plan with Gumroad URL
2. Save
3. Restart Django server
4. Check plan in admin
5. Check plan page

**Expected Results**:
- URL still present after restart
- Payment status correct
- Frontend button works

**Status**: ⬜ Not Tested | ✓ Pass | ✗ Fail

---

## Edge Cases to Test

### Edge Case 1: Very Long URLs
**Test**: Enter URL with 400+ characters
**Expected**: Should save (URLField max_length=500)

### Edge Case 2: URL with Special Characters
**Test**: `https://gumroad.com/l/test-prod_v2?wanted=true`
**Expected**: Should save and work correctly

### Edge Case 3: Whitespace
**Test**: Enter URL with leading/trailing spaces
**Expected**: Spaces trimmed automatically

### Edge Case 4: Plan Without Price
**Test**: Plan with price=0 and Gumroad URL
**Expected**: Button still appears (Gumroad handles pricing)

---

## Regression Tests

### Existing Functionality
- [ ] Free plan download still works
- [ ] Default checkout still works (when Gumroad disabled)
- [ ] Plan publishing/unpublishing unaffected
- [ ] Plan deletion works normally
- [ ] Other admin actions work
- [ ] SEO fields unaffected
- [ ] Image uploads work

---

## Performance Tests

### Load Tests
- [ ] Admin page loads in < 2 seconds
- [ ] Plan detail page loads in < 2 seconds
- [ ] No N+1 query issues
- [ ] Plan list with 100+ plans loads reasonably

---

## Browser Compatibility

Test frontend on:
- [ ] Chrome/Edge (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Mobile Chrome
- [ ] Mobile Safari

**Focus**: Button appearance, link functionality, responsive design

---

## Security Tests

### Access Control
- [ ] Only admin users can edit Gumroad URLs
- [ ] Non-admin cannot access admin panel
- [ ] URL validation prevents XSS

### URL Security
- [ ] HTTPS enforced (HTTP rejected)
- [ ] Only Gumroad domains accepted
- [ ] No JavaScript injection possible

---

## User Acceptance Criteria

**Admin Perspective**:
- [x] Can add Gumroad URL without technical knowledge
- [x] Clear visual feedback on payment status
- [x] Can enable/disable payment without losing URL
- [x] Validation errors are clear and actionable
- [x] No code changes or deployment needed

**Customer Perspective**:
- [ ] Clear indication of payment method
- [ ] Professional and trustworthy button design
- [ ] Smooth redirect to Gumroad
- [ ] Consistent experience across plans

---

## Known Limitations

1. **No Gumroad API Integration**: System uses simple redirects (by design)
2. **No Payment Tracking**: Django doesn't track Gumroad sales (by design)
3. **Manual URL Entry**: URLs must be entered manually (future: bulk import)
4. **Price Sync**: Admin must manually keep prices in sync with Gumroad

---

## Test Results Summary

**Date Tested**: _______________
**Tested By**: _______________
**Environment**: Development / Staging / Production

**Overall Status**: ⬜ All Pass | ⬜ Some Failures | ⬜ Not Tested

**Critical Issues Found**: 
- None

**Minor Issues Found**:
- None

**Recommended Actions**:
- [ ] Deploy to production
- [ ] Create admin training documentation
- [ ] Set up Gumroad products
- [ ] Test with real Gumroad account

---

## Post-Deployment Checklist

After deploying to production:
- [ ] Verify migration ran successfully
- [ ] Test one real Gumroad purchase end-to-end
- [ ] Monitor error logs for 24 hours
- [ ] Verify analytics tracking (if configured)
- [ ] Document any production-specific configurations
- [ ] Train admin users on new features

---

**Testing Notes**: 
_Use this section for additional observations or issues discovered during testing_

---

**Version**: 1.0  
**Last Updated**: January 3, 2026
