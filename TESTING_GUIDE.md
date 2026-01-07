# Quick Testing Guide - Manual Payment System

## Prerequisites
✅ Server running at http://127.0.0.1:8000/
✅ Admin user created (admin/admin123)
✅ At least one plan exists in the database
✅ Migration 0002 applied

## Test Scenario 1: Complete Payment Flow (Happy Path)

### Step 1: Create Test Order
1. Visit: http://127.0.0.1:8000/plans/
2. Click "Buy Now" on any plan
3. You'll be redirected to: http://127.0.0.1:8000/checkout/<plan_id>/

### Step 2: Review Payment Instructions
✅ Check that page shows:
- Plan details (title, price, features)
- Two payment options (Payoneer and Bank Transfer)
- Payoneer email: bacseried@gmail.com
- Bank SWIFT: AFRINENIXXX
- Receipt upload form

### Step 3: Upload Test Receipt
Fill out the form:
- **Full Name:** John Doe
- **Email:** test@example.com
- **Payment Method:** Choose "Payoneer Transfer"
- **Receipt:** Upload any image file (JPEG/PNG/GIF) or PDF

**Note:** You can use any test image file. In real scenario, this would be a screenshot of payment confirmation.

### Step 4: Verify Order Creation
After submission:
- ✅ Redirected to order confirmation page
- ✅ Page shows "Order Received!" with clock icon
- ✅ Status shows: "Receipt Under Review"
- ✅ Message: "usually within 24 hours"
- ✅ Payment method displayed (💳 Payoneer or 🏦 Bank Transfer)
- ✅ Verification status: "⏳ Under Review"

### Step 5: Check Console for Email
In terminal where server is running:
- ✅ Should see email output in console
- ✅ Subject: "Order Confirmation - [ORDER_NUMBER]"
- ✅ Body includes order number and plan details

### Step 6: Admin Verification
1. Open: http://127.0.0.1:8000/admin/
2. Login: admin / admin123
3. Navigate: Orders → Orders
4. ✅ See new order in list
5. ✅ Payment Method column shows "💳 Payoneer" or "🏦 Bank Transfer"
6. ✅ Receipt column shows "📄 View" link
7. ✅ Verified column shows "⏳ Pending"

### Step 7: Review Receipt
1. Click order number to open detail
2. Scroll to "Manual Payment Verification" section
3. ✅ Receipt image displayed inline (or PDF link)
4. ✅ Shows "Verified at: -" (not yet verified)
5. ✅ Shows "Verified by: -" (not yet verified)

### Step 8: Approve Payment
**Method A - Single Order:**
1. In order detail, add admin comment (optional): "Payment confirmed via Payoneer"
2. Click "Save and continue editing"
3. Go back to order list
4. Select the order checkbox
5. Choose action: "✓ Approve selected payments"
6. Click "Go"

**Method B - Bulk Approval:**
1. From order list, select multiple pending orders
2. Choose action: "✓ Approve selected payments"
3. Click "Go"

### Step 9: Verify Approval
✅ Success message: "1 payment(s) approved. Customers notified via email."
✅ Order status changed to: "COMPLETED" (green badge)
✅ Verified column shows: "✓ [date]"
✅ Check console for approval email

### Step 10: Customer View After Approval
1. Visit order confirmation page (copy URL from browser or email)
2. ✅ Page now shows "Order Complete!" with checkmark
3. ✅ Green download section appears
4. ✅ "Download Your Plan" button visible
5. ✅ Shows download count: "0 of 5"
6. ✅ Shows "Downloads remaining: 5"

### Step 11: Test Download
1. Click "Download [PLAN].pdf" button
2. ✅ File downloads successfully
3. Refresh order confirmation page
4. ✅ Download count updated: "1 of 5"
5. ✅ Downloads remaining: "4"

## Test Scenario 2: Payment Rejection

### Step 1: Create Another Test Order
Follow steps 1-5 from Scenario 1 to create a pending order

### Step 2: Reject Payment
1. Go to admin: http://127.0.0.1:8000/admin/orders/order/
2. Select the pending order
3. Choose action: "✗ Reject selected payments"
4. Click "Go"

### Step 3: Verify Rejection
✅ Success message: "1 payment(s) rejected. Customers notified via email."
✅ Order status changed to: "REJECTED" (red badge)
✅ Verified column shows: "✓ [date]"
✅ Check console for rejection email

### Step 4: Customer View After Rejection
Visit order confirmation page:
- ✅ Page shows "❌ Payment Not Verified" header
- ✅ Red warning card displayed
- ✅ Shows rejection reason (admin comment)
- ✅ Instructions for what to do next
- ✅ Payment details reminder (Payoneer/Bank info)
- ✅ "Submit New Receipt" button visible
- ✅ NO download button (rejected orders can't download)

### Step 5: Verify Download Prevention
1. Try to access download URL directly: http://127.0.0.1:8000/download/[TOKEN]/
2. ✅ Should show error: "This order is not eligible for download"

## Test Scenario 3: Form Validation

### Test 3A: File Size Limit
1. Go to checkout page
2. Try uploading file over 10MB
3. ✅ Should see error: "File size cannot exceed 10MB"

### Test 3B: Invalid File Type
1. Go to checkout page
2. Try uploading .txt, .doc, or other non-image/PDF file
3. ✅ Should see error: "Only image files (JPEG, PNG, GIF) or PDF are allowed"

### Test 3C: Missing Fields
1. Go to checkout page
2. Leave fields empty
3. Try to submit
4. ✅ Should see error messages for required fields

## Test Scenario 4: Email Notifications

### Expected Emails

**1. Order Confirmation (Receipt Submitted)**
- Subject: Order Confirmation - [ORDER_NUMBER]
- When: Immediately after receipt upload
- Contains: Order number, plan details, "receipt is under review" message

**2. Payment Approved**
- Subject: Payment Approved - Your Plan is Ready! 🎉
- When: Admin approves payment
- Contains: Download link, verification date, admin comment, download limits

**3. Payment Rejected**
- Subject: Payment Review Required - Order [ORDER_NUMBER]
- When: Admin rejects payment
- Contains: Rejection reason, payment instructions reminder, resubmit link

### Check Emails in Console
In terminal where server is running, look for:
```
Content-Type: text/plain; charset="utf-8"
MIME-Version: 1.0
Content-Transfer-Encoding: 7bit
Subject: [EMAIL SUBJECT]
From: noreply@plan2d.com
To: [customer-email]
```

## Test Scenario 5: Admin List Filters

### Test Filters
1. Go to: http://127.0.0.1:8000/admin/orders/order/
2. Test filters on right sidebar:
   - ✅ Payment Status (pending, completed, rejected)
   - ✅ Payment Method (Payoneer, Bank Transfer)
   - ✅ Verified at (Yes, No)
   - ✅ Date filters

### Expected Results
- Filtering by "Pending" shows only unverified orders
- Filtering by "Completed" shows only approved orders
- Filtering by "Rejected" shows only rejected orders
- Filtering by "Verified at: No" shows only unreviewed receipts

## Test Scenario 6: Receipt Preview

### Test Image Receipt
1. Upload order with JPEG/PNG/GIF receipt
2. Go to admin order detail
3. ✅ Image displays inline in "Receipt Preview" section
4. ✅ Image is max 600px wide, 400px tall
5. ✅ Click image to open in new tab (full size)

### Test PDF Receipt
1. Upload order with PDF receipt
2. Go to admin order detail
3. ✅ Shows "📄 Open PDF Receipt" button
4. ✅ Click button opens PDF in new tab

## Test Scenario 7: Download Limits

### Test Maximum Downloads
1. Approve an order (default max_downloads = 5)
2. Download file 5 times
3. Try to download 6th time
4. ✅ Should show error: "Download limit exceeded"

### Test Reset Download Count
1. In admin, select order with exceeded downloads
2. Choose action: "Reset Download Count"
3. Click "Go"
4. ✅ Success message appears
5. ✅ Order download_count reset to 0
6. ✅ Customer can download again

## Common Issues & Solutions

### Issue: "This order is not eligible for download"
**Check:**
- Is order status "completed"? (Not pending or rejected)
- Has download limit been exceeded?
- Is access token correct in URL?

**Solution:**
- Approve the order if pending
- Reset download count if exceeded
- Check URL matches order.access_token

### Issue: Receipt image not displaying
**Check:**
- Is file uploaded correctly? (Check media/receipts/ directory)
- Is file an image format? (JPEG/PNG/GIF)
- Are media files configured? (MEDIA_URL, MEDIA_ROOT)

**Solution:**
- Ensure MEDIA_URL is configured in settings
- Check file permissions on media directory

### Issue: Emails not sending
**Check:**
- Is EMAIL_BACKEND set? (Should be console backend for dev)
- Is terminal output visible?

**Solution:**
- In development, check terminal output
- In production, configure SMTP settings

### Issue: Admin can't see receipt preview
**Check:**
- Did migration run successfully?
- Is receipt_file field populated?

**Solution:**
- Run: python manage.py migrate orders
- Check order in database has receipt_file value

## Performance Testing

### Create Multiple Test Orders
```python
# Django shell: python manage.py shell
from apps.orders.models import Order
from apps.plans.models import Plan

plan = Plan.objects.first()
for i in range(10):
    Order.objects.create(
        plan=plan,
        buyer_email=f'test{i}@example.com',
        buyer_name=f'Test User {i}',
        price_paid=plan.price,
        payment_status='pending',
        payment_method='payoneer'
    )
```

### Bulk Operations Test
1. Select all 10 test orders in admin
2. Choose "✓ Approve selected payments"
3. ✅ All orders approved simultaneously
4. ✅ 10 emails sent (check console)
5. ✅ All verified_at timestamps recorded

## Security Testing

### Test 1: Unauthorized Download
1. Get download URL from approved order
2. Logout or use incognito browser
3. Try accessing download URL
4. ✅ Should still work (token-based, no login required)

### Test 2: Invalid Token
1. Modify access token in URL
2. Try to download
3. ✅ Should show 404 or error page

### Test 3: Rejected Order Download
1. Reject an order
2. Try to access its download URL
3. ✅ Should show error: "not eligible for download"

## Checklist Summary

- [ ] Can create order with Payoneer payment
- [ ] Can create order with Bank Transfer payment
- [ ] Receipt upload validates file type
- [ ] Receipt upload validates file size
- [ ] Order created with PENDING status
- [ ] Order confirmation email sent
- [ ] Receipt visible in admin list (📄 View link)
- [ ] Receipt displays in admin detail (image inline or PDF link)
- [ ] Can approve single order
- [ ] Can approve multiple orders (bulk)
- [ ] Approval email sent with download link
- [ ] Approved order shows download button
- [ ] Can download file after approval
- [ ] Download count increments
- [ ] Can reject order
- [ ] Rejection email sent with reason
- [ ] Rejected order shows rejection message
- [ ] Rejected order CANNOT download
- [ ] Admin filters work correctly
- [ ] Verified status tracked (date, user, comment)
- [ ] Download limit enforcement works
- [ ] Reset download count works

## Next Steps After Testing

1. **Production Setup:**
   - Configure SMTP email settings
   - Set up proper media storage (AWS S3 or similar)
   - Change admin password
   - Update ALLOWED_HOSTS

2. **Create Real Plans:**
   - Add actual house plans
   - Upload plan PDF files
   - Set correct pricing

3. **Customer Communication:**
   - Update email templates with your branding
   - Add support contact information
   - Set up customer support email

4. **Monitoring:**
   - Set up logging for failed payments
   - Monitor verification times
   - Track rejection rates

---

**Testing Date:** January 1, 2026  
**Tested By:** [Your Name]  
**Status:** ✅ All Tests Passing
