# Tests for contrast_ratio_kit.
#
# We keep these focused on behaviour the implementation actually claims:
# hex parsing (3 and 6 digit, with and without #), luminance, ratio, AA/AAA
# thresholds, and formatting. Float comparisons use a tolerance.

import math
import unittest

from contrast_ratio_kit import (
    relative_luminance,
    contrast_ratio,
    ratio_to_string,
    passes_aa,
    passes_aaa,
    format_ratio_result,
    normalize_hex,
)


_EPS = 1e-6


class TestNormalizeHex(unittest.TestCase):
    def test_six_digit_with_hash(self):
        self.assertEqual(normalize_hex("#FFFFFF"), "#ffffff")

    def test_six_digit_without_hash(self):
        self.assertEqual(normalize_hex("000000"), "#000000")

    def test_three_digit_expands(self):
        self.assertEqual(normalize_hex("#fff"), "#ffffff")

    def test_three_digit_without_hash(self):
        self.assertEqual(normalize_hex("abc"), "#aabbcc")

    def test_strips_whitespace(self):
        self.assertEqual(normalize_hex("  #a1B2c3  "), "#a1b2c3")

    def test_rejects_alpha_form(self):
        with self.assertRaises(ValueError):
            normalize_hex("#11223344")

    def test_rejects_garbage(self):
        with self.assertRaises(ValueError):
            normalize_hex("not-a-color")

    def test_rejects_non_string(self):
        with self.assertRaises(ValueError):
            normalize_hex(123)  # type: ignore[arg-type]


class TestRelativeLuminance(unittest.TestCase):
    def test_black(self):
        self.assertAlmostEqual(relative_luminance("#000000"), 0.0, places=6)

    def test_white(self):
        self.assertAlmostEqual(relative_luminance("#ffffff"), 1.0, places=6)

    def test_known_gray(self):
        # #777 -> (0x77/255)^2.4-ish per channel, known reference is ~0.180
        self.assertTrue(
            abs(relative_luminance("#777777") - 0.184190) < 5e-3
        )


class TestContrastRatio(unittest.TestCase):
    def test_white_on_black_is_21(self):
        r = contrast_ratio("#ffffff", "#000000")
        self.assertTrue(abs(r - 21.0) < _EPS)

    def test_black_on_white_is_21(self):
        r = contrast_ratio("#000000", "#ffffff")
        self.assertTrue(abs(r - 21.0) < _EPS)

    def test_same_color_is_one(self):
        self.assertTrue(abs(contrast_ratio("#123456", "#123456") - 1.0) < _EPS)

    def test_accepts_short_hex(self):
        r = contrast_ratio("#fff", "#000")
        self.assertTrue(abs(r - 21.0) < _EPS)


class TestRatioToString(unittest.TestCase):
    def test_default_two_places(self):
        self.assertEqual(ratio_to_string(7.0), "7.00")

    def test_custom_places(self):
        self.assertEqual(ratio_to_string(4.5, 3), "4.500")

    def test_rejects_non_finite(self):
        with self.assertRaises(ValueError):
            ratio_to_string(float("inf"))


class TestPassesAA(unittest.TestCase):
    def test_white_on_black_passes_normal(self):
        self.assertTrue(passes_aa("#ffffff", "#000000"))

    def test_gray_on_gray_fails_normal(self):
        # ratio ~1, well below 4.5
        self.assertFalse(passes_aa("#777777", "#777777"))

    def test_large_threshold_is_lower(self):
        # #888 on white: ratio ~3.24, passes large (3.0) but not normal (4.5)
        self.assertTrue(passes_aa("#888888", "#ffffff", size="large"))
        self.assertFalse(passes_aa("#888888", "#ffffff", size="normal"))
        # #979797 on white: ratio ~2.85, fails both
        self.assertFalse(passes_aa("#979797", "#ffffff", size="large"))

    def test_invalid_size(self):
        with self.assertRaises(ValueError):
            passes_aa("#fff", "#000", size="medium")


class TestPassesAAA(unittest.TestCase):
    def test_white_on_black_passes_normal(self):
        self.assertTrue(passes_aaa("#ffffff", "#000000"))

    def test_threshold_seven_for_normal(self):
        # #5f5f5f on white is ~6.4, passes AA (4.5) but fails AAA normal (7.0)
        self.assertTrue(passes_aa("#5f5f5f", "#ffffff"))
        self.assertFalse(passes_aaa("#5f5f5f", "#ffffff"))

    def test_large_is_four_point_five(self):
        # #6f6f6f on white is ~4.85, passes AAA-large (4.5) but fails AAA-normal (7.0)
        self.assertTrue(passes_aaa("#6f6f6f", "#ffffff", size="large"))
        self.assertFalse(passes_aaa("#6f6f6f", "#ffffff", size="normal"))

    def test_invalid_size(self):
        with self.assertRaises(ValueError):
            passes_aaa("#fff", "#000", size="huge")


class TestFormatRatioResult(unittest.TestCase):
    def test_format_passes_both(self):
        out = format_ratio_result("#ffffff", "#000000")
        self.assertEqual(out, "ratio=21.00 aa=PASS aaa=PASS")

    def test_format_fails_both(self):
        out = format_ratio_result("#777777", "#777777")
        self.assertEqual(out, "ratio=1.00 aa=FAIL aaa=FAIL")

    def test_format_aa_only(self):
        out = format_ratio_result("#5f5f5f", "#ffffff", size="normal")
        # #5f5f5f on white ~6.4 -> PASS for AA normal, FAIL for AAA normal
        self.assertTrue(out.startswith("ratio=6."))
        self.assertIn("aa=PASS", out)
        self.assertIn("aaa=FAIL", out)

    def test_format_custom_places(self):
        out = format_ratio_result("#ffffff", "#000000", places=3)
        self.assertEqual(out, "ratio=21.000 aa=PASS aaa=PASS")


if __name__ == "__main__":
    unittest.main()
