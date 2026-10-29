# Core implementation of contrast_ratio_kit.
#
# All math follows the WCAG 2.x definition of relative luminance and contrast ratio.
# We use Python's built-in math module to avoid any third-party dependency.

import math
import re
from typing import Tuple


_HEX3_RE = re.compile(r"^#?([0-9a-fA-F])([0-9a-fA-F])([0-9a-fA-F])$")
_HEX6_RE = re.compile(r"^#?([0-9a-fA-F]{2})([0-9a-fA-F]{2})([0-9a-fA-F]{2})$")


def normalize_hex(s: str) -> str:
    """Return a canonical #rrggbb lowercase form of the input hex color.

    Accepts #rgb, rgb, #rrggbb, or rrggbb. Raises ValueError if the input
    does not match one of those shapes. We intentionally do NOT support
    4- or 8-digit alpha forms: the WCAG contrast ratio is defined on color
    channels only, and silently dropping an alpha component would mislead
    the caller into thinking they measured something they did not.
    """
    if not isinstance(s, str):
        raise ValueError("color must be a string")
    m = _HEX6_RE.match(s.strip())
    if m:
        return "#" + "".join(part.lower() for part in m.groups())
    m = _HEX3_RE.match(s.strip())
    if m:
        return "#" + "".join(c.lower() * 2 for c in m.groups())
    raise ValueError("invalid hex color: {!r}".format(s))


def _hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    normalized = normalize_hex(hex_color)
    # normalize_hex guarantees the #rrggbb form.
    return (
        int(normalized[1:3], 16),
        int(normalized[3:5], 16),
        int(normalized[5:7], 16),
    )


def _channel_luminance(channel_value: int) -> float:
    # WCAG defines the channel transform on a 0..1 sRGB value.
    v = channel_value / 255.0
    if v <= 0.03928:
        # The 0.03928 threshold comes from the sRGB->linear piecewise model
        # used by WCAG 2.x. Some implementations use 0.04045; we follow the
        # WCAG published definition directly.
        return v / 12.92
    return ((v + 0.055) / 1.055) ** 2.4


def relative_luminance(hex_color: str) -> float:
    """Compute the WCAG relative luminance of an sRGB hex color.

    Returns a float in the range [0.0, 1.0] where 0 is black and 1 is white.
    """
    r, g, b = _hex_to_rgb(hex_color)
    return (
        0.2126 * _channel_luminance(r)
        + 0.7152 * _channel_luminance(g)
        + 0.0722 * _channel_luminance(b)
    )


def contrast_ratio(fg: str, bg: str) -> float:
    """Compute the WCAG contrast ratio between two hex colors.

    The result is always >= 1.0 because we take the lighter luminance as
    the numerator and add 0.05 to both (the 0.05 correction accounts for
    ambient flare / display reflection as defined by WCAG).
    """
    l1 = relative_luminance(fg)
    l2 = relative_luminance(bg)
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


def ratio_to_string(ratio: float, places: int = 2) -> str:
    """Format a contrast ratio with the given number of decimal places.

    We round half-to-even via Python's built-in format to avoid introducing
    a custom rounding rule.
    """
    if not math.isfinite(ratio):
        raise ValueError("ratio must be a finite number")
    return "{:.{}f}".format(ratio, places)


def _threshold_for(size: str) -> float:
    size = size.lower().strip()
    if size == "normal":
        return 4.5
    if size == "large":
        return 3.0
    raise ValueError("size must be 'normal' or 'large', got {!r}".format(size))


def passes_aa(fg: str, bg: str, size: str = "normal") -> bool:
    """Return True if the fg/bg pair meets the WCAG AA threshold.

    size may be 'normal' (default 4.5:1) or 'large' (3.0:1).
    """
    threshold = _threshold_for(size)
    return contrast_ratio(fg, bg) >= threshold


def passes_aaa(fg: str, bg: str, size: str = "normal") -> bool:
    """Return True if the fg/bg pair meets the WCAG AAA threshold.

    AAA thresholds are 7.0:1 for normal text and 4.5:1 for large text.
    """
    size = size.lower().strip()
    if size == "normal":
        return contrast_ratio(fg, bg) >= 7.0
    if size == "large":
        return contrast_ratio(fg, bg) >= 4.5
    raise ValueError("size must be 'normal' or 'large', got {!r}".format(size))


def format_ratio_result(fg: str, bg: str, size: str = "normal", places: int = 2) -> str:
    """Return a human-readable summary string.

    Example output::

        ratio=7.00 aa=PASS aaa=PASS

    The values are computed from the actual fg/bg pair. The leading
    'ratio=' field is fixed so callers can parse on the first token if
    they need to.
    """
    r = contrast_ratio(fg, bg)
    aa = "PASS" if r >= _threshold_for(size) else "FAIL"
    aaa = "PASS" if passes_aaa(fg, bg, size) else "FAIL"
    return "ratio={} aa={} aaa={}".format(ratio_to_string(r, places), aa, aaa)
