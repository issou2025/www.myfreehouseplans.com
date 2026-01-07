import io
import logging
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from django.core.files.base import ContentFile
from django.core.files.storage import Storage

from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas

LOGGER = logging.getLogger(__name__)
WATERMARK_TEXT = ("FreeHousePlan.com", "Free plan – for preview only")


@dataclass(frozen=True)
class WatermarkOptions:
    opacity: float = 0.18
    font_size: int = 34
    rotation: int = 45
    padding: int = 80


def _build_overlay(width: float, height: float, options: WatermarkOptions) -> PdfReader:
    packet = io.BytesIO()
    painter = canvas.Canvas(packet, pagesize=(width, height))
    painter.saveState()
    try:
        painter.setFillAlpha(options.opacity)
    except AttributeError:  # pragma: no cover - ReportLab w/out alpha
        pass
    painter.setFont("Helvetica-Bold", options.font_size)
    painter.setFillColorRGB(0.2, 0.2, 0.2)
    painter.translate(width / 2, height / 2)
    painter.rotate(options.rotation)
    baseline = 0
    for index, text in enumerate(WATERMARK_TEXT):
        painter.drawCentredString(0, baseline + (index * options.padding // 2), text)
    painter.restoreState()
    painter.save()
    packet.seek(0)
    return PdfReader(packet)


@lru_cache(maxsize=32)
def _overlay_cache(width: float, height: float, key: str) -> PdfReader:
    return _build_overlay(width, height, WatermarkOptions())


def _get_overlay(width: float, height: float) -> PdfReader:
    cache_key = f"{round(width)}x{round(height)}"
    return _overlay_cache(width, height, cache_key)


def generate_watermarked_pdf(source_storage: Storage, source_path: str, destination_path: str) -> str:
    """Generate a watermarked PDF copy while preserving the original file."""
    LOGGER.info("Generating watermarked PDF for %s", source_path)
    with source_storage.open(source_path, 'rb') as source_stream:
        reader = PdfReader(source_stream)
        writer = PdfWriter()

        for page in reader.pages:
            width = float(page.mediabox.width)
            height = float(page.mediabox.height)
            overlay_reader = _get_overlay(width, height)
            page.merge_page(overlay_reader.pages[0])
            writer.add_page(page)

        output_buffer = io.BytesIO()
        writer.write(output_buffer)
        output_buffer.seek(0)

    source_storage.save(destination_path, ContentFile(output_buffer.read()))
    LOGGER.info("Watermarked PDF stored at %s", destination_path)
    return destination_path
