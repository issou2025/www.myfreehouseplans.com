from django.db import models
from django.utils import timezone
import os


def contact_upload_path(instance, filename):
    """
    Generate unique path for contact message attachments.
    """
    # Sanitize filename
    name, ext = os.path.splitext(filename)
    safe_name = "".join(c for c in name if c.isalnum() or c in (' ', '-', '_')).strip()
    safe_name = safe_name[:50]  # Limit length
    timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
    return f'contact_uploads/{timestamp}_{safe_name}{ext}'


class ContactMessage(models.Model):
    """
    Store contact form submissions with optional file attachments.
    """
    SUBJECT_CHOICES = [
        ('general', 'General Inquiry'),
        ('plans', 'Question About Plans'),
        ('purchase', 'Purchase Support'),
        ('technical', 'Technical Question'),
        ('other', 'Other'),
    ]
    
    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    subject = models.CharField(max_length=50, choices=SUBJECT_CHOICES)
    message = models.TextField()
    attachment = models.FileField(
        upload_to=contact_upload_path,
        blank=True,
        null=True,
        help_text='Optional file attachment (PDF, JPG, PNG, ZIP - Max 10MB)'
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.CharField(max_length=500, blank=True)
    is_read = models.BooleanField(default=False)
    admin_notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Contact Message'
        verbose_name_plural = 'Contact Messages'
    
    def __str__(self):
        return f"{self.full_name} - {self.get_subject_display()} ({self.created_at.strftime('%Y-%m-%d')})"
    
    @property
    def has_attachment(self):
        return bool(self.attachment)
    
    @property
    def attachment_filename(self):
        if self.attachment:
            return os.path.basename(self.attachment.name)
        return None
