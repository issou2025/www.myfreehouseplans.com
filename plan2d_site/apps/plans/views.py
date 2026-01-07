import hashlib
import logging
import random
import secrets
from decimal import Decimal, InvalidOperation
from urllib.parse import urlencode

from django.http import Http404, HttpResponsePermanentRedirect, HttpResponse
from django.template.loader import render_to_string
from django.utils import timezone
from django.views.generic import ListView, DetailView
from django.db.models import Q, F, Case, When, IntegerField

from .models import Plan, Category, PlanSlugHistory

logger = logging.getLogger('plans')

try:  # Optional dependency for PDF generation
    from weasyprint import HTML
except ImportError:  # pragma: no cover - environment without WeasyPrint
    HTML = None


def _apply_language_content(plans, language_code):
    """Helper to mutate plan objects according to requested locale."""
    if not language_code:
        return plans
    for plan in plans:
        plan.apply_language(language_code)
    return plans


class PlanListView(ListView):
    """Public listing of all published house plans with search and filters."""
    model = Plan
    template_name = 'plans/plan_list.html'
    context_object_name = 'plans'
    paginate_by = 12

    def get_queryset(self):
        """Get only published plans, with optional filtering."""
        queryset = (
            Plan.objects.visible()
            .select_related('category', 'pack_configuration')
            .prefetch_related('images')
        )

        filters = self._get_filter_state()

        if filters['category']:
            queryset = queryset.filter(category__slug=filters['category'])

        if filters['search']:
            queryset = queryset.filter(
                Q(title__icontains=filters['search']) |
                Q(description__icontains=filters['search']) |
                Q(reference__icontains=filters['search'])
            )

        if filters['bedrooms']:
            queryset = queryset.filter(bedrooms=filters['bedrooms'])

        if filters['floors_value'] is not None:
            queryset = queryset.filter(floors=filters['floors_value'])

        if filters['plan_type']:
            queryset = queryset.filter(plan_type=filters['plan_type'])

        if filters['min_area_value'] is not None:
            queryset = queryset.filter(total_area_sqm__gte=filters['min_area_value'])

        if filters['max_area_value'] is not None:
            queryset = queryset.filter(total_area_sqm__lte=filters['max_area_value'])

        # Order is decided later via deterministic shuffle, so keep natural ordering for stability
        result = queryset.order_by('pk').distinct()
        
        # Visibility safeguard: log if filters hide too many plans
        total_visible = Plan.objects.visible().count()
        filtered_count = result.count()
        if filtered_count < total_visible:
            hidden_count = total_visible - filtered_count
            filters_applied = {
                'category': filters['category'],
                'search': filters['search'],
                'bedrooms': filters['bedrooms'],
                'floors': filters['floors'],
                'plan_type': filters['plan_type'],
                'min_area': filters['min_area_value'],
                'max_area': filters['max_area_value'],
            }
            active_filters = {k: v for k, v in filters_applied.items() if v}
            logger.info(
                f"Plan filtering: {filtered_count}/{total_visible} plans shown. "
                f"{hidden_count} plans hidden by filters: {active_filters}"
            )
        
        return result

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add categories for filtering
        context['categories'] = Category.objects.filter(is_active=True)

        filters = self._get_filter_state()
        
        # Add current filters for display
        context['current_category'] = filters['category']
        context['current_search'] = filters['search']
        context['current_bedrooms'] = filters['bedrooms']
        context['current_floors'] = filters['floors']
        context['current_plan_type'] = filters['plan_type']
        context['current_min_area'] = filters['min_area_input']
        context['current_max_area'] = filters['max_area_input']
        context['active_filters'] = filters['active_filters']
        context['has_active_filters'] = filters['has_user_filters']
        context['plan_type_choices'] = Plan.PLAN_TYPE_CHOICES
        context['filters_querystring'] = self._build_querystring()
        
        # Visibility monitoring: track total visible plans vs displayed
        total_visible = Plan.objects.visible().count()
        paginator = context.get('paginator')
        if paginator:
            displayed_count = paginator.count
        else:
            plans = context['plans']
            displayed_count = len(plans.object_list if hasattr(plans, 'object_list') else plans)
        context['total_visible_plans'] = total_visible
        context['displayed_plans_count'] = displayed_count
        context['is_filtered'] = filters['has_user_filters']
        
        # Featured plans for potential sidebar/top section
        featured = self._get_featured_plans()
        context['featured_plans'] = featured

        language_code = getattr(self.request, 'LANGUAGE_CODE', None)
        plans_object = context['plans']
        if hasattr(plans_object, 'object_list'):
            plan_list = list(plans_object.object_list)
        else:
            plan_list = list(plans_object)
            context['plans'] = plan_list

        _apply_language_content(plan_list, language_code)
        _apply_language_content(context['featured_plans'], language_code)

        context['plan_quality_alerts'] = self._collect_plan_quality_alerts(plan_list)
        
        return context
    def paginate_queryset(self, queryset, page_size):
        randomized_ids = self._get_randomized_plan_ids(queryset)
        randomized_ids = self._dedupe_preserve_order(randomized_ids)
        pagination = super().paginate_queryset(randomized_ids, page_size)

        if pagination is None:
            return pagination

        paginator, page, id_page, is_paginated = pagination
        ordered_ids = list(id_page)
        adjusted_ids = self._prepare_page_ids(
            ordered_ids,
            randomized_ids,
            page.number,
            page_size,
        )
        plans_for_page = self._fetch_plans_for_page(queryset, adjusted_ids)
        page.object_list = plans_for_page
        return paginator, page, plans_for_page, is_paginated

    def _get_randomized_plan_ids(self, queryset):
        plan_ids = list(queryset.values_list('pk', flat=True))
        if len(plan_ids) <= 1:
            return plan_ids

        signature = self._build_shuffle_signature(len(plan_ids))
        return self._shuffle_plan_ids(plan_ids, signature)

    def _fetch_plans_for_page(self, base_queryset, ordered_ids):
        if not ordered_ids:
            return []

        preserved_order = Case(
            *[When(pk=pk, then=position) for position, pk in enumerate(ordered_ids)],
            output_field=IntegerField(),
        )
        return list(
            base_queryset.filter(pk__in=ordered_ids).order_by(preserved_order)
        )

    def _dedupe_preserve_order(self, items):
        seen = set()
        result = []
        for value in items:
            if value in seen:
                continue
            seen.add(value)
            result.append(value)
        return result

    def _prepare_page_ids(self, page_ids, all_ids, page_number, page_size):
        target_chunk = len(page_ids)
        if target_chunk == 0:
            return page_ids

        restricted_ids = set()
        if self._should_hide_featured_in_grid(page_number):
            restricted_ids = {plan.id for plan in self._get_featured_plans()}

        filtered = []
        seen = set()

        def append_if_allowed(pk):
            if pk in seen or pk in restricted_ids:
                return False
            seen.add(pk)
            filtered.append(pk)
            return True

        for pk in page_ids:
            append_if_allowed(pk)

        if len(filtered) == target_chunk:
            return filtered

        slice_start = (page_number - 1) * page_size + target_chunk
        next_index = slice_start
        total_ids = len(all_ids)

        while len(filtered) < target_chunk and next_index < total_ids:
            pk = all_ids[next_index]
            next_index += 1
            append_if_allowed(pk)

        return filtered

    def _shuffle_plan_ids(self, plan_ids, signature):
        seed_bytes = hashlib.blake2s(signature.encode('utf-8'), digest_size=16).digest()
        seed_int = int.from_bytes(seed_bytes, 'big')
        rng = random.Random(seed_int)
        shuffled = plan_ids[:]
        rng.shuffle(shuffled)
        return shuffled

    def _build_shuffle_signature(self, total_count):
        filter_signature = self.request.META.get('QUERY_STRING', '')
        return f"{self._build_shuffle_seed()}|count:{total_count}|{filter_signature}"

    def _build_shuffle_seed(self):
        """Mix session and calendar seeds to keep order stable per visit but fresh daily."""
        session = getattr(self.request, 'session', None)
        today_token = timezone.now().strftime('%Y%m%d')
        session_seed_key = 'plans.shuffle.token'
        session_day_key = 'plans.shuffle.day'

        if session is None:
            return f"day:{today_token}"

        token = session.get(session_seed_key)
        stored_day = session.get(session_day_key)
        if not token or stored_day != today_token:
            token = secrets.token_hex(16)
            session[session_seed_key] = token
            session[session_day_key] = today_token
            session.modified = True

        return f"{token}:{today_token}"

    def _collect_plan_quality_alerts(self, plans):
        """Surface visibility or quality regressions without hiding plans."""
        alerts = []
        for plan in plans:
            primary_image = plan.get_primary_image()
            if not primary_image:
                alerts.append({
                    'plan_id': plan.id,
                    'reference': plan.reference,
                    'issue': 'missing_primary_image'
                })
                continue

            if not plan.has_high_resolution_primary():
                width = getattr(primary_image.image, 'width', None) or 0
                height = getattr(primary_image.image, 'height', None) or 0
                alerts.append({
                    'plan_id': plan.id,
                    'reference': plan.reference,
                    'issue': 'low_resolution_primary_image',
                    'width': width,
                    'height': height,
                    'min_width': Plan.HIGH_RES_MIN_WIDTH,
                    'min_height': Plan.HIGH_RES_MIN_HEIGHT,
                })

        if alerts:
            logger.warning("Plan quality alerts detected", extra={'plan_quality_alerts': alerts})

        return alerts

    def _get_featured_plans(self):
        if hasattr(self, '_featured_plans_cache'):
            return self._featured_plans_cache

        featured = list(
            Plan.objects.visible()
            .select_related('category', 'pack_configuration')
            .filter(featured=True)[:3]
        )
        self._featured_plans_cache = featured
        return featured

    def _should_hide_featured_in_grid(self, page_number):
        if page_number != 1:
            return False
        filters = self._get_filter_state()
        if filters['has_user_filters']:
            return False
        return bool(self._get_featured_plans())

    def _get_filter_state(self):
        if hasattr(self, '_filter_state'):
            return self._filter_state

        query = self.request.GET
        category = query.get('category', '').strip()
        category_label = ''
        if category:
            category_label = Category.objects.filter(slug=category).values_list('name', flat=True).first() or category

        search_query = query.get('q', '').strip()

        bedrooms = query.get('bedrooms', '').strip()
        if bedrooms and not bedrooms.isdigit():
            bedrooms = ''

        floors_raw = query.get('floors', '').strip()
        floors_value = None
        if floors_raw:
            try:
                floors_value = int(floors_raw)
            except (TypeError, ValueError):
                floors_raw = ''
                floors_value = None

        plan_type_raw = query.get('plan_type', '').strip()
        allowed_plan_types = {choice[0] for choice in Plan.PLAN_TYPE_CHOICES}
        plan_type = plan_type_raw if plan_type_raw in allowed_plan_types else ''
        plan_type_label = dict(Plan.PLAN_TYPE_CHOICES).get(plan_type, '')

        min_area_input = query.get('min_area', '').strip()
        max_area_input = query.get('max_area', '').strip()
        min_area_value = self._parse_decimal(min_area_input)
        max_area_value = self._parse_decimal(max_area_input)

        if min_area_value is not None and max_area_value is not None and min_area_value > max_area_value:
            min_area_value, max_area_value = max_area_value, min_area_value
            min_area_input, max_area_input = max_area_input, min_area_input

        state = {
            'category': category,
            'category_label': category_label,
            'search': search_query,
            'bedrooms': bedrooms,
            'floors': floors_raw,
            'floors_value': floors_value,
            'plan_type': plan_type,
            'plan_type_label': plan_type_label,
            'min_area_input': min_area_input,
            'max_area_input': max_area_input,
            'min_area_value': min_area_value,
            'max_area_value': max_area_value,
        }

        state['active_filters'] = self._build_active_filters(state)
        state['has_user_filters'] = bool(state['active_filters'])

        self._filter_state = state
        return state

    def _build_active_filters(self, state):
        summaries = []
        if state['category'] and state['category_label']:
            summaries.append(f"Category · {state['category_label']}")
        if state['search']:
            summaries.append(f"Search · {state['search']}")
        if state['bedrooms']:
            bedroom_label = f"{state['bedrooms']}+ bedrooms" if state['bedrooms'] == '8' else f"{state['bedrooms']} bedrooms"
            summaries.append(bedroom_label)
        if state['floors_value'] is not None:
            floor_value = state['floors_value']
            floor_label = f"{floor_value} floor" if floor_value == 1 else f"{floor_value} floors"
            summaries.append(floor_label)
        if state['plan_type']:
            summaries.append(f"Use · {state['plan_type_label']}")

        area_label = self._compose_area_label(state['min_area_value'], state['max_area_value'])
        if area_label:
            summaries.append(area_label)

        return summaries

    def _compose_area_label(self, min_area, max_area):
        if min_area is None and max_area is None:
            return ''
        if min_area is not None and max_area is not None:
            return f"{self._format_decimal(min_area)}–{self._format_decimal(max_area)} m²"
        if min_area is not None:
            return f"≥ {self._format_decimal(min_area)} m²"
        return f"≤ {self._format_decimal(max_area)} m²"

    @staticmethod
    def _format_decimal(value):
        if value is None:
            return ''
        text = format(value, 'f').rstrip('0').rstrip('.')
        return text or '0'

    @staticmethod
    def _parse_decimal(value):
        if not value:
            return None
        try:
            decimal_value = Decimal(value)
        except (InvalidOperation, TypeError):
            return None
        return decimal_value if decimal_value >= 0 else None

    def _build_querystring(self):
        querydict = self.request.GET.copy()
        querydict.pop('page', None)
        params = [(key, value) for key, value in querydict.items() if value]
        return urlencode(params)


class PlanDetailView(DetailView):
    """Detailed view of a single house plan including PDF export."""
    model = Plan
    template_name = 'plans/plan_detail.html'
    context_object_name = 'plan'
    
    def get_queryset(self):
        """Only show visible (published + not deleted) plans to public."""
        return (
            Plan.objects.visible()
            .select_related('category', 'pack_configuration')
            .prefetch_related('images')
        )
    
    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
        except Http404:
            slug = kwargs.get('slug')
            history = (
                PlanSlugHistory.objects.select_related('plan')
                .filter(slug=slug)
                .first()
            )
            if history and history.plan.is_visible:
                return HttpResponsePermanentRedirect(history.plan.get_absolute_url())
            raise

        if request.GET.get('format') == 'pdf':
            return self._render_plan_pdf(self.object)

        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def get_object(self):
        """Get plan by slug, apply localization, and increment view count."""
        plan = super().get_object()

        Plan.objects.filter(pk=plan.pk).update(views_count=plan.views_count + 1)
        plan.apply_language(getattr(self.request, 'LANGUAGE_CODE', None))

        return plan
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add related plans from same category
        context['related_plans'] = (
            Plan.objects.visible()
            .select_related('category', 'pack_configuration')
            .filter(category=self.object.category)
            .exclude(pk=self.object.pk)[:4]
        )
        
        # Get primary image or first image
        primary = self.object.get_primary_image()
        gallery_images = self.object.get_gallery_images()
        context['primary_image'] = primary
        context['gallery_images'] = gallery_images

        # Optional visual support (keep plans primary)
        lookup_images = ([primary] if primary else []) + gallery_images
        context['render_3d_image'] = next((img for img in lookup_images if img.image_type == '3d_render'), None)
        floor_plan_image = next((img for img in lookup_images if img.image_type == 'floor_plan'), None)
        context['floor_plan_image'] = floor_plan_image or primary

        _apply_language_content(context['related_plans'], getattr(self.request, 'LANGUAGE_CODE', None))
        context['plan_pdf_ready'] = self._pdf_generation_ready()
        context['pdf_download_url'] = f"{self.request.path}?format=pdf"
        context['pdf_generation_message'] = (
            "Server PDF renderer missing (install WeasyPrint)"
            if not context['plan_pdf_ready'] else ''
        )
        
        return context

    def _pdf_generation_ready(self):
        return HTML is not None

    def _render_plan_pdf(self, plan):
        if not self._pdf_generation_ready():
            return HttpResponse(
                "PDF export is not configured on this server.",
                status=503,
                content_type='text/plain'
            )

        context = self._build_pdf_context(plan)
        html = render_to_string('plans/plan_pdf.html', context, request=self.request)
        pdf_bytes = HTML(string=html, base_url=self.request.build_absolute_uri('/')).write_pdf()
        Plan.objects.filter(pk=plan.pk).update(downloads_count=F('downloads_count') + 1)
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename={plan.slug}-plan-sheet.pdf'
        return response

    def _build_pdf_context(self, plan):
        primary_image = plan.get_primary_image()
        primary_image_url = ''
        if primary_image and getattr(primary_image, 'image', None):
            primary_image_url = self.request.build_absolute_uri(primary_image.image.url)

        return {
            'plan': plan,
            'brand_domain': getattr(self.request, 'brand_domain', self.request.get_host()),
            'primary_image_url': primary_image_url,
            'generated_on': timezone.now(),
            'highlights': self._build_plan_highlights(plan),
        }

    def _build_plan_highlights(self, plan):
        highlights = []
        if plan.bedrooms:
            highlights.append(f"{plan.bedrooms} bedroom layout")
        if plan.bathrooms:
            highlights.append(f"{self._format_decimal_value(plan.bathrooms)} bathroom fit")
        if plan.floors:
            floor_label = 'floor' if plan.floors == 1 else 'floors'
            highlights.append(f"{plan.floors} {floor_label}")
        if plan.total_area_sqm:
            highlights.append(f"{self._format_decimal_value(plan.total_area_sqm)} m² total area")
        if plan.plan_type:
            highlights.append(plan.get_plan_type_display())
        if plan.plot_type:
            highlights.append(f"Plot: {plan.plot_type}")
        return highlights

    @staticmethod
    def _format_decimal_value(value):
        if value is None:
            return ''
        text = format(value, 'f').rstrip('0').rstrip('.')
        return text or '0'
