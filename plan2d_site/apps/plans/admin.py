import json
from urllib.parse import quote, unquote

from django import forms
from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.utils.html import format_html, format_html_join

from .models import (
    Category,
    Plan,
    PlanAuditLog,
    PlanDeletionLog,
    PlanImage,
    PlanPackConfiguration,
    PlanPublishStatus,
    PlanSlugHistory,
)
from .utils import build_plot_size_conversion


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    Admin interface for managing plan categories.
    """
    list_display = ['name', 'slug', 'plan_count', 'display_order', 'is_active', 'updated_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['display_order', 'name']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description')
        }),
        ('Display Settings', {
            'fields': ('display_order', 'is_active')
        }),
    )

    def plan_count(self, obj):
        """Display number of plans in this category."""
        count = obj.plans.count()
        return format_html('<strong>{}</strong>', count)
    plan_count.short_description = 'Plans'


class PlanAdminForm(forms.ModelForm):
    """Expose localized content fields for EN / FR editing."""

    title_fr = forms.CharField(label="Title (FR)", required=False)
    description_fr = forms.CharField(label="Description (FR)", required=False, widget=forms.Textarea)
    seo_title_fr = forms.CharField(label="SEO Title (FR)", required=False)
    seo_description_fr = forms.CharField(label="SEO Description (FR)", required=False, widget=forms.Textarea)
    area_last_edited = forms.CharField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = Plan
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._plot_size_conversion = None
        fr_content = (self.instance.language_content or {}).get('fr', {}) if self.instance.pk else {}
        self.fields['title_fr'].initial = fr_content.get('title')
        self.fields['description_fr'].initial = fr_content.get('description')
        self.fields['seo_title_fr'].initial = fr_content.get('seo_title')
        self.fields['seo_description_fr'].initial = fr_content.get('seo_description')
        
        # Add help text for Gumroad fields
        if 'gumroad_url' in self.fields:
            self.fields['gumroad_url'].widget.attrs['placeholder'] = 'https://gumroad.com/l/your-product'
            self.fields['gumroad_url'].help_text = (
                'Enter the Gumroad checkout URL for this plan. '
                'Example: https://gumroad.com/l/your-product-code'
            )
        if 'gumroad_revit_url' in self.fields:
            self.fields['gumroad_revit_url'].widget.attrs['placeholder'] = 'https://gumroad.com/l/your-revit-file'
            self.fields['gumroad_revit_url'].help_text = (
                'Optional: link to the Gumroad product that delivers the editable Revit (.RVT) file. '
                'Customers complete checkout on Gumroad.'
            )
        if 'gumroad_ifc_url' in self.fields:
            self.fields['gumroad_ifc_url'].widget.attrs['placeholder'] = 'https://gumroad.com/l/your-ifc-file'
            self.fields['gumroad_ifc_url'].help_text = (
                'Optional: link to the Gumroad product that delivers the IFC file. '
                'No files are hosted locally.'
            )
        if 'gumroad_paid_pdf_url' in self.fields:
            self.fields['gumroad_paid_pdf_url'].widget.attrs['placeholder'] = 'https://gumroad.com/l/your-paid-pdf'
            self.fields['gumroad_paid_pdf_url'].help_text = (
                'Optional: dedicated Gumroad checkout link for the dimensioned PDF. '
                'Clear this field or disable the toggle to hide the paid PDF offer.'
            )
        if 'total_area_sqm' in self.fields:
            self.fields['total_area_sqm'].widget.attrs['placeholder'] = 'Enter total area in m²'
        if 'total_area_sqft' in self.fields:
            self.fields['total_area_sqft'].widget.attrs['placeholder'] = 'Or enter total area in ft²'
        if 'suggested_plot_size' in self.fields:
            self.fields['suggested_plot_size'].widget.attrs.setdefault('placeholder', 'e.g., 15 x 20')
            self.fields['suggested_plot_size'].help_text = (
                'Formats accepted: 15x20, 15 x 20, 15m x 20m (all in meters). '
                'Letters and spaces are optional; feet are computed automatically.'
            )
        for price_field, label in (
            ('price', 'the Standard Pack dimensioned PDF'),
            ('revit_price', 'the Revit (RVT) deliverable'),
            ('ifc_price', 'the IFC deliverable'),
            ('pack_3_price', 'Pack 3'),
        ):
            if price_field in self.fields:
                self.fields[price_field].widget.attrs.setdefault('placeholder', 'e.g., 249.00')
                self.fields[price_field].help_text = (
                    f"Set the USD price for {label}. "
                    'Leave blank only if this file is not offered.'
                )
        for zip_field in ('pack_2_gumroad_zip_url', 'pack_3_gumroad_zip_url'):
            if zip_field in self.fields:
                self.fields[zip_field].widget.attrs['placeholder'] = 'https://gumroad.com/l/your-pack-zip'
                self.fields[zip_field].help_text = (
                    'Enter the single Gumroad ZIP checkout URL. The ZIP must already include Metric and Imperial deliverables.'
                )

    def clean_gumroad_url(self):
        """Validate Gumroad URL format."""
        url = self.cleaned_data.get('gumroad_url', '').strip()
        if url:
            if not (url.startswith('https://gumroad.com/') or 
                    (url.startswith('https://') and '.gumroad.com/' in url)):
                raise forms.ValidationError(
                    'Please enter a valid Gumroad URL. '
                    'URL must start with https://gumroad.com/ or https://*.gumroad.com/'
                )
        return url

    def clean(self):
        """Cross-field validation for Gumroad payment configuration."""
        cleaned_data = super().clean()
        enable_gumroad = cleaned_data.get('enable_gumroad_payment', True)
        paid_pdf_available = cleaned_data.get('paid_pdf_available')
        pack2_zip = (cleaned_data.get('pack_2_gumroad_zip_url') or '').strip()
        pack3_zip = (cleaned_data.get('pack_3_gumroad_zip_url') or '').strip()
        pack3_price = cleaned_data.get('pack_3_price')
        
        cleaned_data['pack_2_gumroad_zip_url'] = pack2_zip
        cleaned_data['pack_3_gumroad_zip_url'] = pack3_zip

        if enable_gumroad and paid_pdf_available and not pack2_zip:
            self.add_error(
                'pack_2_gumroad_zip_url',
                'Add the single Gumroad ZIP checkout URL for Pack 2 (must include Metric + Imperial) or disable the paid PDF offer.'
            )

        # Pack 3 visibility rule: Pack 3 stays hidden until a positive price is set.
        # If a price is set, require the Pack 3 ZIP URL so the CTA can work.
        if pack3_price not in (None, ''):
            if pack3_price <= 0:
                self.add_error('pack_3_price', 'Pack 3 price must be above zero.')
            if enable_gumroad and not pack3_zip:
                self.add_error(
                    'pack_3_gumroad_zip_url',
                    'Add the Pack 3 Gumroad ZIP checkout URL (Metric + Imperial inside one ZIP) or clear the Pack 3 price to keep it hidden.'
                )

        # Pricing safety: require positive pricing for active paid packs
        self._validate_pricing_rule('price', paid_pdf_available, 'the Standard Pack (PDF)')
        self._validate_pricing_rule('revit_price', False, 'the Revit deliverable')
        self._validate_pricing_rule('ifc_price', False, 'the IFC deliverable')
        
        return cleaned_data

    def _validate_pricing_rule(self, field_name, is_active, label):
        if field_name not in self.cleaned_data:
            return
        value = self.cleaned_data.get(field_name)
        if value in ('', None):
            value = None
        if is_active:
            if value is None:
                self.add_error(field_name, f'Set a price for {label}.')
            elif value <= 0:
                self.add_error(field_name, f'{label} must be priced above zero.')
        elif value is not None and value <= 0:
            self.add_error(field_name, f'{label} must be priced above zero or left blank when not offered.')

    def clean_gumroad_revit_url(self):
        url = self.cleaned_data.get('gumroad_revit_url', '').strip()
        if url:
            if not (url.startswith('https://gumroad.com/') or 
                    (url.startswith('https://') and '.gumroad.com/' in url)):
                raise forms.ValidationError(
                    'Please enter a valid Gumroad URL. '
                    'URL must start with https://gumroad.com/ or https://*.gumroad.com/'
                )
        return url

    def clean_gumroad_ifc_url(self):
        url = self.cleaned_data.get('gumroad_ifc_url', '').strip()
        if url:
            if not (url.startswith('https://gumroad.com/') or 
                    (url.startswith('https://') and '.gumroad.com/' in url)):
                raise forms.ValidationError(
                    'Please enter a valid Gumroad URL. '
                    'URL must start with https://gumroad.com/ or https://*.gumroad.com/'
                )
        return url

    def clean_gumroad_paid_pdf_url(self):
        url = self.cleaned_data.get('gumroad_paid_pdf_url', '').strip()
        if url:
            if not (url.startswith('https://gumroad.com/') or 
                    (url.startswith('https://') and '.gumroad.com/' in url)):
                raise forms.ValidationError(
                    'Please enter a valid Gumroad URL. '
                    'URL must start with https://gumroad.com/ or https://*.gumroad.com/'
                )
        return url

    def clean_pack_2_gumroad_zip_url(self):
        return self._clean_zip_field('pack_2_gumroad_zip_url')

    def clean_pack_3_gumroad_zip_url(self):
        return self._clean_zip_field('pack_3_gumroad_zip_url')

    def _clean_zip_field(self, field_name):
        url = (self.cleaned_data.get(field_name) or '').strip()
        if url:
            if not (url.startswith('https://gumroad.com/') or (
                    url.startswith('https://') and '.gumroad.com/' in url)):
                raise forms.ValidationError(
                    'Gumroad ZIP URL must start with https://gumroad.com/ or https://*.gumroad.com/'
                )
        return url

    def clean_suggested_plot_size(self):
        value = (self.cleaned_data.get('suggested_plot_size') or '').strip()
        if not value:
            self._plot_size_conversion = None
            return ''
        conversion = build_plot_size_conversion(value)
        if conversion:
            self._plot_size_conversion = conversion
            return conversion.metric_label
        self._plot_size_conversion = None
        return value

    def save(self, commit=True):
        instance = super().save(commit=False)
        language_content = instance.language_content or {}
        fr_payload = {
            'title': self.cleaned_data.get('title_fr', '').strip(),
            'description': self.cleaned_data.get('description_fr', '').strip(),
            'seo_title': self.cleaned_data.get('seo_title_fr', '').strip(),
            'seo_description': self.cleaned_data.get('seo_description_fr', '').strip(),
        }
        fr_payload = {k: v for k, v in fr_payload.items() if v}
        if fr_payload:
            language_content['fr'] = fr_payload
        elif 'fr' in language_content:
            language_content.pop('fr')
        instance.language_content = language_content
        instance._area_last_edited = self.cleaned_data.get('area_last_edited')
        if commit:
            instance.save()
            self.save_m2m()
        return instance


class PlanPermanentDeleteForm(forms.Form):
    """Explicit confirmation form for irreversible deletions."""

    confirmation_value = forms.CharField(
        label="Type the plan reference to confirm",
        max_length=50,
        required=True,
        help_text="This action is permanent. Type the exact reference to continue."
    )
    reason = forms.CharField(
        label="Reason (optional)",
        required=False,
        widget=forms.Textarea(attrs={'rows': 3})
    )

    def __init__(self, *args, plan=None, **kwargs):
        self.plan = plan
        super().__init__(*args, **kwargs)
        if plan:
            self.fields['confirmation_value'].help_text = (
                f'Type "{plan.reference}" to confirm permanent deletion.'
            )

    def clean_confirmation_value(self):
        value = (self.cleaned_data.get('confirmation_value') or '').strip()
        if self.plan and value != self.plan.reference:
            raise forms.ValidationError('Confirmation value does not match the plan reference.')
        return value


class PlanImageInline(admin.TabularInline):
    """
    Inline admin for plan images - allows adding images directly in the plan admin.
    """
    model = PlanImage
    extra = 1
    fields = ['image', 'image_type', 'caption', 'display_order', 'is_primary']
    ordering = ['display_order', '-is_primary']


class PlanSlugHistoryInline(admin.TabularInline):
    model = PlanSlugHistory
    extra = 0
    can_delete = False
    fields = ['slug', 'changed_at']
    readonly_fields = ['slug', 'changed_at']
    ordering = ['-changed_at']


class PlanAuditLogInline(admin.TabularInline):
    model = PlanAuditLog
    extra = 0
    can_delete = False
    fields = ['performed_at', 'action', 'performed_by', 'notes']
    readonly_fields = ['performed_at', 'action', 'performed_by', 'notes']
    ordering = ['-performed_at']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('performed_by')


class PlanPackConfigurationInlineForm(forms.ModelForm):
    class Meta:
        model = PlanPackConfiguration
        fields = '__all__'

    def clean(self):
        return super().clean()


class PlanPackConfigurationInline(admin.StackedInline):
    form = PlanPackConfigurationInlineForm
    model = PlanPackConfiguration
    extra = 0
    max_num = 1
    can_delete = False
    fieldsets = (
        ('Pack 3 Messaging', {
            'fields': (
                'pro_pack_label',
                'pro_pack_summary',
                'pro_pack_notes',
            ),
            'description': 'Pack 3 visibility is controlled by the Pack 3 price on the plan (and requires a ZIP URL). Use these fields only to adjust the public-facing copy.'
        }),
    )

    def get_extra(self, request, obj=None, **kwargs):
        if obj and hasattr(obj, 'pack_configuration'):
            return 0
        return 1

    def has_add_permission(self, request, obj):
        if obj and hasattr(obj, 'pack_configuration'):
            return False
        return super().has_add_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    """Restricted superuser-only admin for full plan lifecycle control."""

    form = PlanAdminForm
    change_form_template = 'admin/plans/plan/change_form.html'
    list_display = [
        'reference',
        'title',
        'status_badge',
        'category',
        'bedrooms',
        'bathrooms',
        'total_area_display',
        'pricing_summary',
        'gumroad_status',
        'revit_status',
        'ifc_status',
        'pack2_delivery_status',
        'pack3_delivery_status',
        'files_status',
        'updated_at',
        'last_modified_by',
        'quick_actions',
    ]
    list_display_links = ('reference', 'title')
    list_filter = [
        # Boolean status filters
        'publish_status',
        'is_deleted',
        'featured',
        # Classification filters
        'category',
        'plan_type',
        # Numeric filters
        'bedrooms',
        'created_at',
    ]
    search_fields = ['title', 'reference', 'slug', 'description', 'engineer_notes']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = [
        'reference',
        'total_area_sqft',
        'suggested_plot_size_ft_display',
        'views_count',
        'downloads_count',
        'created_at',
        'updated_at',
        'publish_status',
        'published_at',
        'unpublished_at',
        'unpublished_by',
        'deleted_at',
        'deleted_by',
        'status_badge',
        'last_modified_by',
        'payment_status_display',
    ]
    list_per_page = 25
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    inlines = [PlanPackConfigurationInline, PlanImageInline, PlanSlugHistoryInline, PlanAuditLogInline]

    class Media:
        js = (
            'js/plan_plot_size_admin.js',
            'js/plan_pack_admin.js',
        )
        css = {
            'all': ('css/admin_plan_filter_sidebar.css',)
        }

    fieldsets = (
        ('Basic Information', {
            'fields': (
                ('title', 'slug'),
                ('reference', 'category'),
                'plan_type',
            )
        }),
        ('Specifications', {
            'fields': (
                ('bedrooms', 'bathrooms'),
                'floors',
                ('total_area_sqm', 'total_area_sqft'),
                ('suggested_plot_size', 'suggested_plot_size_ft_display'),
                ('roof_type', 'wall_system'),
            ),
            'description': 'Total area in square feet and the suggested plot size in feet update automatically from the metric values.'
        }),
        ('Architectural Dossier', {
            'fields': (
                'architect_design_notes',
                ('climate_suitability', 'plot_type'),
                ('budget_level', 'target_user'),
            ),
            'description': 'Public-facing architectural notes and suitability metadata.'
        }),
        ('Content', {
            'fields': ('description', 'engineer_notes')
        }),
        ('Localization (EN / FR)', {
            'fields': (
                'title_fr',
                'description_fr',
                'seo_title_fr',
                'seo_description_fr',
            ),
            'description': 'Optional French overrides. Leave blank to reuse English content.'
        }),
            (Plan.PACK_DISPLAY_LABELS['free'], {
                'fields': (
                    'free_plan_file',
                    'free_3d_image',
                    'free_3d_caption',
                ),
                'classes': ('pack-section', 'pack-section--free'),
                'description': 'Pack 1 preview is permanently free. No pricing fields exist here and no overrides are allowed.'
            }),
            (Plan.PACK_DISPLAY_LABELS['standard'], {
                'fields': (
                    'paid_pdf_available',
                    'price',
                    'pack_2_gumroad_zip_url',
                ),
                'classes': ('pack-section', 'pack-section--standard'),
                'description': 'Pack 2 pricing applies to both metric and imperial PDFs. Configure a single Gumroad ZIP checkout URL that already bundles Metric + Imperial deliverables.'
            }),
        ('Payment Configuration', {
            'fields': (
                'enable_gumroad_payment',
                'payment_status_display',
            ),
            'description': 'Paid packs use Gumroad ZIP checkout URLs. Keep Gumroad payments enabled to show Pack 2 / Pack 3 CTAs publicly.'
        }),
        (Plan.PACK_DISPLAY_LABELS['pro'], {
            'fields': (
                'pack_3_price',
                'pack_3_gumroad_zip_url',
            ),
            'classes': ('pack-section', 'pack-section--pro', 'pack-three-fields'),
            'description': 'Pack 3 stays hidden until a positive Pack 3 price is set. Configure a single Gumroad ZIP checkout URL that contains all formats (Revit/IFC/DWG) in both Metric + Imperial.'
        }),
        ('Pricing & Visibility', {
            'fields': (
                'featured',
                'status_badge',
                'publish_status',
                'published_at',
                'unpublished_at',
                'unpublished_by',
                'unpublished_reason',
                'is_deleted',
                'deleted_at',
                'deleted_by',
                'last_modified_by',
            ),
            'description': 'Use the admin actions to publish, unpublish, soft delete, restore, or hard delete plans.'
        }),
        ('SEO', {
            'fields': ('seo_title', 'seo_description', 'seo_keywords'),
            'classes': ('collapse',),
            'description': 'Custom SEO fields. Leave blank to use auto-generated values.'
        }),
        ('Statistics', {
            'fields': (
                ('views_count', 'downloads_count'),
                ('created_at', 'updated_at'),
            ),
            'classes': ('collapse',),
            'description': 'Read-only statistics and metadata.'
        }),
    )

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:plan_id>/publish/',
                self.admin_site.admin_view(self.publish_plan_view),
                name='plans_plan_publish'
            ),
            path(
                '<int:plan_id>/unpublish/',
                self.admin_site.admin_view(self.unpublish_plan_view),
                name='plans_plan_unpublish'
            ),
            path(
                '<int:plan_id>/restore/',
                self.admin_site.admin_view(self.restore_plan_view),
                name='plans_plan_restore'
            ),
            path(
                '<int:plan_id>/delete/permanent/',
                self.admin_site.admin_view(self.permanent_delete_view),
                name='plans_plan_permanent_delete'
            ),
        ]
        return custom_urls + urls

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        plan_instance = self.get_object(request, object_id) if object_id else None
        if request.method == 'POST' and '_cancel' in request.POST:
            self.message_user(request, 'Changes discarded. No updates applied.', level=messages.INFO)
            return redirect('admin:plans_plan_changelist')

        extra_context = extra_context or {}
        extra_context.update({
            'show_save': False,
            'show_save_and_continue': False,
            'show_save_and_add_another': False,
            'plan_changelist_url': reverse('admin:plans_plan_changelist'),
            'can_permanent_delete': bool(plan_instance and plan_instance.is_deleted),
            'permanent_delete_url': (
                reverse('admin:plans_plan_permanent_delete', args=[plan_instance.pk])
                if plan_instance and plan_instance.is_deleted else ''
            ),
            'plan_reference_value': plan_instance.reference if plan_instance else '',
        })
        return super().changeform_view(request, object_id, form_url, extra_context)

    def total_area_display(self, obj):
        """Display area in both metric and imperial."""
        if obj.total_area_sqm:
            return format_html(
                '{} m² <br><small>({} ft²)</small>',
                obj.total_area_sqm,
                round(obj.total_area_sqft, 1) if obj.total_area_sqft else '-'
            )
        return '-'
    total_area_display.short_description = 'Total Area'

    def suggested_plot_size_ft_display(self, obj):
        conversion = build_plot_size_conversion(getattr(obj, 'suggested_plot_size', '') if obj else '')
        display_value = conversion.imperial_label if conversion else '—'
        return format_html(
            '<span id="id_suggested_plot_size_ft_display" class="plot-size-ft-display" '
            'data-empty-label="—">{}</span>',
            display_value
        )
    suggested_plot_size_ft_display.short_description = 'Suggested plot size (ft)'

    def payment_status_display(self, obj):
        """Display Gumroad payment status with visual indicator and warnings."""
        if obj.has_paid_pdf_offer:
            return format_html(
                '<span style="color: #28a745; font-weight: bold;">'
                '<i class="bi bi-check-circle-fill"></i> {}</span>'
                '<br><small style="color: #6c757d;">{}</small>',
                'Paid PDF active',
                'Button visible on plan page'
            )
        elif obj.paid_pdf_available and obj.enable_gumroad_payment and not obj.gumroad_paid_pdf_url:
            return format_html(
                '<span style="color: #ffc107; font-weight: bold;">'
                '<i class="bi bi-pause-circle-fill"></i> {}</span>'
                '<br><small style="color: #6c757d;">{}</small>',
                'Link needed',
                'Add Gumroad paid PDF link or disable the toggle'
            )
        elif obj.paid_pdf_available and not obj.enable_gumroad_payment:
            return format_html(
                '<span style="color: #dc3545; font-weight: bold;">'
                '<i class="bi bi-exclamation-triangle-fill"></i> {}</span>'
                '<br><small style="color: #6c757d;">{}</small>',
                'Gumroad disabled',
                'Toggle Gumroad payments on to sell the paid PDF'
            )
        elif not obj.paid_pdf_available:
            return format_html(
                '<span style="color: #6c757d;">'
                '<i class="bi bi-eye-slash"></i> {}</span>'
                '<br><small>{}</small>',
                'Paid PDF hidden',
                'Free preview remains available'
            )
        else:
            return format_html(
                '<span style="color: #6c757d;">'
                '<i class="bi bi-x-circle"></i> {}</span>'
                '<br><small>{}</small>',
                'No paid PDF checkout',
                'Provide a Gumroad link to sell the dimensioned PDF'
            )
    payment_status_display.short_description = 'Payment Status'

    def gumroad_status(self, obj):
        """Quick visual indicator for Gumroad payment status in list view."""
        if obj.has_paid_pdf_offer:
            return format_html(
                '<span style="color: #28a745; font-weight: bold;">{}</span>',
                '✓ Gumroad'
            )
        elif obj.paid_pdf_available and obj.enable_gumroad_payment and not obj.gumroad_paid_pdf_url:
            return format_html(
                '<span style="color: #dc3545; font-weight: bold;">{}</span>',
                '⚠ Missing link'
            )
        elif obj.paid_pdf_available and not obj.enable_gumroad_payment:
            return format_html(
                '<span style="color: #ffc107;">{}</span>',
                '⏸ Gumroad off'
            )
        elif not obj.paid_pdf_available:
            return format_html(
                '<span style="color: #6c757d;">{}</span>',
                'Hidden'
            )
        else:
            return format_html(
                '<span style="color: #6c757d;">{}</span>',
                '—'
            )
    gumroad_status.short_description = 'Gumroad'

    def revit_status(self, obj):
        """Surface optional Revit add-on availability."""
        if obj.has_revit_offer:
            return format_html(
                '<span style="color: #0d6efd; font-weight: bold;">{}</span>',
                'RVT ready'
            )
        if obj.revit_available and not obj.gumroad_revit_url:
            return format_html(
                '<span style="color: #dc3545;">{}</span>',
                'Link needed'
            )
        return format_html('<span style="color: #6c757d;">{}</span>', '—')
    revit_status.short_description = 'Revit'

    def ifc_status(self, obj):
        """Surface optional IFC add-on availability."""
        if obj.has_ifc_offer:
            return format_html(
                '<span style="color: #0f766e; font-weight: bold;">{}</span>',
                'IFC ready'
            )
        if obj.ifc_available and not obj.gumroad_ifc_url:
            return format_html(
                '<span style="color: #dc3545;">{}</span>',
                'Link needed'
            )
        return format_html('<span style="color: #6c757d;">{}</span>', '—')
    ifc_status.short_description = 'IFC'

    def pack2_delivery_status(self, obj):
        return self._render_gumroad_zip_status(obj.pack_2_gumroad_zip_url, 'Pack 2 ZIP')
    pack2_delivery_status.short_description = 'Pack 2 ZIP'

    def pack3_delivery_status(self, obj):
        return self._render_gumroad_zip_status(obj.pack_3_gumroad_zip_url, 'Pack 3 ZIP')
    pack3_delivery_status.short_description = 'Pack 3 ZIP'

    def _render_gumroad_zip_status(self, url, label):
        if url:
            return format_html(
                '<span style="color:#16a34a;font-weight:600;">Configured</span><br>'
                '<small style="color:#0f172a;">{}</small>',
                url
            )
        return format_html('<span style="color:#9ca3af;">{}</span><br><small>{}</small>', 'Missing', 'Provide Gumroad ZIP URL')

    def status_badge(self, obj):
        """Visual badge reflecting publish / delete state."""
        if obj.is_deleted:
            color = '#DC2626'
            text = 'Deleted'
        elif obj.publish_status == PlanPublishStatus.DRAFT:
            color = '#4B5563'
            text = 'Draft'
        elif obj.publish_status == PlanPublishStatus.PUBLISHED:
            color = '#15803D' if obj.featured else '#2563EB'
            text = '★ Featured' if obj.featured else 'Published'
        else:
            color = '#6B7280'
            text = 'Unpublished'

        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 11px; font-weight: bold; letter-spacing: 0.05em;">{}</span>',
            color,
            text,
        )
    status_badge.short_description = 'Status'

    def files_status(self, obj):
        """Show which files are uploaded."""
        free_icon = '📄' if obj.has_free_plan else '○'
        paid_icon = '📄' if obj.has_paid_plan else '○'
        paid_flag = 'ON' if obj.paid_pdf_available else 'OFF'
        return format_html(
            'Free: {} &nbsp; Paid: {} ({})',
            free_icon, paid_icon, paid_flag
        )
    files_status.short_description = 'Files'

    def pricing_summary(self, obj):
        """Compact badges showing pricing readiness per deliverable."""
        def chip(text, bg):
            return format_html(
                '<span style="display:inline-block;padding:2px 10px;margin:0 6px 6px 0;'
                'border-radius:999px;font-size:11px;font-weight:600;color:#fff;background:{};">{}</span>',
                bg,
                text
            )

        def format_amount(value):
            return '${:,.2f}'.format(value)

        badges = [chip('Pack 1 · Free', '#0f766e')]

        def append_asset(label, is_active, price, color_active='#2563eb'):
            if not is_active:
                badges.append(chip(f'{label}: hidden', '#9ca3af'))
            elif price:
                badges.append(chip(f'{label}: {format_amount(price)}', color_active))
            else:
                badges.append(chip(f'{label}: price needed', '#b91c1c'))

        append_asset('PDF', obj.paid_pdf_available, obj.price)
        append_asset('RVT', obj.revit_available, obj.revit_price, '#0ea5e9')
        append_asset('IFC', obj.ifc_available, obj.ifc_price, '#0891b2')
        pack_config = getattr(obj, 'pack_configuration', None)
        dwg_price = getattr(pack_config, 'dwg_price', None) if pack_config else None
        has_dwg = bool(pack_config and getattr(pack_config.dwg_file, 'name', ''))
        append_asset('DWG', has_dwg, dwg_price, '#7c3aed')

        return format_html(''.join(['{}'] * len(badges)), *badges)
    pricing_summary.short_description = 'Pricing'

    def quick_actions(self, obj):
        """Inline action buttons with clear labels and colors."""
        changelist_url = reverse('admin:plans_plan_changelist')
        encoded_next = quote(changelist_url)
        buttons = []

        if obj.is_deleted:
            buttons.append(self._action_button(
                label='Restore',
                color='#0F766E',
                url=f"{reverse('admin:plans_plan_restore', args=[obj.pk])}?next={encoded_next}"
            ))
            buttons.append(self._action_button(
                label='Delete permanently',
                color='#7f1d1d',
                url=reverse('admin:plans_plan_permanent_delete', args=[obj.pk])
            ))
        else:
            if obj.publish_status in (PlanPublishStatus.DRAFT, PlanPublishStatus.UNPUBLISHED):
                buttons.append(self._action_button(
                    label='Publish',
                    color='#15803D',
                    url=f"{reverse('admin:plans_plan_publish', args=[obj.pk])}?next={encoded_next}"
                ))
            if obj.publish_status == PlanPublishStatus.PUBLISHED:
                buttons.append(self._action_button(
                    label='Unpublish',
                    color='#EA580C',
                    url=f"{reverse('admin:plans_plan_unpublish', args=[obj.pk])}?next={encoded_next}"
                ))
            buttons.append(self._action_button(
                label='Soft delete',
                color='#B91C1C',
                url=reverse('admin:plans_plan_delete', args=[obj.pk])
            ))

        buttons.append(self._action_button(
            label='Edit',
            color='#1D4ED8',
            url=reverse('admin:plans_plan_change', args=[obj.pk])
        ))

        if not buttons:
            return '—'

        return format_html(
            '<div class="plan-admin-actions">{}</div>',
            format_html_join('', '{}', ((button,) for button in buttons))
        )
    quick_actions.short_description = 'Actions'

    def _action_button(self, label, color, url):
        style = (
            'display:inline-flex;align-items:center;justify-content:center;'
            'margin:0 6px 6px 0;padding:6px 14px;border-radius:6px;'
            'font-weight:600;font-size:12px;text-decoration:none;color:#fff;'
            f'background:{color};border:1px solid {color};min-width:96px;'
        )
        return format_html('<a href="{}" style="{}">{}</a>', url, style, label)

    def _plan_files_preview(self, plan):
        files = []
        if plan.free_plan_file:
            files.append({'label': 'Free preview PDF', 'path': plan.free_plan_file.name})
            watermarked = plan._watermarked_free_plan_name()
            if watermarked:
                files.append({'label': 'Watermarked free PDF copy', 'path': watermarked})
        if plan.paid_plan_file:
            files.append({'label': 'Paid PDF (dimensioned)', 'path': plan.paid_plan_file.name})
        for image in plan.images.all():
            if image.image:
                files.append({'label': f'Image #{image.pk}', 'path': image.image.name})
        return files

    actions = [
        'action_publish',
        'action_unpublish',
        'action_mark_featured',
        'action_soft_delete',
        'action_restore',
    ]

    # ---------- Permission Gates ----------
    def _require_superuser(self, request):
        if not request.user.is_superuser:
            self.message_user(request, 'Only superusers can manage plans.', level=messages.ERROR)
            return False
        return True

    def has_module_permission(self, request):
        return request.user.is_active and request.user.is_superuser

    def has_view_permission(self, request, obj=None):
        return request.user.is_active and request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_active and request.user.is_superuser

    def has_add_permission(self, request):
        return request.user.is_active and request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_active and request.user.is_superuser

    # ---------- Query / Save Overrides ----------
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('category', 'pack_configuration', 'last_modified_by', 'deleted_by', 'unpublished_by')

    def save_model(self, request, obj, form, change):
        obj.last_modified_by = request.user
        super().save_model(request, obj, form, change)
        action = PlanAuditLog.Actions.CREATED if not change else PlanAuditLog.Actions.UPDATED
        changed_fields = ', '.join(form.changed_data) if form.changed_data else ''
        PlanAuditLog.log_action(obj, action, request.user, changed_fields)
        if any(field in form.changed_data for field in ('free_plan_file', 'paid_plan_file')):
            PlanAuditLog.log_action(obj, PlanAuditLog.Actions.FILES_UPDATED, request.user)

    def delete_model(self, request, obj):
        """Override delete to always use soft delete - never hard delete through UI."""
        obj.soft_delete(request.user, reason='Soft deleted via admin delete action')
        self.message_user(
            request,
            f'Plan "{obj.reference}" has been soft deleted (not permanently removed). '
            'Use "Restore" to recover or the "Delete permanently" link to remove it forever.',
            level=messages.WARNING
        )

    def delete_queryset(self, request, queryset):
        """Override bulk delete to always use soft delete - never hard delete through UI."""
        count = queryset.count()
        for plan in queryset:
            plan.soft_delete(request.user, reason='Bulk soft delete via admin delete action')
        self.message_user(
            request,
            f'{count} plan(s) have been soft deleted (not permanently removed). '
            'Use "Restore" to recover them or the per-plan "Delete permanently" flow to erase them forever.',
            level=messages.WARNING
        )

    # ---------- Bulk Actions ----------
    def action_publish(self, request, queryset):
        if not self._require_superuser(request):
            return
        success = 0
        for plan in queryset:
            try:
                plan.publish(request.user)
                success += 1
            except ValidationError as exc:
                self.message_user(request, f"{plan.reference}: {exc}", level=messages.ERROR)
        if success:
            self.message_user(request, f'{success} plan(s) published.')
    action_publish.short_description = 'Publish selected plans'

    def action_unpublish(self, request, queryset):
        if not self._require_superuser(request):
            return
        for plan in queryset:
            plan.unpublish(request.user, reason='Bulk unpublish via admin action')
        self.message_user(request, 'Selected plans have been unpublished.')
    action_unpublish.short_description = 'Unpublish selected plans'

    def action_mark_featured(self, request, queryset):
        if not self._require_superuser(request):
            return
        updated = 0
        for plan in queryset:
            plan.featured = True
            plan.save(update_fields=['featured', 'updated_at'])
            updated += 1
            if not plan.is_deleted:
                if not plan.is_published:
                    plan.publish(request.user, note='Auto-published when marked featured')
                else:
                    PlanAuditLog.log_action(plan, PlanAuditLog.Actions.UPDATED, request.user, 'Marked as featured')
        self.message_user(request, f'{updated} plan(s) marked as featured.')
    action_mark_featured.short_description = 'Mark as featured (publishes if needed)'

    def action_soft_delete(self, request, queryset):
        if not self._require_superuser(request):
            return
        for plan in queryset:
            plan.soft_delete(request.user, reason='Bulk soft delete')
        self.message_user(request, 'Selected plans have been soft deleted.', level=messages.WARNING)
    action_soft_delete.short_description = '⚠ Soft delete selected plans'

    def action_restore(self, request, queryset):
        if not self._require_superuser(request):
            return
        for plan in queryset:
            plan.restore(request.user)
        self.message_user(request, 'Selected plans have been restored.')
    action_restore.short_description = 'Restore soft deleted plans'

    def publish_plan_view(self, request, plan_id):
        if not self._require_superuser(request):
            return redirect('admin:plans_plan_changelist')
        plan = get_object_or_404(Plan, pk=plan_id)
        return self._handle_quick_action(
            request,
            plan,
            performer=lambda: plan.publish(
                request.user,
                note='Quick publish via admin list action'
            ),
            success_message=f'Plan "{plan.reference}" is now published.'
        )

    def unpublish_plan_view(self, request, plan_id):
        if not self._require_superuser(request):
            return redirect('admin:plans_plan_changelist')
        plan = get_object_or_404(Plan, pk=plan_id)
        return self._handle_quick_action(
            request,
            plan,
            performer=lambda: plan.unpublish(
                request.user,
                reason='Quick unpublish via admin list action'
            ),
            success_message=f'Plan "{plan.reference}" has been unpublished.'
        )

    def restore_plan_view(self, request, plan_id):
        if not self._require_superuser(request):
            return redirect('admin:plans_plan_changelist')
        plan = get_object_or_404(Plan, pk=plan_id)
        next_param = request.GET.get('next')
        next_url = unquote(next_param) if next_param else reverse('admin:plans_plan_changelist')
        if not plan.is_deleted:
            self.message_user(request, f'Plan "{plan.reference}" is already active.', level=messages.INFO)
            return redirect(next_url)
        plan.restore(request.user)
        self.message_user(request, f'Plan "{plan.reference}" has been restored.')
        return redirect(next_url)

    def _handle_quick_action(self, request, plan, performer, success_message):
        next_param = request.GET.get('next')
        next_url = unquote(next_param) if next_param else reverse('admin:plans_plan_changelist')
        if plan.is_deleted:
            self.message_user(request, 'Restore the plan before performing this action.', level=messages.ERROR)
            return redirect(next_url)
        try:
            performer()
            self.message_user(request, success_message)
        except ValidationError as exc:
            message = exc.messages[0] if hasattr(exc, 'messages') else str(exc)
            self.message_user(request, message, level=messages.ERROR)
        return redirect(next_url)

    def permanent_delete_view(self, request, plan_id):
        if not self._require_superuser(request):
            return redirect('admin:plans_plan_changelist')

        plan = get_object_or_404(
            Plan.objects.select_related('category').prefetch_related('images'),
            pk=plan_id
        )
        change_url = reverse('admin:plans_plan_change', args=[plan.pk])

        if not plan.is_deleted:
            self.message_user(
                request,
                'Soft delete the plan before requesting permanent deletion.',
                level=messages.ERROR
            )
            return redirect(change_url)

        if plan.orders.exists():
            self.message_user(
                request,
                'This plan has associated orders and cannot be removed.',
                level=messages.ERROR
            )
            return redirect(change_url)

        form = PlanPermanentDeleteForm(data=request.POST or None, plan=plan)
        if request.method == 'POST' and form.is_valid():
            try:
                plan.hard_delete(request.user, reason=form.cleaned_data.get('reason', ''))
            except ValidationError as exc:
                form.add_error(None, exc.messages[0] if hasattr(exc, 'messages') else str(exc))
            else:
                self.message_user(
                    request,
                    f'Plan "{plan.reference}" has been permanently deleted.',
                    level=messages.WARNING
                )
                return redirect('admin:plans_plan_changelist')

        context = {
            **self.admin_site.each_context(request),
            'title': f'Permanently delete {plan.reference}',
            'plan': plan,
            'form': form,
            'files_summary': self._plan_files_preview(plan),
            'opts': self.model._meta,
            'plan_changelist_url': reverse('admin:plans_plan_changelist'),
        }
        return TemplateResponse(request, 'admin/plans/plan/permanent_delete_confirmation.html', context)

    def response_add(self, request, obj, post_url_continue=None):
        if any(key in request.POST for key in ('_savepublish', '_savedraft')):
            return redirect('admin:plans_plan_changelist')
        return super().response_add(request, obj, post_url_continue)

    def response_change(self, request, obj):
        if any(key in request.POST for key in ('_savepublish', '_savedraft')):
            return redirect('admin:plans_plan_changelist')
        return super().response_change(request, obj)


@admin.register(PlanImage)
class PlanImageAdmin(admin.ModelAdmin):
    """
    Admin interface for managing plan images (can also be managed inline with plans).
    """
    list_display = ['plan', 'image_type', 'caption', 'is_primary', 'display_order', 'image_preview']
    list_filter = ['image_type', 'is_primary', 'created_at']
    search_fields = ['plan__title', 'plan__reference', 'caption']
    list_editable = ['display_order']
    ordering = ['plan', 'display_order']
    
    fieldsets = (
        ('Image Details', {
            'fields': (
                'plan',
                'image',
                'image_type',
                'caption',
            )
        }),
        ('Display Settings', {
            'fields': (
                'is_primary',
                'display_order',
            )
        }),
    )

    def image_preview(self, obj):
        """Show small preview of the image."""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 50px; max-width: 100px;" />',
                obj.image.url
            )
        return '-'
    image_preview.short_description = 'Preview'


@admin.register(PlanDeletionLog)
class PlanDeletionLogAdmin(admin.ModelAdmin):
    """Read-only audit view for permanent deletion events."""

    list_display = ['plan_reference', 'plan_title', 'deleted_at', 'deleted_by']
    search_fields = ['plan_reference', 'plan_title', 'reason']
    list_filter = ['deleted_at', 'deleted_by']
    readonly_fields = ['plan_reference', 'plan_title', 'deleted_at', 'deleted_by', 'reason', 'metadata_pretty', 'file_errors_pretty']
    fieldsets = (
        ('Plan Details', {
            'fields': ('plan_reference', 'plan_title', 'deleted_by', 'deleted_at', 'reason')
        }),
        ('Captured Metadata', {
            'fields': ('metadata_pretty',)
        }),
        ('File Cleanup Issues', {
            'fields': ('file_errors_pretty',),
            'description': 'Populated only if storage cleanup encountered issues.'
        }),
    )

    def metadata_pretty(self, obj):
        payload = json.dumps(obj.metadata or {}, indent=2, ensure_ascii=False)
        return format_html('<pre style="white-space: pre-wrap;">{}</pre>', payload)
    metadata_pretty.short_description = 'Metadata'

    def file_errors_pretty(self, obj):
        if not obj.file_errors:
            return '—'
        payload = json.dumps(obj.file_errors, indent=2, ensure_ascii=False)
        return format_html('<pre style="white-space: pre-wrap; color: #b91c1c;">{}</pre>', payload)
    file_errors_pretty.short_description = 'File cleanup errors'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_module_permission(self, request):
        return request.user.is_active and request.user.is_superuser
