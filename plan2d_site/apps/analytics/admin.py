from django.contrib import admin
from django.db.models import Count

from .models import Visit


@admin.register(Visit)
class VisitAdmin(admin.ModelAdmin):
    date_hierarchy = "created_at"
    list_display = ("created_at", "country_code", "device_type", "url")
    list_filter = ("country_code", "device_type", "created_at")
    search_fields = ("url",)
    ordering = ("-created_at",)
    change_list_template = "admin/analytics/visit/change_list.html"

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}

        qs = Visit.objects.all()

        total_visits = qs.count()
        device_counts = {row["device_type"]: row["visits"] for row in qs.values("device_type").annotate(visits=Count("id"))}
        mobile_visits = int(device_counts.get(Visit.DeviceType.MOBILE, 0))
        desktop_visits = int(device_counts.get(Visit.DeviceType.DESKTOP, 0))
        total_device = mobile_visits + desktop_visits

        if total_device:
            mobile_pct = round((mobile_visits / total_device) * 100)
            desktop_pct = 100 - mobile_pct
        else:
            mobile_pct = 0
            desktop_pct = 0

        countries = list(
            qs.values("country_code")
            .annotate(visits=Count("id"))
            .order_by("-visits")
        )
        top_countries = countries[:5]

        top_pages_by_country = []
        for row in top_countries:
            code = row["country_code"]
            pages = list(
                qs.filter(country_code=code)
                .values("url")
                .annotate(visits=Count("id"))
                .order_by("-visits")[:5]
            )
            top_pages_by_country.append({"country_code": code, "pages": pages})

        extra_context.update(
            {
                "analytics_total_visits": total_visits,
                "analytics_mobile_visits": mobile_visits,
                "analytics_desktop_visits": desktop_visits,
                "analytics_mobile_pct": mobile_pct,
                "analytics_desktop_pct": desktop_pct,
                "analytics_countries": countries,
                "analytics_top_countries": top_countries,
                "analytics_top_pages_by_country": top_pages_by_country,
            }
        )

        return super().changelist_view(request, extra_context=extra_context)
