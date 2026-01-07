"""
Order models for managing plan purchases.
Designed to work without user accounts and support multiple payment providers.
"""
from django.db import models
from django.utils import timezone
from django.core.validators import EmailValidator
import uuid
import secrets


class Order(models.Model):
    """
    Represents a purchase of a house plan.
    Works without user accounts - tracked by email and secure token.
    """
    # Payment Status Choices
    PENDING = 'pending'
    PROCESSING = 'processing'
    COMPLETED = 'completed'
    FAILED = 'failed'
    REFUNDED = 'refunded'
    REJECTED = 'rejected'
    
    STATUS_CHOICES = [
        (PENDING, 'Pending Verification'),
        (PROCESSING, 'Processing'),
        (COMPLETED, 'Approved'),
        (FAILED, 'Failed'),
        (REJECTED, 'Rejected'),
        (REFUNDED, 'Refunded'),
    ]
    
    # Payment Method Choices (for manual payments)
    PAYONEER_TRANSFER = 'payoneer'
    BANK_TRANSFER = 'bank_transfer'
    
    PAYMENT_METHOD_CHOICES = [
        (PAYONEER_TRANSFER, 'Payoneer Transfer'),
        (BANK_TRANSFER, 'Bank Transfer (SWIFT)'),
    ]
    
    # Payment Provider Choices (extensible)
    PAYONEER = 'payoneer'
    LEMON_SQUEEZY = 'lemon_squeezy'
    MANUAL = 'manual'
    
    PROVIDER_CHOICES = [
        (PAYONEER, 'Payoneer'),
        (LEMON_SQUEEZY, 'Lemon Squeezy'),
        (MANUAL, 'Manual Payment'),
    ]
    
    # Core Fields
    order_number = models.CharField(
        max_length=32,
        unique=True,
        editable=False,
        help_text="Unique order identifier"
    )
    
    # Buyer Information (no account required)
    buyer_email = models.EmailField(
        validators=[EmailValidator()],
        help_text="Buyer's email address for delivery"
    )
    buyer_name = models.CharField(
        max_length=200,
        blank=True,
        help_text="Optional: Buyer's name"
    )
    
    # Plan Purchase - PROTECTED: Cannot delete plan if orders exist
    plan = models.ForeignKey(
        'plans.Plan',
        on_delete=models.PROTECT,  # CRITICAL: Prevents accidental plan deletion
        related_name='orders',
        help_text="The plan being purchased (deletion blocked if orders exist)"
    )
    
    # Pricing (snapshot at time of purchase)
    price_paid = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Amount paid (captures price at purchase time)"
    )
    currency = models.CharField(
        max_length=3,
        default='USD',
        help_text="Currency code (USD, EUR, etc.)"
    )
    
    # Payment Information
    payment_status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=PENDING,
        db_index=True
    )
    payment_provider = models.CharField(
        max_length=50,
        choices=PROVIDER_CHOICES,
        default=MANUAL,
        help_text="Payment gateway used"
    )
    payment_provider_id = models.CharField(
        max_length=255,
        blank=True,
        help_text="Transaction ID from payment provider"
    )
    
    # Manual Payment Fields
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        blank=True,
        help_text="Payment method used (Payoneer or Bank Transfer)"
    )
    receipt_file = models.FileField(
        upload_to='receipts/%Y/%m/',
        blank=True,
        null=True,
        help_text="Payment receipt uploaded by customer"
    )
    verified_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When payment was verified by admin"
    )
    verified_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_orders',
        help_text="Admin who verified this payment"
    )
    admin_comment = models.TextField(
        blank=True,
        help_text="Admin notes about payment verification"
    )
    
    # Security & Access Control
    access_token = models.CharField(
        max_length=64,
        unique=True,
        editable=False,
        db_index=True,
        help_text="Secure token for downloading purchased plan"
    )
    download_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of times file has been downloaded"
    )
    max_downloads = models.PositiveIntegerField(
        default=5,
        help_text="Maximum allowed downloads (prevents sharing)"
    )
    access_expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Optional: Access expiration date"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When payment was completed"
    )
    
    # Admin Notes
    notes = models.TextField(
        blank=True,
        help_text="Internal notes about this order"
    )
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['buyer_email', '-created_at']),
            models.Index(fields=['payment_status', '-created_at']),
        ]
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
    
    def __str__(self):
        return f"{self.order_number} - {self.plan.title} ({self.get_payment_status_display()})"
    
    def save(self, *args, **kwargs):
        """Auto-generate order number and access token on creation."""
        if not self.order_number:
            self.order_number = self.generate_order_number()
        if not self.access_token:
            self.access_token = self.generate_access_token()
        super().save(*args, **kwargs)
    
    @staticmethod
    def generate_order_number():
        """Generate unique order number: ORD-YYYYMMDD-RANDOM"""
        date_part = timezone.now().strftime('%Y%m%d')
        random_part = uuid.uuid4().hex[:8].upper()
        return f"ORD-{date_part}-{random_part}"
    
    @staticmethod
    def generate_access_token():
        """Generate cryptographically secure access token."""
        return secrets.token_urlsafe(48)
    
    def mark_completed(self):
        """Mark order as completed and record timestamp."""
        if self.payment_status != self.COMPLETED:
            self.payment_status = self.COMPLETED
            self.completed_at = timezone.now()
            self.save(update_fields=['payment_status', 'completed_at', 'updated_at'])
    
    def approve_payment(self, admin_user, comment=''):
        """Approve manual payment after verification."""
        from .emails import send_payment_approved_email
        
        self.payment_status = self.COMPLETED
        self.verified_at = timezone.now()
        self.verified_by = admin_user
        self.completed_at = timezone.now()
        if comment:
            self.admin_comment = comment
        self.save()
        
        # Send approval email
        send_payment_approved_email(self)
    
    def reject_payment(self, admin_user, comment=''):
        """Reject manual payment."""
        from .emails import send_payment_rejected_email
        
        self.payment_status = self.REJECTED
        self.verified_at = timezone.now()
        self.verified_by = admin_user
        if comment:
            self.admin_comment = comment
        self.save()
        
        # Send rejection email
        send_payment_rejected_email(self)
    
    def can_download(self):
        """Check if download is still allowed."""
        # Must be completed
        if self.payment_status != self.COMPLETED:
            return False
        
        # Check download limit
        if self.download_count >= self.max_downloads:
            return False
        
        # Check expiration
        if self.access_expires_at and timezone.now() > self.access_expires_at:
            return False
        
        return True
    
    def increment_download(self):
        """Track download attempt."""
        self.download_count += 1
        self.save(update_fields=['download_count', 'updated_at'])
    
    @property
    def is_expired(self):
        """Check if access has expired."""
        if not self.access_expires_at:
            return False
        return timezone.now() > self.access_expires_at
    
    @property
    def downloads_remaining(self):
        """Calculate remaining downloads."""
        return max(0, self.max_downloads - self.download_count)
