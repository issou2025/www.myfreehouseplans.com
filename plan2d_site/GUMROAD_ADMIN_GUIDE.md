# Gumroad Payment Integration - Admin Guide

## Overview

The Gumroad payment system allows you to link each house plan to a Gumroad product checkout page. This gives you full control over payment links without requiring code changes or redeployment.

## How It Works

### Admin Control
- **Centralized Management**: All Gumroad links are managed through the Django admin panel
- **Per-Plan Configuration**: Each plan can have its own Gumroad product link
- **Toggle Control**: Enable or disable Gumroad payment for any plan without deleting the URL
- **No Code Changes Needed**: Update payment links instantly without developer intervention

### Frontend Behavior
When a customer views a plan:
- **If Gumroad is configured**: Shows "Buy Securely via Gumroad" button
- **If Gumroad is disabled**: Shows default checkout button
- **Secure Redirect**: Clicking the Gumroad button redirects to your Gumroad checkout page
- **Professional Trust Signals**: Clear messaging that payment is processed securely by Gumroad

## Setting Up Gumroad Payment

### Step 1: Create Your Gumroad Product

1. Go to [Gumroad.com](https://gumroad.com) and sign in
2. Click "Products" → "New Product"
3. Upload your dimensioned plan PDF
4. Set the price (should match your plan price)
5. Configure product settings (description, delivery method, etc.)
6. Publish the product
7. Copy the checkout URL (e.g., `https://gumroad.com/l/your-product-code`)

### Step 2: Configure in Django Admin

1. **Navigate to Admin Panel**
   - Go to `/admin/`
   - Click "Plans" under the Plans section

2. **Edit the Plan**
   - Find the plan you want to link
   - Click on it to open the edit form

3. **Locate Payment Configuration Section**
   - Scroll to the "Payment Configuration" fieldset
   - You'll see three fields:
     - **Price**: The display price (should match Gumroad)
     - **Gumroad URL**: Your Gumroad checkout link
     - **Enable Gumroad Payment**: Toggle to enable/disable

4. **Enter Gumroad URL**
   ```
   Example: https://gumroad.com/l/modern-house-plan-001
   ```
   - Must start with `https://gumroad.com/` or `https://*.gumroad.com/`
   - No trailing spaces
   - Copy directly from Gumroad product page

5. **Enable Payment**
   - Check "Enable Gumroad Payment" (checked by default)
   - This makes the Gumroad button appear on the plan page

6. **Check Payment Status**
   - The **Payment Status** indicator shows:
     - ✓ **Gumroad Payment Active** (Green): Ready to accept payments
     - ⏸ **Gumroad Payment Disabled** (Yellow): URL saved but button hidden
     - ⚠ **Warning: No Gumroad URL** (Red): Payment enabled but URL missing
     - — **No Gumroad Payment** (Gray): Using default checkout

7. **Save the Plan**
   - Click "Save" or "Save and continue editing"
   - The plan page will now show the Gumroad buy button

## Admin List View

The plans list view includes a **Gumroad** column showing quick status:

- **✓ Gumroad** (Green): Active and configured correctly
- **⏸ Disabled** (Yellow): URL exists but payment is disabled
- **⚠ No URL** (Red): Payment enabled but URL is missing
- **—** (Gray): Not using Gumroad

## URL Validation

The system validates Gumroad URLs automatically:

### Valid URLs
```
✓ https://gumroad.com/l/product-code
✓ https://gumroad.com/l/product-code/variant
✓ https://yourname.gumroad.com/l/product-code
```

### Invalid URLs
```
✗ http://gumroad.com/l/product  (must use HTTPS)
✗ gumroad.com/l/product         (missing protocol)
✗ https://notgumroad.com/...    (not a Gumroad domain)
```

## Common Workflows

### Scenario 1: Adding Gumroad to an Existing Plan

1. Create product on Gumroad
2. Copy the checkout URL
3. Open plan in Django admin
4. Paste URL in "Gumroad URL" field
5. Ensure "Enable Gumroad Payment" is checked
6. Save

**Result**: Plan page now shows Gumroad buy button

### Scenario 2: Temporarily Disabling Gumroad Payment

1. Open plan in Django admin
2. Uncheck "Enable Gumroad Payment"
3. Save

**Result**: Gumroad button hidden, default checkout shown. URL is preserved for future use.

### Scenario 3: Updating Gumroad Product Link

1. Open plan in Django admin
2. Replace old URL with new URL in "Gumroad URL" field
3. Save

**Result**: Buy button now redirects to new Gumroad product

### Scenario 4: Removing Gumroad Payment

1. Open plan in Django admin
2. Clear the "Gumroad URL" field
3. Save

**Result**: Default checkout system is used

## Error Handling

### Missing URL Warning

**Error Message**: "Payment is enabled but no Gumroad URL is provided"

**Solution**: Either:
- Add a valid Gumroad URL, or
- Uncheck "Enable Gumroad Payment"

### Invalid URL Format

**Error Message**: "Please enter a valid Gumroad URL..."

**Solution**: Ensure URL:
- Starts with `https://`
- Contains `gumroad.com/` in the domain
- Is copied correctly from Gumroad

## Best Practices

### 1. Price Consistency
- Keep Django "Price" field in sync with Gumroad product price
- Customers see the preview price before clicking buy

### 2. Test Before Publishing
- Create a test Gumroad product
- Test the full purchase flow
- Verify PDF delivery works

### 3. Product Organization
- Use clear product names in Gumroad (e.g., "House Plan PL-2024-001")
- Match Gumroad product name to plan title for easy tracking

### 4. URL Management
- Keep a spreadsheet mapping plan references to Gumroad product URLs
- Document any URL changes for audit trail

### 5. Customer Communication
- Ensure plan title and description match Gumroad product
- Clear expectations about what's included in the purchase

## Frontend Customer Experience

### What Customers See

**Plan Detail Page - With Gumroad Enabled:**
```
Build-Ready Plan
✓ All dimensions included
✓ Construction-ready details
✓ No watermarks

[Buy Securely via Gumroad]
$49.99
One-time purchase • Secure checkout
🛡 Payment processed securely by Gumroad
```

**Plan Detail Page - Without Gumroad:**
```
Build-Ready Plan
✓ All dimensions included
✓ Construction-ready details
✓ No watermarks

[Get Dimensioned Plan]
$49.99
One-time purchase
```

## Technical Details

### Database Fields

- `gumroad_url` (URLField): Stores the Gumroad checkout link
- `enable_gumroad_payment` (BooleanField): Toggles payment button display

### Business Logic

```python
# Button displays when:
if plan.gumroad_url AND plan.enable_gumroad_payment:
    show_gumroad_button()
else:
    show_default_checkout_button()
```

### Security Features

- URLs must use HTTPS
- Domain validation prevents phishing
- No user-editable URLs (admin only)
- URL changes tracked in audit log

## Troubleshooting

### Problem: Gumroad button not showing

**Checks:**
1. Is Gumroad URL field filled?
2. Is "Enable Gumroad Payment" checked?
3. Is plan published (not draft)?
4. Clear browser cache and refresh

### Problem: Invalid URL error

**Checks:**
1. URL starts with `https://`
2. URL contains `gumroad.com/`
3. No extra spaces or characters
4. Copied directly from Gumroad

### Problem: Payments not received

**Solution:**
- This is a Gumroad issue, not Django
- Check Gumroad dashboard for payment status
- Verify Gumroad product is published and active
- Contact Gumroad support if needed

## Migration from Other Payment Systems

### From Manual Payment
1. Create Gumroad products for all plans
2. Map each plan to its Gumroad product
3. Update admin with Gumroad URLs
4. Test each plan's buy button

### From Stripe/PayPal
1. Disable old payment integration
2. Set up Gumroad products
3. Update plan Gumroad URLs
4. Redirect old payment pages if needed

## Reporting & Analytics

### Tracking Sales
- View sales in Gumroad dashboard
- Gumroad provides detailed analytics
- Export sales data for accounting

### Identifying Products
- Use consistent naming in Gumroad
- Include plan reference code in product name
- Tag products for easy filtering

## Support & Maintenance

### Regular Tasks
- Review payment status monthly
- Update URLs when changing Gumroad products
- Verify price consistency
- Test buy flow quarterly

### When to Update URLs
- Changing Gumroad product
- Moving to new Gumroad account
- Updating product variants
- Fixing broken links

## FAQ

**Q: Can I use both Gumroad and default checkout?**
A: Yes, but only one shows per plan. Toggle using "Enable Gumroad Payment".

**Q: Do I need coding skills?**
A: No, everything is managed through the admin panel.

**Q: What if Gumroad is down?**
A: Temporarily disable Gumroad payment to show default checkout.

**Q: Can I A/B test payment methods?**
A: Yes, toggle individual plans to compare Gumroad vs default checkout.

**Q: Is payment data stored in Django?**
A: No, Gumroad handles all payment processing and storage.

**Q: Can customers see my Gumroad URL?**
A: Yes, it's visible in the browser when they click the buy button.

## Security Considerations

- **No API Keys**: System uses simple redirects, no API integration
- **No Payment Data**: Django never sees payment information
- **HTTPS Only**: All Gumroad URLs must use secure connections
- **Admin Only**: Only admin users can modify payment links
- **Audit Trail**: All URL changes are logged

## Future Enhancements

Possible future features:
- Bulk URL import/export
- Gumroad API integration for automatic product sync
- Sales analytics in Django admin
- Automated price synchronization
- Webhook for purchase notifications

---

**Last Updated**: January 3, 2026
**Version**: 1.0
**Support**: Contact system administrator for assistance
