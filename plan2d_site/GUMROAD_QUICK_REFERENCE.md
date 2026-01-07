# Gumroad Payment - Quick Reference Card

## Quick Setup (3 Steps)

1. **Create Gumroad Product**
   - Upload your dimensioned plan PDF to Gumroad
   - Set price and publish
   - Copy checkout URL

2. **Add to Django Admin**
   - Admin → Plans → Edit Plan
   - Paste URL in "Gumroad URL" field
   - Check "Enable Gumroad Payment"
   - Save

3. **Verify**
   - Visit plan page
   - Confirm "Buy Securely via Gumroad" button appears
   - Test click (don't complete purchase)

## Payment Status Quick Guide

| Indicator | Meaning | Action Needed |
|-----------|---------|---------------|
| ✓ **Gumroad Payment Active** (Green) | Working correctly | None |
| ⏸ **Gumroad Payment Disabled** (Yellow) | URL saved, button hidden | Enable if desired |
| ⚠ **Warning: No Gumroad URL** (Red) | Missing URL | Add URL or disable |
| — **No Gumroad Payment** (Gray) | Using default checkout | Add URL to use Gumroad |

## Valid URL Formats

```
✓ https://gumroad.com/l/product-code
✓ https://yourname.gumroad.com/l/product-code
✗ http://gumroad.com/l/product (no HTTP)
✗ Missing https://
```

## Common Admin Actions

### Enable Gumroad for a Plan
1. Open plan in admin
2. Enter Gumroad URL
3. Check "Enable Gumroad Payment"
4. Save

### Temporarily Disable
1. Open plan in admin
2. Uncheck "Enable Gumroad Payment"
3. Save
(URL is preserved for later)

### Update Product Link
1. Open plan in admin
2. Replace old URL with new URL
3. Save

### Remove Gumroad
1. Open plan in admin
2. Clear "Gumroad URL" field
3. Save
(Falls back to default checkout)

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Button not showing | Check URL filled and payment enabled |
| Invalid URL error | Ensure starts with `https://gumroad.com/` |
| Wrong product opens | Verify correct URL copied from Gumroad |
| Payments not received | Check Gumroad dashboard (not Django issue) |

## Admin Panel Location

```
Django Admin → Plans → [Select Plan]
↓
Payment Configuration Section
  - Price
  - Gumroad URL ← Paste here
  - Enable Gumroad Payment ← Check this
  - Payment Status ← Shows status
```

## Frontend Display Logic

```
IF Gumroad URL exists AND payment enabled:
  → Show: "Buy Securely via Gumroad" button
  → Redirects to: Your Gumroad checkout

IF Gumroad disabled OR no URL:
  → Show: "Get Dimensioned Plan" button
  → Redirects to: Default checkout page
```

## Safety Features

- ✓ URL validation (must be real Gumroad URL)
- ✓ HTTPS enforced
- ✓ Admin-only editing
- ✓ Changes logged in audit trail
- ✓ No payment data stored in Django
- ✓ Toggle without losing URL

## Best Practices Checklist

- [ ] Price in Django matches Gumroad price
- [ ] Product name in Gumroad matches plan title
- [ ] Tested full purchase flow
- [ ] PDF delivery verified in Gumroad
- [ ] Payment status shows green checkmark
- [ ] Customer-facing page reviewed

## Need Help?

- **Full Documentation**: See GUMROAD_ADMIN_GUIDE.md
- **Technical Issues**: Contact system administrator
- **Payment Issues**: Check Gumroad dashboard first

---

**Pro Tip**: Keep a spreadsheet mapping plan references to Gumroad URLs for easy tracking!
