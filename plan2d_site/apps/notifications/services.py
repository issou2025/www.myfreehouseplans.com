"""Centralized notification services.

All admin notifications go through this module for consistent logging and error handling.
"""
import logging
from django.core.mail import EmailMessage
from django.conf import settings
from django.utils import timezone
from .models import EmailLog

# Configure logger
logger = logging.getLogger('notifications')


class NotificationService:
    """
    Central service for sending all notifications.
    Provides consistent logging, error handling, and retry logic.
    """
    
    @classmethod
    def get_admin_email(cls):
        """Get admin email from settings."""
        return getattr(settings, 'ADMIN_EMAIL', 'entreprise2rc@gmail.com')
    
    @classmethod
    def get_from_email(cls):
        """Get default from email."""
        return getattr(settings, 'DEFAULT_FROM_EMAIL', 'FreeHousePlan.com <noreply@freehouseplan.com>')
    
    @classmethod
    def send_email(cls, to_email, subject, body, category='other', 
                   attachment_path=None, attachment_name=None,
                   reply_to=None, related_contact_id=None, related_order_id=None,
                   fail_silently=False):
        """
        Send an email with full logging and error tracking.
        
        Args:
            to_email: Recipient email address
            subject: Email subject line
            body: Plain text email body
            category: Category for logging (see EmailLog.CATEGORY_CHOICES)
            attachment_path: Path to file to attach (optional)
            attachment_name: Display name for attachment (optional)
            reply_to: Reply-to email address (optional)
            related_contact_id: ID of related ContactMessage (optional)
            related_order_id: ID of related Order (optional)
            fail_silently: If True, don't raise exceptions on failure
            
        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        # Create log entry
        log_entry = EmailLog.objects.create(
            to_email=to_email,
            from_email=cls.get_from_email(),
            subject=subject,
            category=category,
            status='pending',
            has_attachment=bool(attachment_path),
            attachment_name=attachment_name or '',
            related_contact_id=related_contact_id,
            related_order_id=related_order_id,
        )
        
        try:
            # Build email
            email = EmailMessage(
                subject=subject,
                body=body,
                from_email=cls.get_from_email(),
                to=[to_email],
                reply_to=[reply_to] if reply_to else None,
            )
            
            # Add attachment if provided
            if attachment_path:
                try:
                    email.attach_file(attachment_path)
                    logger.info(f"Attached file: {attachment_path}")
                except Exception as attach_error:
                    logger.warning(f"Could not attach file {attachment_path}: {attach_error}")
                    # Continue sending email without attachment
            
            # Send email
            email.send(fail_silently=False)
            
            # Mark as sent
            log_entry.mark_sent()
            logger.info(f"Email sent successfully: [{category}] {subject} -> {to_email}")
            
            return True
            
        except Exception as e:
            # Log failure
            error_msg = str(e)
            log_entry.mark_failed(error_msg)
            logger.error(f"Email FAILED: [{category}] {subject} -> {to_email} | Error: {error_msg}")
            
            if not fail_silently:
                raise
            
            return False
    
    # ========================================
    # Admin Notification Methods
    # ========================================
    
    @classmethod
    def notify_admin_new_contact(cls, contact_msg):
        """
        Send admin notification when a new contact message is received.
        
        Args:
            contact_msg: ContactMessage instance
            
        Returns:
            bool: True if notification sent successfully
        """
        subject = f"[Contact Form] {contact_msg.get_subject_display()} - {contact_msg.full_name}"
        
        body = f"""
════════════════════════════════════════════════════════════
📬 NEW CONTACT MESSAGE RECEIVED
════════════════════════════════════════════════════════════

From: {contact_msg.full_name}
Email: {contact_msg.email}
Subject: {contact_msg.get_subject_display()}
Date: {contact_msg.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')}
IP Address: {contact_msg.ip_address or 'Unknown'}

────────────────────────────────────────────────────────────
MESSAGE:
────────────────────────────────────────────────────────────

{contact_msg.message}

────────────────────────────────────────────────────────────
ATTACHMENT: {'✓ Yes - ' + contact_msg.attachment_filename if contact_msg.has_attachment else '✗ None'}
────────────────────────────────────────────────────────────

Reply directly to: {contact_msg.email}

---
This notification was sent by the {getattr(settings, 'BRAND_DOMAIN', 'FreeHousePlan.com')} Contact System.
Manage messages: {getattr(settings, 'SITE_URL', 'http://localhost:8000')}/admin/core/contactmessage/
"""
        
        return cls.send_email(
            to_email=cls.get_admin_email(),
            subject=subject,
            body=body,
            category='contact_admin',
            attachment_path=contact_msg.attachment.path if contact_msg.has_attachment else None,
            attachment_name=contact_msg.attachment_filename if contact_msg.has_attachment else None,
            reply_to=contact_msg.email,
            related_contact_id=contact_msg.pk,
            fail_silently=True,  # Don't fail user's submission if email fails
        )
    
    @classmethod
    def notify_admin_new_order(cls, order):
        """
        Send admin notification when a new order is placed.
        Includes receipt attachment if present.
        
        Args:
            order: Order instance
            
        Returns:
            bool: True if notification sent successfully
        """
        subject = f"[New Order] {order.order_number} - {order.plan.title} - ${order.price_paid}"
        
        receipt_info = ""
        if order.receipt_file:
            receipt_info = f"""
────────────────────────────────────────────────────────────
PAYMENT RECEIPT: ✓ ATTACHED
────────────────────────────────────────────────────────────
Receipt file is attached to this email for verification.
"""
        else:
            receipt_info = """
────────────────────────────────────────────────────────────
PAYMENT RECEIPT: ✗ NOT UPLOADED
────────────────────────────────────────────────────────────
Customer has not uploaded a receipt yet.
"""
        
        body = f"""
════════════════════════════════════════════════════════════
💰 NEW ORDER RECEIVED - ACTION REQUIRED
════════════════════════════════════════════════════════════

Order Number: {order.order_number}
Status: {order.get_payment_status_display()}
Created: {order.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')}

────────────────────────────────────────────────────────────
CUSTOMER INFORMATION:
────────────────────────────────────────────────────────────

Name: {order.buyer_name or 'Not provided'}
Email: {order.buyer_email}

────────────────────────────────────────────────────────────
ORDER DETAILS:
────────────────────────────────────────────────────────────

Plan: {order.plan.title}
Reference: {order.plan.reference}
Price: ${order.price_paid} {order.currency}
Payment Method: {order.get_payment_method_display() if order.payment_method else 'Not specified'}
Payment Provider: {order.get_payment_provider_display()}
{receipt_info}
────────────────────────────────────────────────────────────
REQUIRED ACTION:
────────────────────────────────────────────────────────────

1. Review the payment receipt
2. Verify payment was received to your account
3. Approve or reject the order in the admin panel

Admin Panel: {getattr(settings, 'SITE_URL', 'http://localhost:8000')}/admin/orders/order/{order.pk}/change/

---
This notification was sent by the {getattr(settings, 'BRAND_DOMAIN', 'FreeHousePlan.com')} Order System.
"""
        
        return cls.send_email(
            to_email=cls.get_admin_email(),
            subject=subject,
            body=body,
            category='order_admin',
            attachment_path=order.receipt_file.path if order.receipt_file else None,
            attachment_name=f"receipt_{order.order_number}.{order.receipt_file.name.split('.')[-1]}" if order.receipt_file else None,
            reply_to=order.buyer_email,
            related_order_id=order.pk,
            fail_silently=True,  # Don't fail user's submission if email fails
        )
    
    @classmethod
    def notify_admin_receipt_uploaded(cls, order):
        """
        Send admin notification when a receipt is uploaded to an existing order.
        
        Args:
            order: Order instance with newly uploaded receipt
            
        Returns:
            bool: True if notification sent successfully
        """
        subject = f"[Receipt Uploaded] {order.order_number} - Needs Verification"
        
        body = f"""
════════════════════════════════════════════════════════════
📎 PAYMENT RECEIPT UPLOADED - VERIFICATION NEEDED
════════════════════════════════════════════════════════════

Order Number: {order.order_number}
Customer: {order.buyer_name or 'Not provided'} ({order.buyer_email})

Plan: {order.plan.title}
Price: ${order.price_paid} {order.currency}
Payment Method: {order.get_payment_method_display() if order.payment_method else 'Not specified'}

────────────────────────────────────────────────────────────
RECEIPT ATTACHED
────────────────────────────────────────────────────────────

Please review the attached receipt and verify payment.

Action required: Approve or reject in admin panel
Admin Panel: {getattr(settings, 'SITE_URL', 'http://localhost:8000')}/admin/orders/order/{order.pk}/change/

---
This notification was sent by the {getattr(settings, 'BRAND_DOMAIN', 'FreeHousePlan.com')} Order System.
"""
        
        return cls.send_email(
            to_email=cls.get_admin_email(),
            subject=subject,
            body=body,
            category='order_admin',
            attachment_path=order.receipt_file.path if order.receipt_file else None,
            attachment_name=f"receipt_{order.order_number}.{order.receipt_file.name.split('.')[-1]}" if order.receipt_file else None,
            reply_to=order.buyer_email,
            related_order_id=order.pk,
            fail_silently=True,
        )


# Convenience functions for backward compatibility
def notify_admin_new_contact(contact_msg):
    """Send admin notification for new contact message."""
    return NotificationService.notify_admin_new_contact(contact_msg)


def notify_admin_new_order(order):
    """Send admin notification for new order."""
    return NotificationService.notify_admin_new_order(order)


def notify_admin_receipt_uploaded(order):
    """Send admin notification when receipt is uploaded."""
    return NotificationService.notify_admin_receipt_uploaded(order)
