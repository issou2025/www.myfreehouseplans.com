"""
Context processor to make branding assets available in all templates.
Provides logos and slider images without hardcoding paths.
"""
from django.db.utils import ProgrammingError

from .models import Logo, LogoType, PresentationSlider


def branding_context(request):
    """
    Add branding assets to template context.
    Makes logos and slider images available globally.
    """
    try:
        return {
            'site_logo': Logo.get_active_logo(LogoType.MAIN),
            'footer_logo': Logo.get_active_logo(LogoType.FOOTER),
            'favicon': Logo.get_active_logo(LogoType.FAVICON),
        }
    except ProgrammingError:
        # Fail-safe: if branding tables are not migrated yet, render without assets.
        return {
            'site_logo': None,
            'footer_logo': None,
            'favicon': None,
        }


def slider_context(request):
    """
    Add visible slider images to template context.
    Only includes active, non-deleted slides in display order.
    """
    try:
        # Limit to 10 slides
        return {
            'slider_images': list(PresentationSlider.objects.visible()[:10])
        }
    except ProgrammingError:
        return {
            'slider_images': []
        }
