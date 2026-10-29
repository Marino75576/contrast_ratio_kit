# contrast_ratio_kit
# A focused library for computing WCAG contrast ratios between two colors.
#
# We export a small, deliberate surface so users can rely on stable names.

from contrast_ratio_kit.core import (
    relative_luminance,
    contrast_ratio,
    ratio_to_string,
    passes_aa,
    passes_aaa,
    format_ratio_result,
    normalize_hex,
)

__all__ = [
    "relative_luminance",
    "contrast_ratio",
    "ratio_to_string",
    "passes_aa",
    "passes_aaa",
    "format_ratio_result",
    "normalize_hex",
]

__version__ = "0.1.0"
