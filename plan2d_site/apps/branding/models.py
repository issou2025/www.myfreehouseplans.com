"""
Branding & Presentation models for managing site visuals.
Allows admin to control logos and presentation slider images.
"""
from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.utils.text import slugify
from django.contrib.auth import get_user_model
import os
from PIL import Image

User = get_user_model()


class SliderManager(models.Manager):
    """Custom manager for presentation slides."""
    
    def active(self):
        """Get all non-deleted slides."""
        return self.get_queryset().filter(is_deleted=False)
    
    def visible(self):
        """Get slides that should be displayed on frontend."""
        return self.get_queryset().filter(is_active=True, is_deleted=False).order_by('display_order')


def logo_upload_path(instance, filename):
    """Generate upload path for logos."""
    ext = os.path.splitext(filename)[1]
    safe_name = slugify(instance.logo_type)
    return f'branding/logos/{safe_name}{ext}'


def slider_upload_path(instance, filename):
    """Generate upload path for slider images."""
    ext = os.path.splitext(filename)[1]
    base_name = slugify(instance.title or 'slider')
    return f'presentation/slider/{base_name}_{instance.id or "new"}{ext}'


class LogoType(models.TextChoices):
    """Available logo types."""
    MAIN = 'main_logo', 'Main Logo (Header)'
    FOOTER = 'footer_logo', 'Footer Logo'
    FAVICON = 'favicon', 'Favicon'


class Logo(models.Model):
    """
    Website logo management.
    Only one active logo per type allowed.
    """
    logo_type = models.CharField(
        max_length=20,
        choices=LogoType.choices,
        unique=True,
        help_text="Type of logo (only one per type)"
    )
    image = models.ImageField(
        upload_to=logo_upload_path,
        validators=[FileExtensionValidator(['svg', 'png', 'webp', 'jpg', 'jpeg'])],
        help_text="Upload logo (SVG, PNG, WEBP, JPG)"
    )
    alt_text = models.CharField(
        max_length=200,
        default="Site Logo",
        help_text="Alternative text for accessibility"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Set as active logo"
    )
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='uploaded_logos'
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Logo"
        verbose_name_plural = "Logos"
        ordering = ['logo_type']

    def __str__(self):
        return f"{self.get_logo_type_display()} {'(Active)' if self.is_active else '(Inactive)'}"

    def clean(self):
        """Validate image dimensions and file size."""
        if self.image:
            # Check file size (max 5MB)
            if self.image.size > 5 * 1024 * 1024:
                raise ValidationError("Logo file size must be less than 5MB")

            # Validate image can be opened
            try:
                img = Image.open(self.image)
                img.verify()
                
                # Check dimensions for favicon
                if self.logo_type == LogoType.FAVICON:
                    if img.size[0] > 512 or img.size[1] > 512:
                        raise ValidationError("Favicon dimensions should not exceed 512x512 pixels")
            except Exception as e:
                raise ValidationError(f"Invalid image file: {str(e)}")

    def save(self, *args, **kwargs):
        # If setting as active, deactivate other logos of same type
        if self.is_active:
            Logo.objects.filter(logo_type=self.logo_type).exclude(pk=self.pk).update(is_active=False)
        
        super().save(*args, **kwargs)

    @classmethod
    def get_active_logo(cls, logo_type):
        """Get the active logo for a specific type."""
        try:
            return cls.objects.get(logo_type=logo_type, is_active=True)
        except cls.DoesNotExist:
            return None


class PresentationSlider(models.Model):
    """
    Presentation slider images for homepage/plans pages.
    Admin can control order, visibility, and content.
    """
    # Custom manager
    objects = SliderManager()
    
    title = models.CharField(
        max_length=200,
        blank=True,
        help_text="Optional title overlay"
    )
    short_description = models.TextField(
        max_length=500,
        blank=True,
        help_text="Optional short description"
    )
    image = models.ImageField(
        upload_to='presentation/slider/',
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'webp'])],
        help_text="Upload slider image (JPG, PNG, WEBP)"
    )
    link_url = models.URLField(
        blank=True,
        help_text="Optional link when image is clicked"
    )
    display_order = models.IntegerField(
        default=0,
        help_text="Lower numbers appear first"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Display this slide on the website"
    )
    is_deleted = models.BooleanField(
        default=False,
        help_text="Soft delete flag"
    )
    
    # Audit fields
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_slides'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Presentation Slide"
        verbose_name_plural = "Presentation Slider"
        ordering = ['display_order', '-created_at']

    def __str__(self):
        status = "Active" if self.is_active else "Inactive"
        return f"{self.title or f'Slide {self.id}'} ({status})"

    def clean(self):
        """Validate image dimensions and file size."""
        if self.image:
            # Check file size (max 10MB)
            if self.image.size > 10 * 1024 * 1024:
                raise ValidationError("Image file size must be less than 10MB")

            # Validate image dimensions
            try:
                img = Image.open(self.image)
                img.verify()
                
                # Recommend minimum dimensions for quality
                if img.size[0] < 800:
                    raise ValidationError("Image width should be at least 800px for quality display")
            except Exception as e:
                raise ValidationError(f"Invalid image file: {str(e)}")

    @property
    def is_visible(self):
        """Check if slide should be displayed on frontend."""
        return self.is_active and not self.is_deleted

    def soft_delete(self):
        """Soft delete the slide."""
        self.is_deleted = True
        self.is_active = False
        self.save()

    def restore(self):
        """Restore soft-deleted slide."""
        self.is_deleted = False
        self.save()
