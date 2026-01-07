"""
Context processor to make branding assets available in all templates.
Provides logos and slider images without hardcoding paths.
"""
from .models import Logo, LogoType, PresentationSlider


def branding_context(request):
    """
    Add branding assets to template context.
    Makes logos and slider images available globally.
    """
    return {
        'site_logo': Logo.get_active_logo(LogoType.MAIN),
        'footer_logo': Logo.get_active_logo(LogoType.FOOTER),
        'favicon': Logo.get_active_logo(LogoType.FAVICON),
    }


def slider_context(request):
    """
    Add visible slider images to template context.
    Only includes active, non-deleted slides in display order.
    """
    return {
        'slider_images': PresentationSlider.objects.visible()[:10]  # Limit to 10 slides
    }
