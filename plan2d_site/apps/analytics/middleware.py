from __future__ import annotations

from django.conf import settings
from django.core.cache import cache

from .models import Visit
from .utils import detect_device_type, get_country_code_from_request, get_client_ip, hash_request_fingerprint


class VisitTrackingMiddleware:
    """Privacy-respecting analytics.

    Stores only: URL path, country code, device type, timestamp.
    Does NOT store IP address, cookies, names, emails, or identifiers.

    To avoid excessive writes, it throttles repeat hits from the same
    fingerprint to the same path within a short window.
    """

    EXCLUDED_PREFIXES = (
        "/admin",
        settings.STATIC_URL or "/static/",
        settings.MEDIA_URL or "/media/",
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if not getattr(settings, "ANALYTICS_ENABLED", True):
            return response

        if request.method != "GET":
            return response

        # Only record successful-ish responses.
        if getattr(response, "status_code", 200) >= 400:
            return response

        path = request.path or "/"
        if any(path.startswith(prefix) for prefix in self.EXCLUDED_PREFIXES):
            return response

        # Skip obvious non-page URLs.
        if path in ("/favicon.ico", "/robots.txt"):
            return response

        throttle_seconds = int(getattr(settings, "ANALYTICS_THROTTLE_SECONDS", 60))

        user_agent = request.META.get("HTTP_USER_AGENT", "")
        ip = get_client_ip(request)
        fingerprint = hash_request_fingerprint(ip, user_agent)
        cache_key = f"visit:{fingerprint}:{path}"

        if throttle_seconds > 0 and cache.get(cache_key):
            return response

        if throttle_seconds > 0:
            cache.set(cache_key, True, timeout=throttle_seconds)

        try:
            Visit.objects.create(
                url=path,
                country_code=get_country_code_from_request(request),
                device_type=detect_device_type(user_agent),
            )
        except Exception:
            # Never block page rendering due to analytics.
            return response

        return response
