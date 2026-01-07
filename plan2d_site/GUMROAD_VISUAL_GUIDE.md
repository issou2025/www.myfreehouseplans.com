# Gumroad Integration - Visual Admin Guide

## 🎨 What You'll See in the Admin Panel

### 1. Plans List View

When you navigate to **Admin → Plans**, you'll see a new **Gumroad** column:

```
┌──────────────┬───────────────┬────────┬──────────┬────────────┬──────────┐
│ Reference    │ Title         │ Price  │ Gumroad  │ Status     │ Updated  │
├──────────────┼───────────────┼────────┼──────────┼────────────┼──────────┤
│ PL-2024-001  │ Modern Villa  │ $49.99 │ ✓ Gumroad│ Published  │ 1d ago   │
│ PL-2024-002  │ Cottage Plan  │ $39.99 │ ⏸ Disabled│ Published  │ 2d ago   │
│ PL-2024-003  │ Beach House   │ $59.99 │ ⚠ No URL │ Published  │ 3d ago   │
│ PL-2024-004  │ City Loft     │ $44.99 │ —        │ Unpublished│ 5d ago   │
└──────────────┴───────────────┴────────┴──────────┴────────────┴──────────┘
```

**Status Legend:**
- **✓ Gumroad** (Green) = Ready to accept payments
- **⏸ Disabled** (Yellow) = URL saved but button hidden
- **⚠ No URL** (Red) = Warning - payment enabled but no URL
- **—** (Gray) = Not using Gumroad

---

### 2. Plan Edit Form - Payment Configuration Section

When you edit a plan, scroll to find the **Payment Configuration** section:

```
╔══════════════════════════════════════════════════════════════════╗
║                     PAYMENT CONFIGURATION                        ║
║                                                                  ║
║  Configure Gumroad payment link. Payment button will only       ║
║  appear if Gumroad URL is provided AND payment is enabled.      ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  Price: [$49.99] USD                                            ║
║  Help: Price in USD for the full plan                           ║
║                                                                  ║
║  ─────────────────────────────────────────────────────────────  ║
║                                                                  ║
║  Gumroad URL:                                                   ║
║  [https://gumroad.com/l/your-product                        ]  ║
║  Placeholder: https://gumroad.com/l/your-product               ║
║  Help: Enter the Gumroad checkout URL for this plan.           ║
║        Example: https://gumroad.com/l/your-product-code        ║
║                                                                  ║
║  ─────────────────────────────────────────────────────────────  ║
║                                                                  ║
║  [✓] Enable Gumroad payment                                     ║
║  Help: Enable or disable Gumroad payment for this plan.        ║
║        Payment button will only show if both this is           ║
║        enabled AND Gumroad URL is provided.                    ║
║                                                                  ║
║  ─────────────────────────────────────────────────────────────  ║
║                                                                  ║
║  Payment Status:                                               ║
║  ✓ Gumroad Payment Active                                      ║
║  Button will appear on plan page                               ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
```

---

### 3. Payment Status Indicators

The **Payment Status** field shows different states:

#### State 1: ✅ Active and Working
```
┌────────────────────────────────────────┐
│ ✓ Gumroad Payment Active              │
│ Button will appear on plan page       │
│                                        │
│ [GREEN BACKGROUND]                    │
└────────────────────────────────────────┘
```
**Meaning**: Everything configured correctly, customers will see Gumroad button

---

#### State 2: ⏸️ Disabled (URL Preserved)
```
┌────────────────────────────────────────┐
│ ⏸ Gumroad Payment Disabled            │
│ URL saved but payment button hidden   │
│                                        │
│ [YELLOW BACKGROUND]                   │
└────────────────────────────────────────┘
```
**Meaning**: URL is saved, but button won't show. Can re-enable anytime.

---

#### State 3: ⚠️ Warning - Configuration Issue
```
┌────────────────────────────────────────┐
│ ⚠ Warning: No Gumroad URL              │
│ Payment enabled but URL missing       │
│                                        │
│ [RED BACKGROUND]                      │
└────────────────────────────────────────┘
```
**Meaning**: Payment is enabled but no URL provided. Needs attention!

---

#### State 4: ❌ Not Using Gumroad
```
┌────────────────────────────────────────┐
│ — No Gumroad Payment                   │
│ Using default checkout system         │
│                                        │
│ [GRAY BACKGROUND]                     │
└────────────────────────────────────────┘
```
**Meaning**: Not configured for Gumroad, using standard checkout

---

### 4. Form Validation Examples

#### ✅ Valid URL - Saves Successfully
```
Input: https://gumroad.com/l/modern-villa-2024

Result: ✓ Saved successfully
        Payment status: Active
```

---

#### ❌ Invalid URL - Shows Error
```
Input: http://gumroad.com/l/modern-villa

Error Message:
┌─────────────────────────────────────────────────────────────┐
│ ⚠ Please enter a valid Gumroad URL.                        │
│   URL must start with https://gumroad.com/ or              │
│   https://*.gumroad.com/                                   │
└─────────────────────────────────────────────────────────────┘
```

---

#### ⚠️ Missing URL with Payment Enabled
```
Gumroad URL: [empty]
Enable Gumroad Payment: [✓] Checked

Error Message:
┌─────────────────────────────────────────────────────────────┐
│ ⚠ Payment is enabled but no Gumroad URL is provided.       │
│   Either add a Gumroad URL or disable Gumroad payment.     │
└─────────────────────────────────────────────────────────────┘
```

---

## 🌐 Frontend Customer Experience

### Scenario A: Gumroad Enabled

**Plan Detail Page (Build-Ready Section):**

```
┌─────────────────────────────────────────────────────────────┐
│  Build-Ready                                               │
│  Complete dimensioned set for construction                 │
│                                                            │
│  ✓ All dimensions included                                │
│  ✓ Wall thicknesses specified                             │
│  ✓ Door & window sizes                                    │
│  ✓ Construction-ready details                             │
│  ✓ No watermarks                                          │
│                                                            │
│  ╔════════════════════════════════════════════════════╗   │
│  ║  🔒 Buy Securely via Gumroad                       ║   │
│  ╚════════════════════════════════════════════════════╝   │
│                                                            │
│  $49.99                                                    │
│  One-time purchase • Secure checkout                       │
│  🛡 Payment processed securely by Gumroad                  │
└─────────────────────────────────────────────────────────────┘
```

**Button Style**:
- Primary blue button
- Lock icon for security
- Full width
- Professional appearance

---

### Scenario B: Gumroad Disabled (Default Checkout)

**Plan Detail Page (Build-Ready Section):**

```
┌─────────────────────────────────────────────────────────────┐
│  Build-Ready                                               │
│  Complete dimensioned set for construction                 │
│                                                            │
│  ✓ All dimensions included                                │
│  ✓ Wall thicknesses specified                             │
│  ✓ Door & window sizes                                    │
│  ✓ Construction-ready details                             │
│  ✓ No watermarks                                          │
│                                                            │
│  ╔════════════════════════════════════════════════════╗   │
│  ║  🛒 Get Dimensioned Plan                           ║   │
│  ╚════════════════════════════════════════════════════╝   │
│                                                            │
│  $49.99                                                    │
│  One-time purchase                                         │
└─────────────────────────────────────────────────────────────┘
```

**Button Style**:
- Primary blue button
- Cart icon
- Full width
- Links to internal checkout

---

## 🔄 Common Workflows - Step by Step

### Workflow 1: Adding Gumroad to New Plan

```
Step 1: Create Product in Gumroad
┌────────────────────────────────────┐
│ Gumroad.com → Products → New      │
│ Upload: dimensioned-plan.pdf      │
│ Price: $49.99                     │
│ → Publish                         │
│ → Copy URL                        │
└────────────────────────────────────┘
              ↓
Step 2: Configure in Django
┌────────────────────────────────────┐
│ Admin → Plans → Add Plan          │
│ Fill basic info...                │
│ Scroll to Payment Configuration   │
│ Paste URL in Gumroad URL field    │
│ ✓ Enable Gumroad Payment          │
│ → Save                            │
└────────────────────────────────────┘
              ↓
Step 3: Verify
┌────────────────────────────────────┐
│ Visit plan page                   │
│ See: "Buy Securely via Gumroad"   │
│ Test: Click button                │
│ → Redirects to Gumroad ✓          │
└────────────────────────────────────┘
```

---

### Workflow 2: Temporarily Disabling Gumroad

```
Current State: Gumroad Active
┌────────────────────────────────────┐
│ Gumroad URL: [filled]             │
│ Enable: [✓] Checked               │
│ Status: ✓ Active                  │
└────────────────────────────────────┘
              ↓
Action: Uncheck Enable
┌────────────────────────────────────┐
│ Gumroad URL: [still filled]       │
│ Enable: [ ] Unchecked             │
│ → Save                            │
└────────────────────────────────────┘
              ↓
New State: Disabled (URL Preserved)
┌────────────────────────────────────┐
│ Status: ⏸ Disabled                │
│ Frontend: Shows default button     │
│ URL: Still saved in database      │
│ Can re-enable anytime ✓           │
└────────────────────────────────────┘
```

---

### Workflow 3: Updating Product Link

```
Current: Old Product
┌────────────────────────────────────┐
│ URL: gumroad.com/l/old-product    │
└────────────────────────────────────┘
              ↓
Action: Replace URL
┌────────────────────────────────────┐
│ Clear old URL                     │
│ Paste: gumroad.com/l/new-product  │
│ → Save                            │
└────────────────────────────────────┘
              ↓
Result: Updated Instantly
┌────────────────────────────────────┐
│ Button now links to new product   │
│ No code changes needed ✓          │
│ No deployment needed ✓            │
└────────────────────────────────────┘
```

---

## 📱 Mobile Admin View

The admin panel is responsive:

```
┌─────────────────────┐
│ Payment Config      │
├─────────────────────┤
│ Price:              │
│ [$49.99]           │
│                     │
│ Gumroad URL:        │
│ [https://...]      │
│                     │
│ [✓] Enable Payment  │
│                     │
│ Status:             │
│ ✓ Active           │
│ Button will appear  │
└─────────────────────┘
```

---

## 🎯 Quick Reference: When to Use What

| Scenario | Gumroad URL | Enable Payment | Result |
|----------|-------------|----------------|--------|
| New paid plan | Fill | ✓ Check | Gumroad button shows |
| Temporarily pause | Keep filled | ⬜ Uncheck | Default button shows |
| Switch to default | Clear | Either | Default button shows |
| A/B testing | Fill both | Toggle | Switch between systems |
| Free plan | Leave empty | Either | No paid button |

---

## 🔍 Troubleshooting Visual Guide

### Problem: Button Not Showing

**Check This:**
```
┌─────────────────────────────────────┐
│ 1. Gumroad URL: [Is it filled?]   │
│    ✓ Yes → Continue                │
│    ✗ No → Fill it                  │
│                                    │
│ 2. Enable Payment: [Is it checked?]│
│    ✓ Yes → Continue                │
│    ✗ No → Check it                 │
│                                    │
│ 3. Plan Status: [Is it published?] │
│    ✓ Published → Should work       │
│    ✗ Unpublished → Publish it      │
└─────────────────────────────────────┘
```

---

### Problem: Wrong Product Opens

**Fix This:**
```
Current URL:
┌────────────────────────────────────┐
│ gumroad.com/l/wrong-product       │
└────────────────────────────────────┘
              ↓
Copy Correct URL from Gumroad:
┌────────────────────────────────────┐
│ Go to Gumroad product             │
│ Click "Share" or copy URL         │
│ Verify it's the right product     │
└────────────────────────────────────┘
              ↓
Update in Django:
┌────────────────────────────────────┐
│ Replace with correct URL          │
│ Save                              │
│ Test by clicking button           │
└────────────────────────────────────┘
```

---

## 💡 Pro Tips

### Tip 1: Test Before Publishing
```
1. Create Gumroad product
2. Set price to $0.01 for testing
3. Configure in Django
4. Complete test purchase
5. Verify PDF delivery
6. Update to real price
7. Publish plan
```

### Tip 2: Keep Prices in Sync
```
┌────────────────────────────────────┐
│ Gumroad: $49.99                   │
│ Django Price Field: $49.99         │
│ → Must match for consistency!     │
└────────────────────────────────────┘
```

### Tip 3: URL Organization
Keep a spreadsheet:
```
┌──────────────┬────────────────────────────────┬──────────┐
│ Plan Ref     │ Gumroad URL                    │ Status   │
├──────────────┼────────────────────────────────┼──────────┤
│ PL-2024-001  │ gumroad.com/l/villa-001        │ Active   │
│ PL-2024-002  │ gumroad.com/l/cottage-002      │ Active   │
│ PL-2024-003  │ gumroad.com/l/beach-003        │ Disabled │
└──────────────┴────────────────────────────────┴──────────┘
```

---

## 🎨 Color Guide

**Admin Status Colors:**
- 🟢 Green (`#28a745`) = Active/Success
- 🟡 Yellow (`#ffc107`) = Warning/Disabled
- 🔴 Red (`#dc3545`) = Error/Missing
- ⚪ Gray (`#6c757d`) = Neutral/Inactive

**Frontend Button:**
- 🔵 Blue Primary = Call-to-action button
- Standard Bootstrap primary color
- Professional and trustworthy

---

## 📞 Need More Help?

- **Detailed Guide**: GUMROAD_ADMIN_GUIDE.md
- **Quick Reference**: GUMROAD_QUICK_REFERENCE.md
- **Testing**: GUMROAD_TESTING_GUIDE.md
- **Technical**: GUMROAD_IMPLEMENTATION_SUMMARY.md

---

**Visual Guide Version**: 1.0  
**Last Updated**: January 3, 2026  
**Designed for**: Non-technical admin users
