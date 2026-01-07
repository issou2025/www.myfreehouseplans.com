"""
Admin interface for notification logs.
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import EmailLog


@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    """
    Admin interface for viewing email notification logs.
    Read-only - used for debugging and audit purposes.
    """
    list_display = [
        'status_badge',
        'category',
        'short_subject',
        'to_email',
        'has_file',
        'created_at',
        'sent_at',
    ]
    list_filter = [
        'status',
        'category',
        'has_attachment',
        'created_at',
    ]
    search_fields = [
        'to_email',
        'subject',
        'error_message',
    ]
    readonly_fields = [
        'to_email',
        'from_email',
        'subject',
        'category',
        'status',
        'error_message',
        'has_attachment',
        'attachment_name',
        'related_contact_id',
        'related_order_id',
        'created_at',
        'sent_at',
    ]
    fieldsets = (
        ('Email Details', {
            'fields': ('subject', 'to_email', 'from_email', 'category')
        }),
        ('Status', {
            'fields': ('status', 'error_message', 'created_at', 'sent_at')
        }),
        ('Attachment', {
            'fields': ('has_attachment', 'attachment_name'),
            'classes': ('collapse',)
        }),
        ('Related Objects', {
            'fields': ('related_contact_id', 'related_order_id'),
            'classes': ('collapse',),
            'description': 'IDs of related contact messages or orders'
        }),
    )
    list_per_page = 50
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    def status_badge(self, obj):
        """Display status with color-coded badge."""
        colors = {
            'sent': '#28a745',      # Green
            'failed': '#dc3545',    # Red
            'pending': '#ffc107',   # Yellow
        }
        icons = {
            'sent': '✓',
            'failed': '✗',
            'pending': '⏳',
        }
        color = colors.get(obj.status, '#6c757d')
        icon = icons.get(obj.status, '?')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} {}</span>',
            color, icon, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'
    
    def short_subject(self, obj):
        """Truncate subject for list view."""
        if len(obj.subject) > 50:
            return obj.subject[:47] + '...'
        return obj.subject
    short_subject.short_description = 'Subject'
    
    def has_file(self, obj):
        """Show if email had attachment."""
        if obj.has_attachment:
            return format_html(
                '<span title="{}" style="color: green;">📎 Yes</span>',
                obj.attachment_name
            )
        return format_html('<span style="color: gray;">-</span>')
    has_file.short_description = 'File'
    
    def has_add_permission(self, request):
        """Disable manual log creation."""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Disable editing logs."""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Allow deleting old logs for cleanup."""
        return True
