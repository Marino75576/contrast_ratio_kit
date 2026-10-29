# contrast_ratio_kit

A small Python library for computing WCAG 2.x contrast ratios between two hex colors and checking pass/fail against AA and AAA thresholds.

```python
from contrast_ratio_kit import (
    contrast_ratio,
    passes_aa,
    passes_aaa,
    format_ratio_result,
)

contrast_ratio("#ffffff", "#000000")   # -> 21.0
passes_aa("#777777", "#ffffff")        # -> False
passes_aaa("#ffffff", "#000000")       # -> True
format_ratio_result("#ffffff", "#000000")  # -> 'ratio=21.00 aa=PASS aaa=PASS'
```

## Why this exists

The WCAG contrast ratio is a short, well-defined formula, but the details bite: the sRGB channel transform uses a piecewise function, both luminances get a +0.05 correction, and AA vs AAA thresholds differ for normal and large text. This library implements exactly that computation with no dependencies, so it can run anywhere Python runs.

The trade-off: it only accepts hex colors (`#rgb` or `#rrggbb`). It does not parse `rgb()`/`hsl()` strings, named colors, or alpha forms. If you need those, convert upstream. Alpha is rejected outright because the WCAG ratio is defined on opaque colors; silently dropping the alpha channel would give a misleading number.

## Edge cases worth knowing

- `contrast_ratio("#fff", "#fff")` returns `1.0`, the minimum possible ratio. Same color always passes nothing.
- `size="large"` lowers the AA bar to 3.0 and the AAA bar to 4.5. Pass `size="normal"` (the default) for the standard text thresholds.
- `ratio_to_string` rounds half-to-even via Python's built-in formatting; `21.0` formats as `"21.00"`, not `"21.0"`.
- Inputs are stripped of surrounding whitespace; `"  #abc  "` is accepted.

## Exported names

- `normalize_hex(s) -> str`
- `relative_luminance(hex_color) -> float`
- `contrast_ratio(fg, bg) -> float`
- `ratio_to_string(ratio, places=2) -> str`
- `passes_aa(fg, bg, size="normal") -> bool`
- `passes_aaa(fg, bg, size="normal") -> bool`
- `format_ratio_result(fg, bg, size="normal", places=2) -> str`

## Running the tests

```
PYTHONPATH=src python -m unittest discover -s tests
```
