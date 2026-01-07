"""
Sitemaps for SEO
"""
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from apps.plans.models import Plan


class PlanSitemap(Sitemap):
    """Sitemap for published house plans"""
    changefreq = "weekly"
    priority = 0.9
    protocol = 'https'

    def items(self):
        return Plan.objects.visible().select_related('category')

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return reverse('plans:detail', args=[obj.slug])


class StaticViewSitemap(Sitemap):
    """Sitemap for static pages"""
    priority = 0.8
    changefreq = 'monthly'
    protocol = 'https'

    def items(self):
        return ['core:home', 'core:about', 'core:faq', 'core:contact', 'plans:plan_list']

    def location(self, item):
        return reverse(item)


class CategorySitemap(Sitemap):
    """Sitemap for plan categories"""
    changefreq = "weekly"
    priority = 0.7
    protocol = 'https'

    def items(self):
        from apps.plans.models import Category
        return Category.objects.filter(is_active=True)

    def location(self, obj):
        return reverse('plans:plan_list') + f'?category={obj.slug}'
