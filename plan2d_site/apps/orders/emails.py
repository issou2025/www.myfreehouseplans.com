"""
Email notifications for orders.
"""
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.urls import reverse


def send_order_confirmation_email(order):
    """
    Send order confirmation email to buyer.
    """
    subject = f"Order Confirmation - {order.order_number}"
    
    context = {
        'order': order,
        'site_url': getattr(settings, 'SITE_URL', 'http://localhost:8000'),
    }
    
    # Plain text message
    message = f"""
Thank you for your order!

Order Number: {order.order_number}
Plan: {order.plan.title} ({order.plan.reference})
Price: ${order.price_paid}
Status: {order.get_payment_status_display()}

{'Your download link is ready!' if order.payment_status == 'completed' else 'Payment instructions will be sent separately.'}

View your order: {context['site_url']}/orders/confirmation/{order.order_number}/

    Thank you for choosing {getattr(settings, 'BRAND_DOMAIN', 'FreeHousePlan.com')}!
    """
    
    # Send email
    try:
        send_mail(
            subject=subject,
            message=message,
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'FreeHousePlan.com <noreply@freehouseplan.com>'),
            recipient_list=[order.buyer_email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False


def send_download_link_email(order):
    """
    Send download link after payment is completed.
    """
    if order.payment_status != order.COMPLETED:
        return False
    
    subject = f"Your Plan is Ready! - {order.plan.title}"
    
    context = {
        'order': order,
        'site_url': getattr(settings, 'SITE_URL', 'http://localhost:8000'),
        'download_url': f"{getattr(settings, 'SITE_URL', 'http://localhost:8000')}/download/{order.access_token}/",
    }
    
    message = f"""
Great news! Your payment has been confirmed.

Your house plan is ready for download:

Plan: {order.plan.title}
Reference: {order.plan.reference}
Order: {order.order_number}

Download Link:
{context['download_url']}

Important:
{'- Access expires: ' + order.access_expires_at.strftime('%B %d, %Y') if order.access_expires_at else '- Lifetime access'}

    Need help? Contact us at {getattr(settings, 'SUPPORT_EMAIL', 'support@freehouseplan.com')}

    Thank you for choosing {getattr(settings, 'BRAND_DOMAIN', 'FreeHousePlan.com')}!
    """
    
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'FreeHousePlan.com <noreply@freehouseplan.com>'),
            recipient_list=[order.buyer_email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False


def send_payment_instructions_email(order):
    """
    Send payment instructions for manual payment.
    """
    if order.payment_status != order.PENDING:
        return False
    
    subject = f"Payment Instructions - Order {order.order_number}"
    
    message = f"""
Thank you for your order!

Order Number: {order.order_number}
Plan: {order.plan.title}
Amount Due: ${order.price_paid}

PAYMENT INSTRUCTIONS:
[Payment details will be added here based on your setup]

    For now, please contact {getattr(settings, 'SUPPORT_EMAIL', 'support@freehouseplan.com')} with your order number to arrange payment.

Once payment is confirmed, you'll receive your download link immediately.

Order Details:
{getattr(settings, 'SITE_URL', 'http://localhost:8000')}/orders/confirmation/{order.order_number}/

Thank you!
    {getattr(settings, 'BRAND_NAME', 'FreeHousePlan')} Team
    """
    
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'FreeHousePlan.com <noreply@freehouseplan.com>'),
            recipient_list=[order.buyer_email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False


def send_payment_approved_email(order):
    """
    Send email when manual payment is approved.
    """
    if order.payment_status != order.COMPLETED:
        return False
    
    subject = f"Payment Approved - Your Plan is Ready! 🎉"
    
    download_url = f"{getattr(settings, 'SITE_URL', 'http://localhost:8000')}/download/{order.access_token}/"
    
    message = f"""
Great news! Your payment has been verified and approved.

Order Number: {order.order_number}
Plan: {order.plan.title}
Reference: {order.plan.reference}
Verified: {order.verified_at.strftime('%B %d, %Y at %I:%M %p') if order.verified_at else 'Just now'}

YOUR DOWNLOAD LINK:
{download_url}

Important Information:
✓ This link is unique and secure
✓ You can download up to {order.max_downloads} times
✓ Downloads remaining: {order.downloads_remaining}
{'✓ Access expires: ' + order.access_expires_at.strftime('%B %d, %Y') if order.access_expires_at else '✓ Lifetime access included'}

{f'Admin Note: {order.admin_comment}' if order.admin_comment else ''}

    Need assistance? Contact us at {getattr(settings, 'SUPPORT_EMAIL', 'support@freehouseplan.com')}

    Thank you for choosing {getattr(settings, 'BRAND_DOMAIN', 'FreeHousePlan.com')}!
    {getattr(settings, 'BRAND_NAME', 'FreeHousePlan')} Team
    """
    
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'FreeHousePlan.com <noreply@freehouseplan.com>'),
            recipient_list=[order.buyer_email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False


def send_payment_rejected_email(order):
    """
    Send email when manual payment is rejected.
    """
    if order.payment_status != order.REJECTED:
        return False
    
    subject = f"Payment Review Required - Order {order.order_number}"
    
    message = f"""
Thank you for submitting your payment receipt.

Order Number: {order.order_number}
Plan: {order.plan.title}
Amount: ${order.price_paid}

Unfortunately, we were unable to verify your payment with the information provided.

Reason: {order.admin_comment if order.admin_comment else 'Receipt could not be validated'}

WHAT TO DO NEXT:

1. Double-check that you sent the payment to:
   - Payoneer: bacseried@gmail.com (Issoufou Abdou Chéfou)
   OR
   - Bank of Africa Niger
     Account: Abdou Chefou Issoufou
     SWIFT: AFRINENIXXX
     IBAN: NE58NE0380100400440716000006

2. Re-upload a clear receipt showing:
   ✓ Transaction date
   ✓ Amount ({order.price_paid} {order.currency})
   ✓ Recipient details
   ✓ Your name

3. Visit your order page to resubmit:
   {getattr(settings, 'SITE_URL', 'http://localhost:8000')}/orders/confirmation/{order.order_number}/

We're here to help! If you have questions, reply to this email or contact:
{getattr(settings, 'SUPPORT_EMAIL', 'support@freehouseplan.com')} (include order #{order.order_number})

Thank you for your patience,
{getattr(settings, 'BRAND_NAME', 'FreeHousePlan')} Team
    """
    
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'FreeHousePlan.com <noreply@freehouseplan.com>'),
            recipient_list=[order.buyer_email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False
