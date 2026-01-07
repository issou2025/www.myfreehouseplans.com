# Manual Payment System Documentation

## Overview
This document explains the complete manual payment verification system implemented for Plan2D, designed for markets where Stripe and PayPal are not available.

## Payment Methods Supported

### 1. Payoneer Transfer
- **Account Email:** bacseried@gmail.com
- **Account Holder:** Issoufou Abdou Chéfou
- **Instructions:** Customers send money via Payoneer and upload the receipt

### 2. Bank Transfer (SWIFT)
- **Bank:** Bank of Africa Niger
- **Account Holder:** Abdou Chefou Issoufou
- **Currency:** XOF (West African CFA Franc)
- **SWIFT Code:** AFRINENIXXX
- **IBAN:** NE58NE0380100400440716000006
- **Instructions:** Customers make international wire transfer and upload receipt

## Customer Workflow

### Step 1: Customer Selects Plan
- Customer browses plans and clicks "Buy Now"
- Redirected to `/checkout/<plan_id>/`

### Step 2: Payment Instructions Displayed
The checkout page shows:
- Plan details and price
- Two payment options side-by-side (Payoneer vs Bank Transfer)
- Step-by-step instructions for each method
- Receipt upload form

### Step 3: Customer Makes Payment
Customer transfers money using either:
- Payoneer (faster, typically 1-3 business days)
- Bank Transfer (slower, 3-7 business days)

### Step 4: Receipt Upload
Customer fills out form:
- Full Name
- Email Address
- Payment Method (dropdown)
- Receipt File (image or PDF, max 10MB)

**Receipt Requirements:**
- Must show: transaction date, amount, recipient, sender name
- Accepted formats: JPEG, PNG, GIF, PDF
- Maximum size: 10MB

### Step 5: Order Created
- Order saved with status: `PENDING`
- Receipt stored in: `media/receipts/YYYY/MM/filename.ext`
- Confirmation email sent to customer
- Customer redirected to order confirmation page

### Step 6: Customer Waits
- Typical verification time: **24 hours**
- Customer receives status page showing "Under Review"
- Email notification when status changes

## Admin Workflow

### Admin Access
1. Login at: http://127.0.0.1:8000/admin/
2. Navigate to: **Orders** → **Orders**
3. Filter by: `Payment Status = Pending` and `Verified at = No`

### Order List View
Admin sees these columns:
- Order Number
- Buyer Email
- Plan (clickable link)
- Payment Method (💳 Payoneer or 🏦 Bank Transfer)
- Price
- Status Badge (color-coded)
- **Receipt** (📄 View link)
- **Verified** (✓ Date or ⏳ Pending)
- Created Date

### Verification Process

#### Step 1: Open Order
Click order number to view details

#### Step 2: Review Receipt
In "Manual Payment Verification" section:
- View uploaded receipt (images show inline, PDFs have "Open PDF" button)
- Check transaction details match order
- Verify amount, date, recipient

#### Step 3: Approve or Reject

**To Approve Single Order:**
1. Click into order detail
2. Scroll to "Manual Payment Verification" section
3. Add optional admin comment
4. Click **Save and continue editing**
5. Then use bulk action "✓ Approve selected payments"

**To Approve Multiple Orders:**
1. Select orders using checkboxes
2. Choose action: "✓ Approve selected payments"
3. Click "Go"
4. System automatically:
   - Updates status to `COMPLETED`
   - Records verification timestamp
   - Records admin user who approved
   - Sends approval email with download link

**To Reject Orders:**
1. Select orders using checkboxes
2. Choose action: "✗ Reject selected payments"
3. Click "Go"
4. System automatically:
   - Updates status to `REJECTED`
   - Records verification timestamp
   - Records admin user who rejected
   - Sends rejection email with instructions

### Admin Actions Available
- **✓ Approve selected payments** - Approve manual payments and send download links
- **✗ Reject selected payments** - Reject payments with standard reason
- Mark as Completed
- Mark as Failed
- Reset Download Count

## Email Notifications

### 1. Order Confirmation (Automatic)
**Sent:** When customer submits receipt
**To:** Customer
**Subject:** Order Confirmation - [ORDER_NUMBER]
**Content:**
- Order number and plan details
- "Receipt is under review" message
- Link to order confirmation page

### 2. Payment Approved (Automatic)
**Sent:** When admin approves payment
**To:** Customer
**Subject:** Payment Approved - Your Plan is Ready! 🎉
**Content:**
- Verification confirmation
- **Secure download link**
- Download limits (5 downloads)
- Admin comment (if any)

### 3. Payment Rejected (Automatic)
**Sent:** When admin rejects payment
**To:** Customer
**Subject:** Payment Review Required - Order [ORDER_NUMBER]
**Content:**
- Rejection reason (admin comment)
- Payment instructions reminder (Payoneer/Bank details)
- What to check in receipt
- Link to resubmit

## Technical Implementation

### Models (apps/orders/models.py)

#### Order Model Fields
```python
# Manual Payment Fields
payment_method = models.CharField(choices=['payoneer', 'bank_transfer'])
receipt_file = models.FileField(upload_to='receipts/%Y/%m/')
verified_at = models.DateTimeField(null=True)
verified_by = models.ForeignKey(User, related_name='verified_orders')
admin_comment = models.TextField(blank=True)

# Payment Status Choices
PENDING = 'pending'
COMPLETED = 'completed'
REJECTED = 'rejected'
FAILED = 'failed'
REFUNDED = 'refunded'
```

#### Order Model Methods
```python
def approve_payment(admin_user, comment=''):
    """Sets status to COMPLETED, records verification, sends approval email"""

def reject_payment(admin_user, comment=''):
    """Sets status to REJECTED, records verification, sends rejection email"""

def can_download():
    """Returns True only if status is COMPLETED and download limit not exceeded"""
```

### Forms (apps/orders/forms.py)

#### ReceiptUploadForm
```python
class ReceiptUploadForm(forms.Form):
    buyer_name = forms.CharField(max_length=255)
    buyer_email = forms.EmailField()
    payment_method = forms.ChoiceField(choices=[
        ('payoneer', 'Payoneer Transfer'),
        ('bank_transfer', 'Bank Transfer (SWIFT)')
    ])
    receipt_file = forms.FileField()
    
    def clean_receipt_file(self):
        # Validates: max 10MB, only images/PDF
```

### Views (apps/orders/views.py)

#### CheckoutView
```python
def get(request, plan_id):
    # Displays payment instructions and receipt upload form
    
def post(request, plan_id):
    # Validates receipt, creates order with PENDING status
    # Sends confirmation email
    # Redirects to order confirmation
```

### Admin (apps/orders/admin.py)

#### OrderAdmin Configuration
```python
list_display = [
    'order_number', 'buyer_email', 'plan_link',
    'payment_method', 'price_paid', 'status_badge',
    'receipt_preview', 'verified_status', 'created_at'
]

readonly_fields = ['verified_at', 'verified_by', 'receipt_image_preview']

actions = ['approve_payments', 'reject_payments']
```

#### Display Methods
- `receipt_preview()` - Shows "📄 View" link in list
- `verified_status()` - Shows "✓ Date" or "⏳ Pending"
- `receipt_image_preview()` - Full receipt in detail view
- `status_badge()` - Color-coded status badge

### Email Functions (apps/orders/emails.py)

#### Available Functions
- `send_order_confirmation_email(order)` - Receipt submitted
- `send_payment_approved_email(order)` - Payment verified
- `send_payment_rejected_email(order)` - Payment rejected
- `send_download_link_email(order)` - Download ready

### Security Features

#### Receipt Upload
- File type validation: only images (JPEG/PNG/GIF) and PDF
- File size limit: 10MB maximum
- Files stored in: `media/receipts/YYYY/MM/` (organized by date)

#### Download Protection
- Unique access tokens (64 characters, cryptographically secure)
- Download limits: 5 downloads per order
- Status check: Only `COMPLETED` orders can download
- `REJECTED` orders cannot access files

#### Admin Tracking
- `verified_by` - Records which admin approved/rejected
- `verified_at` - Timestamp of verification
- `admin_comment` - Reason for rejection or approval notes

## Testing Checklist

### Customer Side
- [ ] Can view payment instructions at checkout
- [ ] Can upload receipt (valid formats)
- [ ] Sees error for invalid file types
- [ ] Sees error for files over 10MB
- [ ] Receives order confirmation email
- [ ] Can view order status (pending)
- [ ] Receives approval email with download link (after admin approves)
- [ ] Can download file after approval
- [ ] Cannot download if rejected
- [ ] Receives rejection email with reason

### Admin Side
- [ ] Can see pending orders in admin list
- [ ] Can filter by payment method (Payoneer/Bank Transfer)
- [ ] Can view receipt inline (images) or open PDF
- [ ] Can approve single order
- [ ] Can approve multiple orders (bulk action)
- [ ] Can reject orders with comment
- [ ] Can see who verified and when
- [ ] Cannot download count shows correctly

## Database Migration

The manual payment system was added with migration:
```bash
python manage.py makemigrations orders
python manage.py migrate orders
```

**Migration:** `0002_order_admin_comment_order_payment_method_and_more.py`

**Fields Added:**
- `payment_method` (CharField)
- `receipt_file` (FileField)
- `verified_at` (DateTimeField, nullable)
- `verified_by` (ForeignKey to User, nullable)
- `admin_comment` (TextField)

## Configuration

### Media Files
Ensure `MEDIA_ROOT` and `MEDIA_URL` are configured in settings:

```python
# settings/dev.py
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
```

### Email Settings
Currently using console backend for development:

```python
# settings/dev.py
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

**For Production:**
```python
# settings/prod.py
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
DEFAULT_FROM_EMAIL = 'noreply@plan2d.com'
```

### Payment Details
Payment information is **hardcoded** in:
- `apps/orders/views.py` (CheckoutView)
- `apps/orders/emails.py` (rejection email)

To change payment details, edit these files.

## Support Scenarios

### Customer Reports "Payment Not Verified"

**Check:**
1. Is receipt readable/clear?
2. Does amount match order price?
3. Does recipient match payment details?
4. Is transaction date recent?

**Resolution:**
- If receipt valid: Approve payment
- If receipt invalid: Reject with specific reason
- If unclear: Contact customer via email

### Customer Uploaded Wrong Receipt

**Resolution:**
1. Reject current order with reason: "Please upload receipt for this specific order"
2. Customer will receive email with resubmit link
3. Customer can resubmit with correct receipt

### Payment Received but No Receipt

**Resolution:**
1. Contact customer at buyer_email
2. Request receipt upload
3. Once uploaded, verify and approve

### Download Link Not Working

**Check:**
1. Is order status `COMPLETED`?
2. Has download limit been exceeded?
3. Is access token valid?

**Resolution:**
- If status wrong: Approve payment
- If downloads exceeded: Reset download count (admin action)
- If token invalid: Technical issue, contact developer

## Future Enhancements

### Potential Improvements
1. **Custom rejection reasons** - Dropdown instead of hardcoded message
2. **Receipt re-upload** - Allow customers to replace receipt without new order
3. **Mobile Money** - Add MTN Mobile Money, Orange Money support
4. **Auto-verification** - OCR scanning of receipts (advanced)
5. **SMS notifications** - Text messages for status updates
6. **Multi-currency** - Support XOF, USD, EUR display
7. **Admin dashboard** - Statistics on verification times, rejection rates
8. **Customer dashboard** - View all orders, resubmit receipts

## Admin Credentials

**Username:** admin  
**Password:** admin123  
**Admin URL:** http://127.0.0.1:8000/admin/

**IMPORTANT:** Change the admin password in production!

## File Locations

### Backend Files
- Models: `apps/orders/models.py`
- Forms: `apps/orders/forms.py`
- Views: `apps/orders/views.py`
- Admin: `apps/orders/admin.py`
- Emails: `apps/orders/emails.py`

### Frontend Files
- Checkout Template: `apps/orders/templates/orders/checkout.html`
- Confirmation Template: `apps/orders/templates/orders/order_confirmation.html`

### Media Storage
- Receipts: `media/receipts/YYYY/MM/`

## Support Contact

For questions about this system:
- **Developer:** [Your Contact]
- **Support Email:** support@plan2d.com
- **Admin Panel:** http://127.0.0.1:8000/admin/

---

**Last Updated:** January 1, 2026  
**System Version:** 1.0  
**Django Version:** 5.0.1  
**Python Version:** 3.13.0
