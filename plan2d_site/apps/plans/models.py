import logging
from pathlib import Path

from django.apps import apps
from django.db import models, transaction
from django.utils import timezone
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage
from django.core.validators import MinValueValidator, FileExtensionValidator
from django.urls import reverse
from django.conf import settings
from decimal import Decimal, ROUND_HALF_UP

logger = logging.getLogger(__name__)


class PlanPublishStatus(models.TextChoices):
    """Canonical visibility states for plans."""
    DRAFT = 'draft', 'Draft'
    UNPUBLISHED = 'unpublished', 'Unpublished'
    PUBLISHED = 'published', 'Published'


class PlanQuerySet(models.QuerySet):
    """Reusable queryset helpers for plan visibility rules."""

    def active(self):
        return self.filter(is_deleted=False)

    def published(self):
        return self.active().filter(publish_status=PlanPublishStatus.PUBLISHED)

    def drafts(self):
        return self.active().filter(publish_status=PlanPublishStatus.DRAFT)

    def unpublished(self):
        return self.active().filter(
            publish_status__in=[PlanPublishStatus.DRAFT, PlanPublishStatus.UNPUBLISHED]
        )

    def visible(self):
        """Plans that can be shown publicly."""
        return self.published()


class PlanManager(models.Manager):
    """Default manager exposing custom queryset helpers."""

    def get_queryset(self):
        return PlanQuerySet(self.model, using=self._db)

    def active(self):
        return self.get_queryset().active()

    def published(self):
        return self.get_queryset().published()

    def drafts(self):
        return self.get_queryset().drafts()

    def unpublished(self):
        return self.get_queryset().unpublished()

    def visible(self):
        return self.get_queryset().visible()


class Category(models.Model):
    """
    Category for organizing house plans (e.g., Modern, Traditional, Bungalow).
    """
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)
    display_order = models.IntegerField(default=0, help_text="Lower numbers appear first")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ['display_order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class PlanReferenceSequence(models.Model):
    """Track the incremental reference counter for each calendar year."""
    year = models.PositiveIntegerField(unique=True)
    last_number = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Plan Reference Sequence"
        verbose_name_plural = "Plan Reference Sequences"

    def __str__(self):
        return f"{self.year}: {self.last_number}"

    @classmethod
    def next_sequence_for_year(cls, year: int) -> int:
        """Generate the next sequential number for a given year in a safe, atomic way."""
        with transaction.atomic():
            sequence, _ = cls.objects.select_for_update().get_or_create(
                year=year,
                defaults={'last_number': 0},
            )
            sequence.last_number += 1
            sequence.save(update_fields=['last_number', 'updated_at'])
        return sequence.last_number


class Plan(models.Model):
    """
    Core model for house plans - represents a construction-ready 2D floor plan.
    """
    HIGH_RES_MIN_WIDTH = 1600
    HIGH_RES_MIN_HEIGHT = 1200
    PLAN_TYPE_CHOICES = [
        ('residential', 'Residential'),
        ('commercial', 'Commercial'),
        ('mixed', 'Mixed Use'),
        ('other', 'Other'),
    ]
    REFERENCE_PREFIX = 'FHP'
    REFERENCE_SEQUENCE_PADDING = 4
    AREA_CONVERSION_FACTOR = Decimal('10.7639')
    AREA_PRECISION = Decimal('0.01')
    PACK_DISPLAY_LABELS = {
        'free': 'Pack 1 · Free Preview',
        'standard': 'Pack 2 · Standard Build Set',
        'pro': 'Pack 3 · Pro BIM Deliverables',
    }
    PACK_SUMMARY_DEFAULTS = {
        'free': 'Study the flow and zoning with a clean, watermark-only preview.',
        'standard': 'Unlock the dimensioned PDF with full annotations and schedules.',
        'pro': 'Optional BIM assets for consultants: editable files and neutral exchanges.',
    }
    objects = PlanManager()

    # Basic Information
    title = models.CharField(max_length=200, help_text="Display name of the plan")
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    reference = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        editable=False,
        help_text="Auto-generated plan reference (e.g., FHP-2026-0007)"
    )
    category = models.ForeignKey(
        Category, 
        on_delete=models.PROTECT, 
        related_name='plans'
    )
    plan_type = models.CharField(
        max_length=20, 
        choices=PLAN_TYPE_CHOICES, 
        default='residential'
    )

    # Plan Specifications
    bedrooms = models.PositiveIntegerField(
        validators=[MinValueValidator(0)],
        help_text="Number of bedrooms"
    )
    bathrooms = models.DecimalField(
        max_digits=3, 
        decimal_places=1,
        validators=[MinValueValidator(0)],
        help_text="Number of bathrooms (e.g., 2.5 for 2 full + 1 half)"
    )
    total_area_sqm = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Total Area (m²)",
        help_text="Total floor area in square meters (enter either m² or ft²)"
    )
    total_area_sqft = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Total Area (ft²)",
        blank=True,
        null=True,
        help_text="Automatically synced with the m² value"
    )

    # Architectural Dossier (optional, displayed on public plan pages)
    floors = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(1)],
        help_text="Number of floors/levels (optional)"
    )
    suggested_plot_size = models.CharField(
        max_length=120,
        blank=True,
        help_text="Suggested plot size (e.g., 12m x 20m) (optional)"
    )
    roof_type = models.CharField(
        max_length=120,
        blank=True,
        help_text="Roof type (e.g., gable, hip, flat) (optional)"
    )
    wall_system = models.CharField(
        max_length=120,
        blank=True,
        help_text="Wall system (e.g., masonry, timber frame) (optional)"
    )
    architect_design_notes = models.TextField(
        blank=True,
        help_text="Architect’s design notes shown publicly (design logic, functional choices, build simplicity)"
    )

    BUDGET_LEVEL_CHOICES = [
        ('low', 'Low'),
        ('mid', 'Medium'),
        ('high', 'High'),
    ]
    climate_suitability = models.CharField(
        max_length=120,
        blank=True,
        help_text="Climate suitability (optional)"
    )
    plot_type = models.CharField(
        max_length=120,
        blank=True,
        help_text="Plot type (flat, sloped, narrow, corner, etc.) (optional)"
    )
    budget_level = models.CharField(
        max_length=10,
        choices=BUDGET_LEVEL_CHOICES,
        blank=True,
        help_text="Budget level (optional)"
    )
    target_user = models.CharField(
        max_length=120,
        blank=True,
        help_text="Target user (first-time builder, rental, guest house, etc.) (optional)"
    )

    # Content
    description = models.TextField(
        help_text="Public description visible to customers"
    )
    engineer_notes = models.TextField(
        blank=True,
        help_text="Internal notes for engineers/admin only (not visible to customers)"
    )

    # Files
    free_plan_file = models.FileField(
        upload_to='plans/free/%Y/%m/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(['pdf'])],
        help_text="Preview plan without dimensions (PDF only)"
    )
    free_3d_image = models.ImageField(
        upload_to='plans/free_3d/%Y/%m/',
        blank=True,
        null=True,
        help_text="Optional free 3D preview image without dimensions"
    )
    free_3d_caption = models.CharField(
        max_length=200,
        blank=True,
        help_text="Optional caption shown next to the free 3D preview"
    )
    paid_plan_file = models.FileField(
        upload_to='plans/paid/%Y/%m/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(['pdf'])],
        help_text="Full plan with dimensions (PDF only)"
    )
    paid_pdf_available = models.BooleanField(
        default=True,
        help_text="Toggle off to hide the dimensioned paid PDF while keeping the free preview available."
    )
    gumroad_paid_pdf_url = models.URLField(
        blank=True,
        max_length=500,
        help_text="Optional Gumroad link dedicated to the paid PDF checkout."
    )
    pack_2_gumroad_zip_url = models.URLField(
        blank=True,
        max_length=500,
        verbose_name="Pack 2 Gumroad ZIP URL",
        help_text="Single Gumroad ZIP delivering Pack 2 (contains both Metric and Imperial PDFs)."
    )

    # Pricing
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        blank=True,
        null=True,
        help_text="Price in USD for the dimensioned PDF (Pack 2 · Standard)."
    )

    # Gumroad Payment Integration
    gumroad_url = models.URLField(
        blank=True,
        max_length=500,
        help_text="Gumroad checkout link for the paid version of this plan (e.g., https://gumroad.com/l/your-product)"
    )
    enable_gumroad_payment = models.BooleanField(
        default=True,
        help_text="Enable or disable Gumroad payment for this plan. Payment button will only show if both this is enabled AND Gumroad URL is provided."
    )

    # Optional Revit Offer
    revit_available = models.BooleanField(
        default=False,
        help_text="Toggle on when an editable Revit (RVT) file is available for this plan."
    )
    gumroad_revit_url = models.URLField(
        blank=True,
        max_length=500,
        help_text="Gumroad checkout link for the Revit (.RVT) file. Payments remain on Gumroad."
    )
    revit_version = models.CharField(
        max_length=50,
        blank=True,
        help_text="Revit version compatibility (e.g., Revit 2022)."
    )
    revit_notes = models.TextField(
        blank=True,
        help_text="Optional context describing what is included in the Revit file."
    )
    revit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        blank=True,
        null=True,
        help_text="Price in USD for the editable Revit deliverable. Applies to both metric and imperial files."
    )

    # Optional IFC Offer
    ifc_available = models.BooleanField(
        default=False,
        help_text="Toggle on when an open IFC file is available for this plan."
    )
    gumroad_ifc_url = models.URLField(
        blank=True,
        max_length=500,
        help_text="Gumroad checkout link for the IFC file. Payments remain on Gumroad."
    )
    ifc_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        blank=True,
        null=True,
        help_text="Price in USD for the IFC deliverable. Applies to both metric and imperial files."
    )
    ifc_version = models.CharField(
        max_length=50,
        blank=True,
        help_text="IFC version or schema (e.g., IFC2x3, IFC4)."
    )
    ifc_notes = models.TextField(
        blank=True,
        help_text="Optional context describing what is included in the IFC export."
    )
    pack_3_gumroad_zip_url = models.URLField(
        blank=True,
        max_length=500,
        verbose_name="Pack 3 Gumroad ZIP URL",
        help_text="Single Gumroad ZIP delivering Pack 3 (Metric + Imperial Revit/IFC/DWG)."
    )

    pack_3_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        blank=True,
        null=True,
        help_text=(
            "Pack 3 selling price in USD. Pack 3 stays hidden on the website until a positive price is set here."
        ),
    )

    # Visibility & Lifecycle
    publish_status = models.CharField(
        max_length=20,
        choices=PlanPublishStatus.choices,
        default=PlanPublishStatus.DRAFT,
        db_index=True,
        help_text="Controls whether the plan is publicly visible"
    )
    published_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Timestamp of the last publish action"
    )
    unpublished_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Timestamp of the last unpublish action"
    )
    unpublished_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='plans_unpublished',
        help_text="Admin who last unpublished this plan"
    )
    unpublished_reason = models.CharField(
        max_length=255,
        blank=True,
        help_text="Optional note explaining why the plan was unpublished"
    )
    featured = models.BooleanField(
        default=False,
        help_text="Show this plan in featured sections"
    )
    is_deleted = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Soft delete flag (keeps orders intact)"
    )
    deleted_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="When the plan was soft-deleted"
    )
    deleted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='plans_deleted',
        help_text="Admin who soft-deleted this plan"
    )
    last_modified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='plans_modified',
        help_text="Last admin who modified this plan"
    )
    language_content = models.JSONField(
        blank=True,
        default=dict,
        help_text="Localized content keyed by language code (e.g., EN/FR)"
    )

    # Metadata
    views_count = models.PositiveIntegerField(default=0, editable=False)
    downloads_count = models.PositiveIntegerField(default=0, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # SEO Fields
    seo_title = models.CharField(
        max_length=60,
        blank=True,
        help_text="Custom SEO title (60 chars max). Leave empty to auto-generate."
    )
    seo_description = models.CharField(
        max_length=160,
        blank=True,
        help_text="Custom SEO description (160 chars max). Leave empty to auto-generate."
    )
    seo_keywords = models.CharField(
        max_length=255,
        blank=True,
        help_text="Comma-separated keywords for SEO"
    )

    class Meta:
        verbose_name = "Plan"
        verbose_name_plural = "Plans"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['publish_status', '-created_at']),
            models.Index(fields=['category', 'publish_status']),
            models.Index(fields=['is_deleted', 'publish_status']),
        ]

    def __str__(self):
        return f"{self.reference or 'Plan'} - {self.title}"

    def _build_reference_value(self) -> str:
        """Return a unique, formatted reference for newly created plans."""
        current_year = timezone.now().year
        sequence = PlanReferenceSequence.next_sequence_for_year(current_year)
        sequence_str = f"{sequence:0{self.REFERENCE_SEQUENCE_PADDING}d}"
        return f"{self.REFERENCE_PREFIX}-{current_year}-{sequence_str}"

    def _quantize_area(self, value: Decimal | None) -> Decimal | None:
        if value is None:
            return None
        return value.quantize(self.AREA_PRECISION, rounding=ROUND_HALF_UP)

    def _convert_sqm_to_sqft(self, sqm: Decimal | None) -> Decimal | None:
        if sqm is None:
            return None
        return self._quantize_area(Decimal(sqm) * self.AREA_CONVERSION_FACTOR)

    def _convert_sqft_to_sqm(self, sqft: Decimal | None) -> Decimal | None:
        if sqft is None:
            return None
        return self._quantize_area(Decimal(sqft) / self.AREA_CONVERSION_FACTOR)

    def _watermarked_free_plan_name(self, source_name: str | None = None) -> str:
        file_name = source_name or getattr(self.free_plan_file, 'name', '')
        if not file_name:
            return ''
        original = Path(file_name)
        stamped = original.with_stem(f"{original.stem}_watermarked")
        return str(stamped)

    def _watermarked_file_exists(self) -> bool:
        if not self.free_plan_file:
            return False
        destination = self._watermarked_free_plan_name()
        if not destination:
            return False
        storage = self.free_plan_file.storage
        return storage.exists(destination)

    def _delete_watermarked_free_plan(self, source_name: str | None = None):
        destination = self._watermarked_free_plan_name(source_name)
        if not destination:
            return
        storage = getattr(self.free_plan_file, 'storage', default_storage)
        if storage.exists(destination):
            storage.delete(destination)

    def _collect_file_snapshot(self):
        """Capture storage references for every file tied to this plan."""
        snapshot = []
        metadata = []

        def _append(label, storage, path, asset_type):
            if not path:
                return
            snapshot.append({'storage': storage, 'path': path})
            metadata.append({'label': label, 'path': path, 'type': asset_type})

        if self.free_plan_file:
            storage = self.free_plan_file.storage
            _append('Free PDF', storage, self.free_plan_file.name, 'free_pdf')
            watermarked_name = self._watermarked_free_plan_name()
            if watermarked_name:
                _append('Free PDF (watermarked copy)', storage, watermarked_name, 'free_pdf_watermarked')

        if self.paid_plan_file:
            _append('Paid PDF', self.paid_plan_file.storage, self.paid_plan_file.name, 'paid_pdf')

        if self.free_3d_image:
            _append('Free 3D preview', self.free_3d_image.storage, self.free_3d_image.name, 'free_3d_image')

        for image in self.images.all():
            if image.image:
                _append(f"Image #{image.pk}", image.image.storage, image.image.name, 'image')

        return snapshot, metadata

    def ensure_free_plan_watermark(self, force: bool = False) -> str:
        """Generate (or fetch) the watermarked free-plan PDF path."""
        if not self.free_plan_file or self.is_deleted:
            return ''

        destination = self._watermarked_free_plan_name()
        storage = self.free_plan_file.storage

        if not destination:
            return ''

        needs_regeneration = force or not storage.exists(destination)

        if not needs_regeneration:
            try:
                original_mtime = storage.get_modified_time(self.free_plan_file.name)
                watermarked_mtime = storage.get_modified_time(destination)
                needs_regeneration = watermarked_mtime < original_mtime
            except (NotImplementedError, FileNotFoundError):
                needs_regeneration = False

        if not needs_regeneration:
            return destination

        try:
            from .services.watermark import generate_watermarked_pdf
        except ImportError:  # pragma: no cover - hard dependency missing
            logger.warning(
                "Watermark dependencies missing; falling back to original free plan file."
            )
            return ''

        try:
            return generate_watermarked_pdf(storage, self.free_plan_file.name, destination)
        except Exception as exc:  # pragma: no cover - defensive logging
            logger.exception("Unable to watermark free plan file %s", self.free_plan_file.name)
            raise ValidationError("Unable to generate watermarked free plan document.") from exc

    def save(self, *args, **kwargs):
        """Custom save hook to keep lifecycle fields and files in sync."""
        old_instance = None
        if self.pk:
            old_instance = Plan.objects.filter(pk=self.pk).first()
        old_free_file_name = ''
        if old_instance and old_instance.free_plan_file:
            old_free_file_name = old_instance.free_plan_file.name
        new_free_file_name = self.free_plan_file.name if self.free_plan_file else ''
        free_plan_changed = old_free_file_name != new_free_file_name

        if not self.reference:
            self.reference = self._build_reference_value()

        # Auto-generate or normalize slug
        base_slug = self.slug or self.title
        self.slug = slugify(base_slug)

        # Keep area fields in sync without forcing duplicate manual work
        self.total_area_sqm = self._quantize_area(self.total_area_sqm)
        self.total_area_sqft = self._quantize_area(self.total_area_sqft)
        sqm_changed = bool(old_instance) and self.total_area_sqm != old_instance.total_area_sqm
        sqft_changed = bool(old_instance) and self.total_area_sqft != old_instance.total_area_sqft
        area_last_source = getattr(self, '_area_last_edited', None)

        if area_last_source == 'sqm' and self.total_area_sqm:
            self.total_area_sqft = self._convert_sqm_to_sqft(self.total_area_sqm)
        elif area_last_source == 'sqft' and self.total_area_sqft:
            self.total_area_sqm = self._convert_sqft_to_sqm(self.total_area_sqft)
        elif self.total_area_sqm and not self.total_area_sqft:
            self.total_area_sqft = self._convert_sqm_to_sqft(self.total_area_sqm)
        elif self.total_area_sqft and not self.total_area_sqm:
            self.total_area_sqm = self._convert_sqft_to_sqm(self.total_area_sqft)
        elif sqm_changed and not sqft_changed:
            self.total_area_sqft = self._convert_sqm_to_sqft(self.total_area_sqm)
        elif sqft_changed and not sqm_changed:
            self.total_area_sqm = self._convert_sqft_to_sqm(self.total_area_sqft)

        # Validate Gumroad URLs if provided
        self._normalize_gumroad_url('gumroad_url')
        self._normalize_gumroad_url('gumroad_revit_url')
        self._normalize_gumroad_url('gumroad_ifc_url')
        self._normalize_gumroad_url('gumroad_paid_pdf_url')
        self._normalize_gumroad_url('pack_2_gumroad_zip_url')
        self._normalize_gumroad_url('pack_3_gumroad_zip_url')

        # Enforce status invariants
        now = timezone.now()
        if self.is_deleted:
            self.publish_status = PlanPublishStatus.UNPUBLISHED

        if self.publish_status == PlanPublishStatus.PUBLISHED and not self.is_deleted:
            if not self.published_at:
                self.published_at = now
            self.unpublished_at = None
            self.unpublished_reason = self.unpublished_reason or ''
            self.unpublished_by = None
        else:
            if old_instance and old_instance.publish_status == PlanPublishStatus.PUBLISHED and self.publish_status != PlanPublishStatus.PUBLISHED:
                self.unpublished_at = now

        self._normalize_language_content()

        super().save(*args, **kwargs)

        if self.free_plan_file:
            try:
                self.ensure_free_plan_watermark(force=free_plan_changed)
            except ValidationError:
                raise

        # Persist slug history for safe redirects
        if old_instance and old_instance.slug != self.slug:
            PlanSlugHistory.objects.update_or_create(
                plan=self,
                slug=old_instance.slug,
                defaults={'changed_at': now}
            )

        # Clean up replaced files to avoid orphaned assets
        self._cleanup_replaced_files(old_instance)

    def get_absolute_url(self):
        """URL to view this plan (to be implemented later)."""
        return reverse('plans:detail', kwargs={'slug': self.slug})

    def get_free_plan_download_url(self):
        if not self.free_plan_file:
            return ''
        return reverse('plans:free_download', kwargs={'slug': self.slug})

    @property
    def is_visible(self):
        return self.publish_status == PlanPublishStatus.PUBLISHED and not self.is_deleted

    @property
    def is_published(self):
        return self.publish_status == PlanPublishStatus.PUBLISHED

    @property
    def is_draft(self):
        return self.publish_status == PlanPublishStatus.DRAFT

    def _prepared_url(self, value: str | None) -> str:
        return value.strip() if value else ''

    @property
    def has_free_plan(self):
        """Check if free preview is available."""
        return bool(self.free_plan_file)

    @property
    def has_paid_plan(self):
        """Check if paid plan is available."""
        return bool(self.paid_plan_file)

    @property
    def has_revit_offer(self):
        """True when Pack 3 is available (priced + ZIP configured)."""
        return self.has_pro_pack

    @property
    def has_ifc_offer(self):
        """True when Pack 3 is available (priced + ZIP configured)."""
        return self.has_pro_pack

    @property
    def has_paid_pdf_offer(self):
        """True when Pack 2 ZIP is available."""
        return bool(
            self.paid_pdf_available and
            self.enable_gumroad_payment and
            self.pack_2_gumroad_zip_url
        )

    @property
    def pack_config(self):
        if hasattr(self, '_pack_config_cache'):
            return self._pack_config_cache
        config = getattr(self, 'pack_configuration', None)
        if config is None:
            config, _ = PlanPackConfiguration.objects.get_or_create(plan=self)
        self._pack_config_cache = config
        return config

    @property
    def has_pro_pack(self):
        price = self.pack_3_price
        return bool(
            self.enable_gumroad_payment and
            self.pack_3_gumroad_zip_url and
            price is not None and
            price > 0
        )

    @property
    def pro_pack_label(self):
        return self.pack_config.display_label

    @property
    def pro_pack_summary(self):
        return self.pack_config.display_summary or self.PACK_SUMMARY_DEFAULTS['pro']

    @property
    def pro_pack_notes(self):
        return self.pack_config.display_notes

    @property
    def has_dwg_asset(self):
        return self.has_pro_pack

    def dwg_download_url(self):
        file = getattr(self.pack_config, 'dwg_file', None)
        return getattr(file, 'url', '') if file else ''

    # ---------- Image helpers ----------
    def _get_image_sequence(self):
        """Return cached plan images to avoid repeated queryset evaluation."""
        cache_key = '_image_sequence_cache'
        if hasattr(self, cache_key):
            return getattr(self, cache_key)
        images = list(self.images.all())
        setattr(self, cache_key, images)
        return images

    def get_primary_image(self):
        """Return the primary image, respecting explicit flags and display order."""
        cache_key = '_primary_image_cache'
        if hasattr(self, cache_key):
            return getattr(self, cache_key)

        images = self._get_image_sequence()
        primary = next((image for image in images if image.is_primary), None)
        if not primary and images:
            primary = images[0]

        setattr(self, cache_key, primary)
        return primary

    def get_gallery_images(self):
        """Return non-primary images for galleries without querying again."""
        cache_key = '_gallery_images_cache'
        if hasattr(self, cache_key):
            return getattr(self, cache_key)

        primary = self.get_primary_image()
        gallery = [image for image in self._get_image_sequence() if not primary or image.pk != primary.pk]
        setattr(self, cache_key, gallery)
        return gallery

    def has_high_resolution_primary(self, min_width=None, min_height=None):
        """Check if the primary image satisfies the high-resolution baseline."""
        min_width = min_width or self.HIGH_RES_MIN_WIDTH
        min_height = min_height or self.HIGH_RES_MIN_HEIGHT

        primary = self.get_primary_image()
        if not primary or not primary.image:
            return False

        width = getattr(primary.image, 'width', None) or 0
        height = getattr(primary.image, 'height', None) or 0
        return width >= min_width and height >= min_height

    def get_seo_title(self):
        """Get SEO title (custom or auto-generated)."""
        if self.seo_title:
            return self.seo_title
        domain = getattr(settings, 'BRAND_DOMAIN', 'FreeHousePlan.com')
        return f"{self.title} Free House Plan | {self.reference} | {domain}"

    def get_seo_description(self):
        """Get SEO description (custom or auto-generated)."""
        if self.seo_description:
            return self.seo_description
        domain = getattr(settings, 'BRAND_DOMAIN', 'FreeHousePlan.com')
        plan_type = self.get_plan_type_display().lower()
        base = (
            f"{self.title}: {self.bedrooms} bed, {self.bathrooms} bath, {self.total_area_sqm}m² {plan_type} house plan. "
            "Download the free preview (no dimensions)."
        )

        upsell_bits = []
        if self.has_paid_pdf_offer:
            upsell_bits.append("Pack 2 ZIP includes Metric + Imperial PDFs")
        if self.has_pro_pack:
            upsell_bits.append("Pack 3 ZIP adds DWG, Revit, and IFC (Metric + Imperial)")

        if upsell_bits:
            return f"{base} " + "; ".join(upsell_bits) + f". Available on {domain}."

        return f"{base} Build-ready upgrades available on {domain}."

    def get_seo_keywords(self):
        """Get SEO keywords (custom or auto-generated)."""
        if self.seo_keywords:
            return self.seo_keywords
        keywords = [
            "free house plan",
            "free house plans",
            "free floor plan",
            "house plan free",
            "simple house plan",
            "build-ready house plan",
            "architectural plans",
            f"{self.bedrooms} bedroom house plan",
            f"{self.bedrooms} bed house plan",
            f"{self.category.name.lower()} house plan",
            "house plans",
            "floor plans",
            f"{int(self.total_area_sqm)}m2 house plan",
            f"{int(self.total_area_sqft)}sqft house plan",
        ]

        if self.has_pro_pack:
            keywords.extend([
                "dwg house plans",
                "revit house plans",
                "ifc building models",
                "metric and imperial plans",
            ])

        return ", ".join(keywords)

    def publish(self, user=None, note=''):
        """Publish the plan safely with audit logging."""
        if self.is_deleted:
            raise ValidationError("Cannot publish a deleted plan. Restore it first.")
        if self.publish_status == PlanPublishStatus.PUBLISHED:
            return
        self.publish_status = PlanPublishStatus.PUBLISHED
        self.published_at = timezone.now()
        self.unpublished_at = None
        self.unpublished_reason = ''
        self.unpublished_by = None
        self.last_modified_by = user
        self.save(update_fields=[
            'publish_status',
            'published_at',
            'unpublished_at',
            'unpublished_reason',
            'unpublished_by',
            'last_modified_by',
            'updated_at'
        ])
        PlanAuditLog.log_action(self, PlanAuditLog.Actions.PUBLISHED, user, note)

    def unpublish(self, user=None, reason=''):
        if self.publish_status == PlanPublishStatus.UNPUBLISHED:
            return
        self.publish_status = PlanPublishStatus.UNPUBLISHED
        self.unpublished_at = timezone.now()
        self.unpublished_by = user
        self.unpublished_reason = reason or self.unpublished_reason
        self.last_modified_by = user
        self.save(update_fields=[
            'publish_status',
            'unpublished_at',
            'unpublished_by',
            'unpublished_reason',
            'last_modified_by',
            'updated_at'
        ])
        PlanAuditLog.log_action(self, PlanAuditLog.Actions.UNPUBLISHED, user, reason)

    def mark_draft(self, user=None, note=''):
        """Return plan to draft mode (hidden from public)."""
        if self.is_deleted:
            raise ValidationError("Cannot mark a deleted plan as draft. Restore it first.")
        if self.publish_status == PlanPublishStatus.DRAFT:
            return
        now = timezone.now()
        self.publish_status = PlanPublishStatus.DRAFT
        if self.is_published:
            self.unpublished_at = now
            self.unpublished_by = user
            self.unpublished_reason = note or self.unpublished_reason
        self.last_modified_by = user
        self.save(update_fields=[
            'publish_status',
            'unpublished_at',
            'unpublished_by',
            'unpublished_reason',
            'last_modified_by',
            'updated_at'
        ])
        PlanAuditLog.log_action(self, PlanAuditLog.Actions.DRAFTED, user, note)

    def soft_delete(self, user=None, reason=''):
        if self.is_deleted:
            return
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.deleted_by = user
        self.publish_status = PlanPublishStatus.UNPUBLISHED
        self.last_modified_by = user
        self.save(update_fields=[
            'is_deleted',
            'deleted_at',
            'deleted_by',
            'publish_status',
            'last_modified_by',
            'updated_at'
        ])
        PlanAuditLog.log_action(self, PlanAuditLog.Actions.SOFT_DELETED, user, reason)

    def restore(self, user=None):
        if not self.is_deleted:
            return
        self.is_deleted = False
        self.deleted_at = None
        self.deleted_by = None
        self.last_modified_by = user
        self.save(update_fields=[
            'is_deleted',
            'deleted_at',
            'deleted_by',
            'last_modified_by',
            'updated_at'
        ])
        PlanAuditLog.log_action(self, PlanAuditLog.Actions.RESTORED, user)

    def hard_delete(self, user=None, reason: str = ''):
        """PERMANENT deletion - removes plan and all associated data. Use with extreme caution."""
        from apps.orders.models import Order

        order_count = self.orders.count()
        if order_count > 0:
            completed_count = self.orders.filter(payment_status=Order.COMPLETED).count()
            raise ValidationError(
                f"Cannot hard delete plan {self.reference}: {order_count} order(s) exist "
                f"({completed_count} completed). This would violate order integrity."
            )

        if not self.is_deleted:
            raise ValidationError(
                f"Plan {self.reference} must be soft deleted first. "
                "Hard delete is only allowed for already soft-deleted plans."
            )

        file_snapshot, file_metadata = self._collect_file_snapshot()
        metadata = {
            'slug': self.slug,
            'category': self.category.name if self.category_id else None,
            'files': file_metadata,
            'total_files': len(file_metadata),
        }

        with transaction.atomic():
            deletion_log = PlanDeletionLog.objects.create(
                plan_reference=self.reference,
                plan_title=self.title,
                deleted_by=user,
                reason=reason or '',
                metadata=metadata,
            )
            PlanAuditLog.log_action(
                self,
                PlanAuditLog.Actions.HARD_DELETED,
                user,
                f"PERMANENT DELETION of {self.reference}"
            )

            super().delete()
            transaction.on_commit(
                lambda: self._finalize_permanent_file_cleanup(file_snapshot, deletion_log.pk)
            )

        logger.info("Plan %s permanently deleted by %s", self.reference, getattr(user, 'username', 'system'))
        return deletion_log

    # ---------- Localization Helpers ----------
    def apply_language(self, language_code):
        """Mutate fields based on requested language (fallbacks to defaults)."""
        if not language_code:
            return self
        payload = (self.language_content or {}).get(language_code.lower())
        if not payload:
            return self
        for field in ('title', 'description', 'seo_title', 'seo_description'):
            value = payload.get(field)
            if value:
                setattr(self, field, value)
        return self

    def get_localized_value(self, field_name, language_code):
        payload = (self.language_content or {}).get(language_code.lower(), {})
        return payload.get(field_name)

    # ---------- Internal utilities ----------
    def _normalize_language_content(self):
        if not self.language_content:
            self.language_content = {}
            return
        normalized = {}
        for lang_code, values in self.language_content.items():
            lang = (lang_code or '').lower()
            if lang not in {'en', 'fr'}:
                continue
            cleaned = {}
            for key in ('title', 'description', 'seo_title', 'seo_description'):
                value = (values or {}).get(key)
                if value:
                    cleaned[key] = value.strip()
            if cleaned:
                normalized[lang] = cleaned
        self.language_content = normalized

    def _cleanup_replaced_files(self, old_instance):
        if not old_instance:
            return
        for field_name in (
            'free_plan_file',
            'free_3d_image',
            'paid_plan_file',
        ):
            old_file = getattr(old_instance, field_name)
            new_file = getattr(self, field_name)
            if old_file and (not new_file or old_file.name != new_file.name):
                if field_name == 'free_plan_file':
                    self._delete_watermarked_free_plan(old_file.name)
                old_file.delete(save=False)

    def _delete_all_files(self, snapshot=None):
        target_snapshot = snapshot
        if target_snapshot is None:
            target_snapshot, _ = self._collect_file_snapshot()

        errors = []
        for entry in target_snapshot:
            storage = entry.get('storage')
            path = entry.get('path')
            if not storage or not path:
                continue
            try:
                if storage.exists(path):
                    storage.delete(path)
            except Exception as exc:  # pragma: no cover - defensive cleanup guard
                logger.warning("Failed to delete plan asset %s: %s", path, exc)
                errors.append({'path': path, 'error': str(exc)})
        return errors

    def _finalize_permanent_file_cleanup(self, snapshot, log_entry_pk):
        errors = self._delete_all_files(snapshot)
        if errors:
            PlanDeletionLog = apps.get_model('plans', 'PlanDeletionLog')
            PlanDeletionLog.objects.filter(pk=log_entry_pk).update(file_errors=errors)

    def _normalize_gumroad_url(self, field_name):
        url_value = getattr(self, field_name, '') or ''
        if not url_value:
            return
        cleaned = url_value.strip()
        setattr(self, field_name, cleaned)
        if not (cleaned.startswith('https://gumroad.com/') or (
                cleaned.startswith('https://') and '.gumroad.com/' in cleaned)):
            raise ValidationError({
                field_name: 'Gumroad URL must start with https://gumroad.com/ or https://*.gumroad.com/'
            })


class PlanPackConfiguration(models.Model):
    """Lightweight, additive metadata that organizes plan packs."""

    plan = models.OneToOneField(
        Plan,
        on_delete=models.CASCADE,
        related_name='pack_configuration'
    )
    enable_pro_pack = models.BooleanField(
        default=False,
        help_text="Show the Pack 3 – Pro BIM grouping on plan pages and in admin."
    )
    pro_pack_label = models.CharField(
        max_length=120,
        blank=True,
        help_text="Optional heading override for Pack 3 (defaults to 'Pack 3 · Pro BIM Deliverables')."
    )
    pro_pack_summary = models.CharField(
        max_length=255,
        blank=True,
        help_text="Short descriptor shown near Pack 3 cards on the frontend."
    )
    pro_pack_notes = models.TextField(
        blank=True,
        help_text="Long-form notes for Pack 3 (supports Markdown-safe plain text)."
    )
    dwg_file = models.FileField(
        upload_to='plans/pro/dwg/%Y/%m/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(['dwg', 'dxf', 'zip'])],
        help_text="Optional DWG or DXF deliverable stored locally. Leave empty if not offered."
    )
    dwg_file_label = models.CharField(
        max_length=120,
        blank=True,
        help_text="Optional call-to-action label for the DWG button (defaults to 'Download DWG')."
    )
    dwg_file_description = models.CharField(
        max_length=255,
        blank=True,
        help_text="Optional caption displayed beneath the DWG download button."
    )
    dwg_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        blank=True,
        null=True,
        help_text="Price in USD for the DWG/DXF deliverable (applies to all unit formats)."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Plan Pack Configuration'
        verbose_name_plural = 'Plan Pack Configurations'

    def __str__(self):
        return f"Packs for {self.plan.reference}"

    @property
    def display_label(self):
        return self.pro_pack_label or Plan.PACK_DISPLAY_LABELS['pro']

    @property
    def display_summary(self):
        return self.pro_pack_summary

    @property
    def display_notes(self):
        return self.pro_pack_notes

    @property
    def dwg_cta_label(self):
        return self.dwg_file_label or 'Download DWG'


class PlanImage(models.Model):
    """
    Images associated with a plan (floor plans, elevations, 3D renders, etc.).
    """
    IMAGE_TYPE_CHOICES = [
        ('floor_plan', 'Floor Plan'),
        ('elevation', 'Elevation'),
        ('section', 'Section'),
        ('3d_render', '3D Render'),
        ('photo', 'Photo'),
        ('other', 'Other'),
    ]

    plan = models.ForeignKey(
        Plan,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField(
        upload_to='plans/images/%Y/%m/',
        help_text="Upload plan images (PNG, JPG)"
    )
    image_type = models.CharField(
        max_length=20,
        choices=IMAGE_TYPE_CHOICES,
        default='floor_plan'
    )
    caption = models.CharField(
        max_length=200,
        blank=True,
        help_text="Optional caption for the image"
    )
    display_order = models.IntegerField(
        default=0,
        help_text="Lower numbers appear first"
    )
    is_primary = models.BooleanField(
        default=False,
        help_text="Use as the main thumbnail image"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Plan Image"
        verbose_name_plural = "Plan Images"
        ordering = ['display_order', '-is_primary', '-created_at']

    def __str__(self):
        return f"{self.plan.reference} - {self.get_image_type_display()}"

    def save(self, *args, **kwargs):
        # If this is set as primary, remove primary from other images
        if self.is_primary:
            PlanImage.objects.filter(
                plan=self.plan, 
                is_primary=True
            ).exclude(pk=self.pk).update(is_primary=False)
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        image = self.image
        super().delete(*args, **kwargs)
        if image:
            image.delete(save=False)


class PlanSlugHistory(models.Model):
    """Keeps track of historical slugs for safe redirects."""

    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, related_name='slug_history')
    slug = models.SlugField(max_length=200, unique=True)
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-changed_at']
        verbose_name = 'Plan Slug History'
        verbose_name_plural = 'Plan Slug History'

    def __str__(self):
        return f"{self.slug} → {self.plan.slug}"


class PlanAuditLog(models.Model):
    """Immutable log of administrative actions applied to plans."""

    class Actions(models.TextChoices):
        CREATED = 'created', 'Created'
        UPDATED = 'updated', 'Updated'
        FILES_UPDATED = 'files_updated', 'Files Updated'
        PUBLISHED = 'published', 'Published'
        UNPUBLISHED = 'unpublished', 'Unpublished'
        DRAFTED = 'drafted', 'Marked Draft'
        SOFT_DELETED = 'soft_deleted', 'Soft Deleted'
        RESTORED = 'restored', 'Restored'
        HARD_DELETED = 'hard_deleted', 'Hard Deleted'

    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, related_name='audit_logs')
    action = models.CharField(max_length=50, choices=Actions.choices)
    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='plan_actions'
    )
    notes = models.TextField(blank=True)
    metadata = models.JSONField(blank=True, default=dict)
    performed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-performed_at']
        verbose_name = 'Plan Audit Log'
        verbose_name_plural = 'Plan Audit Logs'

    def __str__(self):
        return f"{self.get_action_display()} - {self.plan.reference}"

    @classmethod
    def log_action(cls, plan, action, user=None, notes='', metadata=None):
        metadata = metadata or {}
        return cls.objects.create(
            plan=plan,
            action=action,
            performed_by=user,
            notes=notes,
            metadata=metadata
        )


class PlanDeletionLog(models.Model):
    """Immutable audit trail for irreversible plan deletions."""

    plan_reference = models.CharField(max_length=50)
    plan_title = models.CharField(max_length=200)
    deleted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='plan_deletions'
    )
    deleted_at = models.DateTimeField(auto_now_add=True)
    reason = models.TextField(blank=True)
    metadata = models.JSONField(blank=True, default=dict)
    file_errors = models.JSONField(blank=True, default=list)

    class Meta:
        ordering = ['-deleted_at']
        verbose_name = 'Plan Deletion Log'
        verbose_name_plural = 'Plan Deletion Logs'

    def __str__(self):
        return f"{self.plan_reference} permanently deleted"
