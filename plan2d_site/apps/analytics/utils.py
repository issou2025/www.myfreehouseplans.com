import hashlib
from typing import Optional

from django.conf import settings


_MOBILE_UA_MARKERS = (
    "mobi",
    "android",
    "iphone",
    "ipad",
    "ipod",
    "windows phone",
    "blackberry",
    "opera mini",
)


def detect_device_type(user_agent: str) -> str:
    ua = (user_agent or "").lower()
    if any(marker in ua for marker in _MOBILE_UA_MARKERS):
        return "mobile"
    return "desktop"


def get_client_ip(request) -> Optional[str]:
    # Prefer proxy headers when present; fall back to REMOTE_ADDR.
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        # XFF can contain multiple IPs: client, proxy1, proxy2...
        ip = xff.split(",")[0].strip()
        return ip or None

    x_real_ip = request.META.get("HTTP_X_REAL_IP")
    if x_real_ip:
        return x_real_ip.strip() or None

    return request.META.get("REMOTE_ADDR")


def hash_request_fingerprint(ip: Optional[str], user_agent: str) -> str:
    # Used only for throttling/deduping in cache. Never stored in DB.
    raw = f"{settings.SECRET_KEY}|{ip or ''}|{user_agent or ''}".encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def get_country_code_from_request(request) -> str:
    # If you deploy behind a proxy/CDN that provides country code headers,
    # we use them to avoid doing GeoIP lookups.
    header_candidates = (
        request.META.get("HTTP_CF_IPCOUNTRY"),  # Cloudflare
        request.META.get("HTTP_X_COUNTRY_CODE"),
        request.META.get("HTTP_X_COUNTRY"),
    )
    for value in header_candidates:
        if value and len(value) == 2 and value.isalpha():
            return value.upper()

    # Optional GeoIP2 support (no hard dependency).
    geoip_path = getattr(settings, "GEOIP_PATH", None)
    if geoip_path:
        try:
            from django.contrib.gis.geoip2 import GeoIP2  # type: ignore

            ip = get_client_ip(request)
            if not ip:
                return "UN"

            g = GeoIP2(path=geoip_path)
            code = g.country_code(ip)
            if code and len(code) == 2:
                return code.upper()
        except Exception:
            return "UN"

    return "UN"
