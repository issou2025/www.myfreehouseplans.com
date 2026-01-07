"""
Admin interface for Branding & Presentation management.
Clean, professional interface with image previews and ordering.
"""
from django.contrib import admin
from django.utils.html import format_html
from django.db import models
from django.forms import Textarea
from .models import Logo, PresentationSlider, LogoType
import logging

logger = logging.getLogger('branding')


@admin.register(Logo)
class LogoAdmin(admin.ModelAdmin):
    """Admin interface for logo management."""
    
    list_display = ['logo_type_display', 'preview', 'is_active', 'uploaded_at', 'uploaded_by']
    list_filter = ['logo_type', 'is_active', 'uploaded_at']
    readonly_fields = ['preview_large', 'uploaded_by', 'uploaded_at', 'updated_at']
    
    fieldsets = (
        ('Logo Information', {
            'fields': ('logo_type', 'image', 'preview_large', 'alt_text', 'is_active')
        }),
        ('Metadata', {
            'fields': ('uploaded_by', 'uploaded_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def logo_type_display(self, obj):
        """Display logo type with icon."""
        icons = {
            LogoType.MAIN: '🏠',
            LogoType.FOOTER: '📄',
            LogoType.FAVICON: '⭐',
        }
        icon = icons.get(obj.logo_type, '🖼️')
        return f"{icon} {obj.get_logo_type_display()}"
    logo_type_display.short_description = "Logo Type"
    
    def preview(self, obj):
        """Small preview in list view."""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 40px; max-width: 100px; object-fit: contain;"/>',
                obj.image.url
            )
        return "No image"
    preview.short_description = "Preview"
    
    def preview_large(self, obj):
        """Large preview in edit view."""
        if obj.image:
            return format_html(
                '<div style="background: #f0f0f0; padding: 20px; border-radius: 8px; display: inline-block;">'
                '<img src="{}" style="max-height: 200px; max-width: 400px; object-fit: contain;"/>'
                '<p style="margin-top: 10px; color: #666;">Current logo</p>'
                '</div>',
                obj.image.url
            )
        return "No image uploaded yet"
    preview_large.short_description = "Current Logo"
    
    def save_model(self, request, obj, form, change):
        """Track who uploaded the logo."""
        if not change:  # New logo
            obj.uploaded_by = request.user
            logger.info(f"New logo uploaded: {obj.logo_type} by {request.user.username}")
        else:
            logger.info(f"Logo updated: {obj.logo_type} by {request.user.username}")
        
        super().save_model(request, obj, form, change)
    
    def has_delete_permission(self, request, obj=None):
        """Restrict deletion to superusers."""
        return request.user.is_superuser


@admin.register(PresentationSlider)
class PresentationSliderAdmin(admin.ModelAdmin):
    """Admin interface for presentation slider management."""
    
    list_display = [
        'order_indicator', 
        'preview', 
        'title_display', 
        'status_indicator', 
        'display_order', 
        'created_at'
    ]
    list_filter = ['is_active', 'is_deleted', 'created_at']
    list_editable = ['display_order']
    search_fields = ['title', 'short_description']
    readonly_fields = ['preview_large', 'created_by', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Slide Content', {
            'fields': ('title', 'short_description', 'image', 'preview_large', 'link_url')
        }),
        ('Display Settings', {
            'fields': ('display_order', 'is_active'),
            'description': 'Control when and where this slide appears'
        }),
        ('Metadata', {
            'fields': ('is_deleted', 'created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 3, 'cols': 60})},
    }
    
    actions = ['activate_slides', 'deactivate_slides', 'soft_delete_slides', 'restore_slides']
    
    def order_indicator(self, obj):
        """Visual indicator of slide order."""
        return f"#{obj.display_order}"
    order_indicator.short_description = "Order"
    
    def preview(self, obj):
        """Small preview in list view."""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 60px; max-width: 120px; object-fit: cover; border-radius: 4px;"/>',
                obj.image.url
            )
        return "No image"
    preview.short_description = "Preview"
    
    def preview_large(self, obj):
        """Large preview in edit view."""
        if obj.image:
            return format_html(
                '<div style="background: #f0f0f0; padding: 20px; border-radius: 8px; display: inline-block;">'
                '<img src="{}" style="max-height: 300px; max-width: 600px; object-fit: contain; border-radius: 8px;"/>'
                '<p style="margin-top: 10px; color: #666;">Current slide image</p>'
                '</div>',
                obj.image.url
            )
        return "No image uploaded yet"
    preview_large.short_description = "Current Image"
    
    def title_display(self, obj):
        """Display title with fallback."""
        if obj.title:
            return obj.title
        return format_html('<em style="color: #999;">Untitled Slide #{}</em>', obj.id)
    title_display.short_description = "Title"
    
    def status_indicator(self, obj):
        """Visual status indicator."""
        if obj.is_deleted:
            return format_html(
                '<span style="background: #dc3545; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">🗑️ DELETED</span>'
            )
        elif obj.is_active:
            return format_html(
                '<span style="background: #28a745; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">✓ ACTIVE</span>'
            )
        else:
            return format_html(
                '<span style="background: #6c757d; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">⊘ INACTIVE</span>'
            )
    status_indicator.short_description = "Status"
    
    def get_queryset(self, request):
        """Show all slides including deleted for transparency."""
        return super().get_queryset(request).select_related('created_by')
    
    def save_model(self, request, obj, form, change):
        """Track who created the slide."""
        if not change:  # New slide
            obj.created_by = request.user
            logger.info(f"New slide created: '{obj.title}' by {request.user.username}")
        else:
            logger.info(f"Slide updated: '{obj.title}' by {request.user.username}")
        
        super().save_model(request, obj, form, change)
    
    # Custom actions
    def activate_slides(self, request, queryset):
        """Activate selected slides."""
        count = queryset.update(is_active=True)
        self.message_user(request, f"Activated {count} slide(s)")
        logger.info(f"Bulk activated {count} slides by {request.user.username}")
    activate_slides.short_description = "✓ Activate selected slides"
    
    def deactivate_slides(self, request, queryset):
        """Deactivate selected slides."""
        count = queryset.update(is_active=False)
        self.message_user(request, f"Deactivated {count} slide(s)")
        logger.info(f"Bulk deactivated {count} slides by {request.user.username}")
    deactivate_slides.short_description = "⊘ Deactivate selected slides"
    
    def soft_delete_slides(self, request, queryset):
        """Soft delete selected slides."""
        count = queryset.update(is_deleted=True, is_active=False)
        self.message_user(request, f"Soft deleted {count} slide(s)")
        logger.warning(f"Bulk soft deleted {count} slides by {request.user.username}")
    soft_delete_slides.short_description = "🗑️ Soft delete selected slides"
    
    def restore_slides(self, request, queryset):
        """Restore soft-deleted slides."""
        count = queryset.filter(is_deleted=True).update(is_deleted=False)
        self.message_user(request, f"Restored {count} slide(s)")
        logger.info(f"Bulk restored {count} slides by {request.user.username}")
    restore_slides.short_description = "♻️ Restore deleted slides"
    
    def has_delete_permission(self, request, obj=None):
        """Restrict hard deletion to superusers."""
        return request.user.is_superuser


# Customize admin site header
admin.site.site_header = "Plan2D Site Administration"
admin.site.site_title = "Plan2D Admin"
admin.site.index_title = "Welcome to Plan2D Administration"
