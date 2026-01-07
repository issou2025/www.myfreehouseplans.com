from __future__ import annotations

from django.conf import settings


def brand(request):
    site_base_url = getattr(settings, "SITE_BASE_URL", "").rstrip("/")

    return {
        "brand_name": getattr(settings, "BRAND_NAME", "FreeHousePlan"),
        "brand_domain": getattr(settings, "BRAND_DOMAIN", "FreeHousePlan.com"),
        "brand_tagline": getattr(
            settings,
            "BRAND_TAGLINE",
            "Free house plans. Upgrade when you're ready to build.",
        ),
        "site_base_url": site_base_url,
        "support_email": getattr(settings, "SUPPORT_EMAIL", "support@freehouseplan.com"),
    }
