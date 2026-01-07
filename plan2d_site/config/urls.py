"""
URL configuration for plan2d_site project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.contrib.sitemaps.views import sitemap
from apps.seo.sitemaps import PlanSitemap, StaticViewSitemap, CategorySitemap
from apps.orders.views import SecureDownloadView
from django.views.i18n import set_language

# Sitemap configuration
sitemaps = {
    'plans': PlanSitemap,
    'static': StaticViewSitemap,
    'categories': CategorySitemap,
}

# Language-independent URLs
urlpatterns = [
    path('admin/', admin.site.urls),
    path('i18n/setlang/', set_language, name='set_language'),
    path('download/<str:access_token>/', SecureDownloadView.as_view(), name='secure_download'),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
]

# Language-dependent URLs (content pages)
urlpatterns += i18n_patterns(
    path('', include('apps.core.urls')),
    path('plans/', include('apps.plans.urls')),
    path('orders/', include('apps.orders.urls')),
    prefix_default_language=False,  # Don't add /en/ prefix for English
)

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
