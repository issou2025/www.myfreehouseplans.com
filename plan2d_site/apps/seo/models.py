from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class SEOMetadata(models.Model):
    """
    SEO metadata that can be attached to any model (Plan, Page, etc.).
    Stores custom meta titles, descriptions, and other SEO data.
    """
    # Generic relation to attach to any model
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # SEO Fields
    meta_title = models.CharField(
        max_length=60,
        blank=True,
        help_text="SEO title (60 chars max for Google). Leave empty to use default."
    )
    meta_description = models.CharField(
        max_length=160,
        blank=True,
        help_text="SEO description (160 chars max). Leave empty to use default."
    )
    meta_keywords = models.CharField(
        max_length=255,
        blank=True,
        help_text="Comma-separated keywords (optional, less important for modern SEO)"
    )
    canonical_url = models.URLField(
        blank=True,
        help_text="Canonical URL if different from default"
    )
    
    # Open Graph / Social Media
    og_title = models.CharField(max_length=100, blank=True, help_text="Title for social media sharing")
    og_description = models.CharField(max_length=200, blank=True, help_text="Description for social media")
    og_image = models.ImageField(upload_to='seo/og_images/', blank=True, null=True, help_text="Social media preview image")
    
    # Indexing Control
    index = models.BooleanField(default=True, help_text="Allow search engines to index this page")
    follow = models.BooleanField(default=True, help_text="Allow search engines to follow links")
    
    # Structured Data
    schema_type = models.CharField(
        max_length=50,
        blank=True,
        help_text="Schema.org type (e.g., Product, Article)"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "SEO Metadata"
        verbose_name_plural = "SEO Metadata"
        unique_together = ['content_type', 'object_id']
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
        ]
    
    def __str__(self):
        return f"SEO for {self.content_object}"
    
    @property
    def robots_content(self):
        """Generate robots meta tag content."""
        index = 'index' if self.index else 'noindex'
        follow = 'follow' if self.follow else 'nofollow'
        return f"{index}, {follow}"


class Redirect(models.Model):
    """
    301/302 redirects for SEO and URL management.
    """
    old_path = models.CharField(
        max_length=255,
        unique=True,
        help_text="Old URL path (e.g., /old-page/)"
    )
    new_path = models.CharField(
        max_length=255,
        help_text="New URL path or full URL"
    )
    redirect_type = models.CharField(
        max_length=3,
        choices=[
            ('301', 'Permanent (301)'),
            ('302', 'Temporary (302)'),
        ],
        default='301'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Redirect"
        verbose_name_plural = "Redirects"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.old_path} -> {self.new_path} ({self.redirect_type})"
