from django.contrib import admin
from django.utils.html import format_html
from .models import ContactMessage


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    """
    Admin interface for viewing and managing contact messages.
    """
    list_display = [
        'full_name', 
        'email', 
        'subject_display', 
        'has_file', 
        'created_at', 
        'is_read',
        'quick_reply'
    ]
    list_filter = ['subject', 'is_read', 'created_at']
    search_fields = ['full_name', 'email', 'message']
    readonly_fields = [
        'full_name', 
        'email', 
        'subject', 
        'message', 
        'attachment', 
        'created_at', 
        'ip_address', 
        'user_agent',
        'attachment_preview'
    ]
    fieldsets = (
        ('Contact Information', {
            'fields': ('full_name', 'email', 'subject')
        }),
        ('Message', {
            'fields': ('message',)
        }),
        ('Attachment', {
            'fields': ('attachment', 'attachment_preview'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'ip_address', 'user_agent'),
            'classes': ('collapse',)
        }),
        ('Admin Actions', {
            'fields': ('is_read', 'admin_notes')
        }),
    )
    list_per_page = 25
    date_hierarchy = 'created_at'
    
    def subject_display(self, obj):
        """Display subject with icon."""
        icons = {
            'general': '💬',
            'plans': '📐',
            'purchase': '💳',
            'technical': '🔧',
            'other': '📋'
        }
        icon = icons.get(obj.subject, '📋')
        return f"{icon} {obj.get_subject_display()}"
    subject_display.short_description = 'Subject'
    
    def has_file(self, obj):
        """Show if message has attachment."""
        if obj.has_attachment:
            return format_html(
                '<span style="color: green;">{}</span>',
                '✓ Yes'
            )
        return format_html(
            '<span style="color: gray;">{}</span>',
            '✗ No'
        )
    has_file.short_description = 'File'
    
    def attachment_preview(self, obj):
        """Show attachment with download link."""
        if obj.has_attachment:
            return format_html(
                '<a href="{}" target="_blank" class="button">📎 Download: {}</a>',
                obj.attachment.url,
                obj.attachment_filename
            )
        return 'No attachment'
    attachment_preview.short_description = 'Attachment'
    
    def quick_reply(self, obj):
        """Provide mailto link for quick reply."""
        return format_html(
            '<a href="mailto:{}?subject=Re: {}" class="button">✉️ Reply</a>',
            obj.email,
            obj.get_subject_display()
        )
    quick_reply.short_description = 'Actions'
    
    def has_add_permission(self, request):
        """Disable adding contact messages through admin."""
        return False
    
    actions = ['mark_as_read', 'mark_as_unread']
    
    @admin.action(description='Mark selected messages as read')
    def mark_as_read(self, request, queryset):
        updated = queryset.update(is_read=True)
        self.message_user(request, f'{updated} message(s) marked as read.')
    
    @admin.action(description='Mark selected messages as unread')
    def mark_as_unread(self, request, queryset):
        updated = queryset.update(is_read=False)
        self.message_user(request, f'{updated} message(s) marked as unread.')
