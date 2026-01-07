"""
Models for tracking notification delivery and failures.
"""
from django.db import models
from django.utils import timezone


class EmailLog(models.Model):
    """
    Track all email notifications sent by the system.
    Helps debug delivery issues and provides audit trail.
    """
    STATUS_CHOICES = [
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('pending', 'Pending'),
    ]
    
    CATEGORY_CHOICES = [
        ('contact_admin', 'Contact - Admin Notification'),
        ('order_admin', 'Order - Admin Notification'),
        ('order_confirmation', 'Order - Buyer Confirmation'),
        ('order_approved', 'Order - Payment Approved'),
        ('order_rejected', 'Order - Payment Rejected'),
        ('download_link', 'Order - Download Link'),
        ('other', 'Other'),
    ]
    
    # Email details
    to_email = models.EmailField()
    from_email = models.EmailField()
    subject = models.CharField(max_length=500)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='other')
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True)
    
    # Reference to related objects
    related_contact_id = models.PositiveIntegerField(null=True, blank=True)
    related_order_id = models.PositiveIntegerField(null=True, blank=True)
    
    # Metadata
    has_attachment = models.BooleanField(default=False)
    attachment_name = models.CharField(max_length=255, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Email Log'
        verbose_name_plural = 'Email Logs'
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['category', '-created_at']),
        ]
    
    def __str__(self):
        return f"[{self.get_status_display()}] {self.subject[:50]}... -> {self.to_email}"
    
    def mark_sent(self):
        """Mark email as successfully sent."""
        self.status = 'sent'
        self.sent_at = timezone.now()
        self.save(update_fields=['status', 'sent_at'])
    
    def mark_failed(self, error_message):
        """Mark email as failed with error details."""
        self.status = 'failed'
        self.error_message = str(error_message)[:1000]
        self.save(update_fields=['status', 'error_message'])
