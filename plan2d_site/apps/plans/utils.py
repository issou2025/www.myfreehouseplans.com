from __future__ import annotations

import re
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional

PLOT_SIZE_PATTERN = re.compile(r"^(?P<width>\d+(?:\.\d+)?)x(?P<depth>\d+(?:\.\d+)?)$")
FEET_CONVERSION_FACTOR = Decimal("3.28084")


def _sanitize_plot_size_input(raw_value: str) -> str:
    normalized = raw_value.lower().strip()
    normalized = normalized.replace("×", "x")
    normalized = re.sub(r"meters?|metres?|meter|metre", "", normalized)
    normalized = re.sub(r"\s+", "", normalized)
    normalized = normalized.replace("m", "")
    return normalized


def _quantize_two_decimals(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _decimal_to_string(value: Decimal) -> str:
    quantized = _quantize_two_decimals(value)
    text = format(quantized, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text


@dataclass(frozen=True)
class PlotSizeConversion:
    metric_label: str
    imperial_label: str


def parse_plot_size_meters(raw_value: Optional[str]) -> Optional[tuple[Decimal, Decimal]]:
    if not raw_value:
        return None
    normalized = _sanitize_plot_size_input(raw_value)
    match = PLOT_SIZE_PATTERN.match(normalized)
    if not match:
        return None
    width = Decimal(match.group("width"))
    depth = Decimal(match.group("depth"))
    if width <= 0 or depth <= 0:
        return None
    return width, depth


def format_plot_size_label(dimensions: tuple[Decimal, Decimal], unit_suffix: str) -> str:
    width_text = _decimal_to_string(dimensions[0])
    depth_text = _decimal_to_string(dimensions[1])
    suffix = unit_suffix or ""
    return f"{width_text}{suffix} x {depth_text}{suffix}"


def convert_plot_size_to_feet(dimensions: tuple[Decimal, Decimal]) -> tuple[Decimal, Decimal]:
    width_ft = dimensions[0] * FEET_CONVERSION_FACTOR
    depth_ft = dimensions[1] * FEET_CONVERSION_FACTOR
    return _quantize_two_decimals(width_ft), _quantize_two_decimals(depth_ft)


def build_plot_size_conversion(raw_value: Optional[str]) -> Optional[PlotSizeConversion]:
    dimensions_m = parse_plot_size_meters(raw_value)
    if not dimensions_m:
        return None
    metric_label = format_plot_size_label(dimensions_m, "m")
    dimensions_ft = convert_plot_size_to_feet(dimensions_m)
    imperial_label = format_plot_size_label(dimensions_ft, " ft")
    return PlotSizeConversion(metric_label=metric_label, imperial_label=imperial_label)
