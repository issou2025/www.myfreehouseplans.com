"""
Admin configuration for SEO app
"""
from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from .models import SEOMetadata, Redirect


class SEOMetadataInline(GenericTabularInline):
    """
    Inline admin for SEO metadata (can be attached to any model).
    """
    model = SEOMetadata
    extra = 0
    fields = (
        'meta_title', 'meta_description', 'meta_keywords',
        'canonical_url', 'index', 'follow'
    )
    classes = ('collapse',)


@admin.register(SEOMetadata)
class SEOMetadataAdmin(admin.ModelAdmin):
    """
    Admin for managing SEO metadata directly.
    """
    list_display = ('content_object', 'meta_title', 'index', 'follow', 'created_at')
    list_filter = ('index', 'follow', 'schema_type', 'created_at')
    search_fields = ('meta_title', 'meta_description', 'meta_keywords')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Content', {
            'fields': ('content_type', 'object_id')
        }),
        ('Basic Meta Tags', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords')
        }),
        ('Technical SEO', {
            'fields': ('canonical_url', 'index', 'follow')
        }),
        ('Open Graph', {
            'fields': ('og_title', 'og_description', 'og_image'),
            'classes': ('collapse',)
        }),
        ('Schema.org', {
            'fields': ('schema_type',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Redirect)
class RedirectAdmin(admin.ModelAdmin):
    """
    Admin for managing URL redirects (301/302).
    """
    list_display = ('old_path', 'new_path', 'redirect_type', 'is_active', 'created_at')
    list_filter = ('redirect_type', 'is_active', 'created_at')
    search_fields = ('old_path', 'new_path')
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Redirect Configuration', {
            'fields': ('old_path', 'new_path', 'redirect_type', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['activate_redirects', 'deactivate_redirects']

    def activate_redirects(self, request, queryset):
        """Bulk action to activate redirects"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} redirect(s) activated.')
    activate_redirects.short_description = 'Activate selected redirects'

    def deactivate_redirects(self, request, queryset):
        """Bulk action to deactivate redirects"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} redirect(s) deactivated.')
    deactivate_redirects.short_description = 'Deactivate selected redirects'
