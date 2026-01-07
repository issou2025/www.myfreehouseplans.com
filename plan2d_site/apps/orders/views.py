"""
Order views for purchase and download flow.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View, TemplateView
from django.contrib import messages
from django.http import FileResponse, Http404, HttpResponse
from django.utils import timezone
from django.core.exceptions import PermissionDenied
from .models import Order
from apps.plans.models import Plan
from .emails import send_order_confirmation_email, send_payment_instructions_email
from .forms import ReceiptUploadForm
from apps.notifications.services import notify_admin_new_order
import mimetypes
import logging

logger = logging.getLogger('orders')


class CheckoutView(View):
    """
    Checkout page for purchasing a plan.
    Shows manual payment instructions (Payoneer and Bank Transfer).
    """
    template_name = 'orders/checkout.html'
    
    def get(self, request, plan_slug):
        """Display checkout page with payment instructions."""
        plan = get_object_or_404(Plan.objects.visible(), slug=plan_slug)
        
        # Check if plan has a price
        if not plan.price or plan.price <= 0:
            messages.error(request, "This plan is not available for purchase.")
            return redirect('plans:plan_detail', slug=plan_slug)
        
        # Payment details
        payment_info = {
            'payoneer': {
                'email': 'bacseried@gmail.com',
                'holder': 'Issoufou Abdou Chéfou',
            },
            'bank': {
                'name': 'Bank of Africa Niger',
                'holder': 'Abdou Chefou Issoufou',
                'currency': 'XOF',
                'swift': 'AFRINENIXXX',
                'iban': 'NE58NE0380100400440716000006',
            }
        }
        
        form = ReceiptUploadForm()
        
        context = {
            'plan': plan,
            'payment_info': payment_info,
            'form': form,
        }
        return render(request, self.template_name, context)
    
    def post(self, request, plan_slug):
        """Process receipt upload and create order."""
        plan = get_object_or_404(Plan.objects.visible(), slug=plan_slug)
        
        form = ReceiptUploadForm(request.POST, request.FILES)
        
        if form.is_valid():
            # Create order with receipt
            order = form.save(commit=False)
            order.plan = plan
            order.price_paid = plan.price
            order.currency = 'USD'
            order.payment_status = Order.PENDING
            order.payment_provider = Order.MANUAL
            order.save()
            
            # Send confirmation email to buyer
            send_order_confirmation_email(order)
            
            # Send notification to admin (with receipt attached)
            try:
                notify_admin_new_order(order)
                logger.info(f"Admin notified of new order: {order.order_number}")
            except Exception as e:
                logger.error(f"Failed to notify admin for order {order.order_number}: {e}")
            
            messages.success(
                request,
                f"Order {order.order_number} submitted! Your payment receipt is under review. "
                f"You'll receive an email once it's verified (usually within 24 hours)."
            )
            
            return redirect('orders:order_confirmation', order_number=order.order_number)
        else:
            # Show errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
            
            # Re-render with form errors
            payment_info = {
                'payoneer': {
                    'email': 'bacseried@gmail.com',
                    'holder': 'Issoufou Abdou Chéfou',
                },
                'bank': {
                    'name': 'Bank of Africa Niger',
                    'holder': 'Abdou Chefou Issoufou',
                    'currency': 'XOF',
                    'swift': 'AFRINENIXXX',
                    'iban': 'NE58NE0380100400440716000006',
                }
            }
            
            context = {
                'plan': plan,
                'payment_info': payment_info,
                'form': form,
            }
            return render(request, self.template_name, context)


class OrderConfirmationView(TemplateView):
    """
    Order confirmation page showing order details and payment status.
    """
    template_name = 'orders/order_confirmation.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order_number = self.kwargs.get('order_number')
        
        order = get_object_or_404(Order, order_number=order_number)
        context['order'] = order
        
        return context


class SecureDownloadView(View):
    """
    Secure download view that validates purchase before serving file.
    Prevents direct media URL access to paid plans.
    """
    
    def get(self, request, access_token):
        """Serve file if valid token and download allowed."""
        # Validate token
        try:
            order = Order.objects.select_related('plan').get(access_token=access_token)
        except Order.DoesNotExist:
            raise Http404("Invalid download link.")
        
        # Check if download is allowed
        if not order.can_download():
            context = {
                'order': order,
                'reason': self._get_denial_reason(order)
            }
            return render(request, 'orders/download_denied.html', context, status=403)
        
        # Get file path
        if not order.plan.paid_plan_file:
            raise Http404("Plan file not found.")
        
        file_path = order.plan.paid_plan_file.path
        
        # Increment download count
        order.increment_download()
        
        # Serve file
        try:
            response = FileResponse(
                open(file_path, 'rb'),
                content_type=mimetypes.guess_type(file_path)[0] or 'application/pdf'
            )
            response['Content-Disposition'] = f'attachment; filename="{order.plan.reference}-{order.plan.slug}.pdf"'
            return response
        except FileNotFoundError:
            raise Http404("Plan file not found on server.")
    
    def _get_denial_reason(self, order):
        """Get human-readable reason for download denial."""
        if order.payment_status != Order.COMPLETED:
            return f"Payment not completed. Status: {order.get_payment_status_display()}"
        
        if order.download_count >= order.max_downloads:
            return f"Download limit reached ({order.max_downloads} downloads maximum)."
        
        if order.is_expired:
            return f"Access expired on {order.access_expires_at.strftime('%B %d, %Y')}."
        
        return "Access denied."


class MyOrdersView(View):
    """
    Allow users to retrieve their orders by email (no account needed).
    """
    template_name = 'orders/my_orders.html'
    
    def get(self, request):
        """Display form to enter email."""
        return render(request, self.template_name)
    
    def post(self, request):
        """Show orders for provided email."""
        email = request.POST.get('email', '').strip()
        
        if not email:
            messages.error(request, "Please enter your email address.")
            return render(request, self.template_name)
        
        # Find orders for this email
        orders = Order.objects.filter(
            buyer_email=email
        ).select_related('plan').order_by('-created_at')
        
        if not orders.exists():
            messages.info(request, f"No orders found for {email}")
        
        context = {
            'email': email,
            'orders': orders,
        }
        return render(request, self.template_name, context)
