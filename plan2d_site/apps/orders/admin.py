"""
Admin configuration for Orders app.
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """
    Admin interface for managing orders with manual payment verification.
    """
    list_display = [
        'order_number',
        'buyer_email',
        'plan_link',
        'payment_method',
        'price_paid',
        'status_badge',
        'receipt_preview',
        'verified_status',
        'created_at',
    ]
    list_filter = [
        'payment_status',
        'payment_method',
        'payment_provider',
        'verified_at',
        'created_at',
    ]
    search_fields = [
        'order_number',
        'buyer_email',
        'buyer_name',
        'plan__title',
        'plan__reference',
        'payment_provider_id',
    ]
    readonly_fields = [
        'order_number',
        'access_token',
        'download_count',
        'created_at',
        'updated_at',
        'completed_at',
        'verified_at',
        'verified_by',
        'download_link',
        'receipt_image_preview',
    ]
    list_per_page = 50
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    fieldsets = (
        ('Order Information', {
            'fields': (
                'order_number',
                ('plan', 'price_paid', 'currency'),
            )
        }),
        ('Buyer Information', {
            'fields': (
                'buyer_email',
                'buyer_name',
            )
        }),
        ('Payment Details', {
            'fields': (
                'payment_status',
                'payment_method',
                ('payment_provider', 'payment_provider_id'),
                'completed_at',
            )
        }),
        ('Manual Payment Verification', {
            'fields': (
                'receipt_file',
                'receipt_image_preview',
                'verified_at',
                'verified_by',
                'admin_comment',
            ),
            'description': 'Receipt verification for manual payments'
        }),
        ('Access Control', {
            'fields': (
                'access_token',
                'download_link',
                ('download_count', 'max_downloads'),
                'access_expires_at',
            ),
            'description': 'Secure download settings and tracking'
        }),
        ('Admin Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': (
                'created_at',
                'updated_at',
            ),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['approve_payments', 'reject_payments', 'reset_download_count']
    
    def plan_link(self, obj):
        """Link to plan detail."""
        url = reverse('admin:plans_plan_change', args=[obj.plan.pk])
        return format_html('<a href="{}">{}</a>', url, obj.plan.title)
    plan_link.short_description = 'Plan'
    
    def receipt_preview(self, obj):
        """Small thumbnail of receipt in list view."""
        if obj.receipt_file:
            return format_html(
                '<a href="{}" target="_blank">📄 View</a>',
                obj.receipt_file.url
            )
        return '-'
    receipt_preview.short_description = 'Receipt'
    
    def receipt_image_preview(self, obj):
        """Full receipt preview in detail view."""
        if obj.receipt_file:
            if obj.receipt_file.name.lower().endswith('.pdf'):
                return format_html(
                    '<a href="{}" target="_blank" class="button">📄 Open PDF Receipt</a>',
                    obj.receipt_file.url
                )
            else:
                return format_html(
                    '<a href="{}" target="_blank">'
                    '<img src="{}" style="max-width: 600px; max-height: 400px; border: 1px solid #ddd;" />'
                    '</a><br><small>Click to open in new tab</small>',
                    obj.receipt_file.url, obj.receipt_file.url
                )
        return format_html('<em>No receipt uploaded</em>')
    receipt_image_preview.short_description = 'Receipt Preview'
    
    def verified_status(self, obj):
        """Show verification status."""
        if obj.verified_at:
            return format_html(
                '<span style="color: green;">✓ {}</span>',
                obj.verified_at.strftime('%Y-%m-%d')
            )
        return format_html('<span style="color: orange;">⏳ Pending</span>')
    verified_status.short_description = 'Verified'
    
    def status_badge(self, obj):
        """Visual badge for payment status."""
        colors = {
            Order.PENDING: '#ffc107',  # yellow
            Order.PROCESSING: '#17a2b8',  # blue
            Order.COMPLETED: '#28a745',  # green
            Order.FAILED: '#dc3545',  # red
            Order.REJECTED: '#dc3545',  # red
            Order.REFUNDED: '#6c757d',  # gray
        }
        color = colors.get(obj.payment_status, '#6c757d')
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 11px; font-weight: bold;">{}</span>',
            color, obj.get_payment_status_display().upper()
        )
    status_badge.short_description = 'Status'
    
    def download_status(self, obj):
        """Show download usage."""
        percentage = (obj.download_count / obj.max_downloads) * 100 if obj.max_downloads > 0 else 0
        
        if obj.download_count >= obj.max_downloads:
            color = 'red'
        elif percentage >= 80:
            color = 'orange'
        else:
            color = 'green'
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}/{}</span>',
            color, obj.download_count, obj.max_downloads
        )
    download_status.short_description = 'Downloads'
    
    def download_link(self, obj):
        """Display the secure download URL."""
        if obj.access_token:
            url = f"/download/{obj.access_token}/"
            return format_html(
                '<a href="{}" target="_blank">🔗 Download Link</a><br>'
                '<small style="color: gray;">{}</small>',
                url, url
            )
        return '-'
    download_link.short_description = 'Download URL'
    
    # Bulk Actions
    
    def approve_payments(self, request, queryset):
        """Approve manual payments and grant download access."""
        updated = 0
        for order in queryset.filter(payment_status=Order.PENDING):
            order.approve_payment(
                admin_user=request.user,
                comment=f"Approved by {request.user.username} via bulk action"
            )
            updated += 1
        
        self.message_user(request, f'{updated} payment(s) approved. Customers notified via email.')
    approve_payments.short_description = '✓ Approve selected payments'
    
    def reject_payments(self, request, queryset):
        """Reject manual payments with reason."""
        updated = 0
        for order in queryset.filter(payment_status=Order.PENDING):
            order.reject_payment(
                admin_user=request.user,
                comment="Payment receipt did not match. Please resubmit with correct details."
            )
            updated += 1
        
        self.message_user(
            request, 
            f'{updated} payment(s) rejected. Customers notified via email.',
            level='warning'
        )
    reject_payments.short_description = '✗ Reject selected payments'
    
    def mark_as_completed(self, request, queryset):
        """Mark selected orders as completed."""
        updated = 0
        for order in queryset:
            if order.payment_status != Order.COMPLETED:
                order.mark_completed()
                updated += 1
        
        self.message_user(request, f'{updated} order(s) marked as completed.')
    mark_as_completed.short_description = 'Mark as Completed'
    
    def mark_as_failed(self, request, queryset):
        """Mark selected orders as failed."""
        updated = queryset.update(payment_status=Order.FAILED)
        self.message_user(request, f'{updated} order(s) marked as failed.')
    mark_as_failed.short_description = 'Mark as Failed'
    
    def reset_download_count(self, request, queryset):
        """Reset download counter for selected orders."""
        updated = queryset.update(download_count=0)
        self.message_user(request, f'Download count reset for {updated} order(s).')
    reset_download_count.short_description = 'Reset Download Count'
