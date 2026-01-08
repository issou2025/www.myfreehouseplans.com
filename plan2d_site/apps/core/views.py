from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.contrib import messages
from django.http import HttpResponse
from django.views import View
from django.conf import settings
from django.db.models import Min
from django.db.utils import ProgrammingError
from .forms import ContactMessageForm
from apps.notifications.services import notify_admin_new_contact
from apps.plans.models import Plan
import logging

logger = logging.getLogger('core')


class HomeView(TemplateView):
    """
    Homepage showcasing the platform and its key features.
    """
    template_name = 'core/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            visible_plans = (
                Plan.objects.visible()
                .select_related('category')
                .prefetch_related('images')
                .order_by('-featured', '-created_at')
            )

            featured = list(visible_plans.filter(featured=True)[:6])

            if len(featured) < 6:
                needed = 6 - len(featured)
                fallback = list(
                    visible_plans.exclude(pk__in=[plan.pk for plan in featured])[:needed]
                )
                featured.extend(fallback)

                if fallback:
                    logger.info(
                        "HomeView: supplementing featured plans with %s fallback plan(s) to keep the showcase visible",
                        len(fallback)
                    )

            context['featured_plans'] = featured

            pack2_min_price = (
                visible_plans.filter(price__gt=0)
                .exclude(pack_2_gumroad_zip_url='')
                .aggregate(value=Min('price'))
                .get('value')
            )
            pack3_min_price = (
                visible_plans.filter(pack_3_price__gt=0)
                .exclude(pack_3_gumroad_zip_url='')
                .aggregate(value=Min('pack_3_price'))
                .get('value')
            )

            context['pack2_min_price'] = pack2_min_price
            context['pack3_min_price'] = pack3_min_price
        except ProgrammingError:
            # Fail-safe: homepage must render even if DB tables are not created yet.
            context['featured_plans'] = []
            context['pack2_min_price'] = None
            context['pack3_min_price'] = None
            logger.warning("HomeView: database tables missing; rendering empty homepage showcase")
        return context


class AboutView(TemplateView):
    """
    About page explaining the mission and approach of the brand.
    """
    template_name = 'core/about.html'


class FAQView(TemplateView):
    """
    FAQ page with common questions and answers.
    """
    template_name = 'core/faq.html'


class ContactView(TemplateView):
    """
    Contact page with form for user inquiries with file upload support.
    """
    template_name = 'core/contact.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ContactMessageForm()
        context['admin_whatsapp'] = settings.ADMIN_WHATSAPP
        return context

    def post(self, request, *args, **kwargs):
        """
        Handle contact form submission with file attachment.
        """
        form = ContactMessageForm(request.POST, request.FILES)
        
        if form.is_valid():
            # Save the contact message
            contact_msg = form.save(commit=False)
            
            # Add metadata
            contact_msg.ip_address = self.get_client_ip(request)
            contact_msg.user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]
            contact_msg.save()
            
            # Send email notification to admin using centralized service
            notification_sent = notify_admin_new_contact(contact_msg)
            
            if notification_sent:
                logger.info(f"Admin notified of new contact message from {contact_msg.email}")
                messages.success(
                    request,
                    f'Thank you, {contact_msg.full_name}! Your message has been sent successfully. '
                    f'We will get back to you at {contact_msg.email} within 24-48 hours.'
                )
            else:
                # Message saved even if email notification failed
                logger.warning(f"Admin notification failed for contact from {contact_msg.email}")
                messages.warning(
                    request,
                    f'Your message has been saved, but there was an issue sending the notification. '
                    f'You can also reach us on WhatsApp: {settings.ADMIN_WHATSAPP}'
                )
            
            return redirect('core:contact')
        else:
            # Form has errors
            messages.error(request, 'Please correct the errors below.')
            context = self.get_context_data(**kwargs)
            context['form'] = form
            return self.render_to_response(context)
    
    def get_client_ip(self, request):
        """
        Get client IP address from request.
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class RobotsView(View):
    """
    Robots.txt file for SEO and crawler control.
    """
    def get(self, request):
        lines = [
            "User-agent: *",
            "Allow: /",
            "Disallow: /admin/",
            "Disallow: /media/paid-plans/",  # Protect paid plan files
            "",
            f"Sitemap: {request.build_absolute_uri('/sitemap.xml')}",
        ]
        return HttpResponse("\n".join(lines), content_type="text/plain")
