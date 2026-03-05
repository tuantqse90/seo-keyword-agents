"""Tests for service helper functions."""
import re
from app.services.keyword_service import _safe_int, _safe_float


class TestSafeInt:
    def test_none(self):
        assert _safe_int(None) is None

    def test_int(self):
        assert _safe_int(42) == 42

    def test_string_number(self):
        assert _safe_int("123") == 123

    def test_string_with_commas(self):
        assert _safe_int("1,234,567") == 1234567

    def test_string_with_suffix(self):
        assert _safe_int("500M+") == 500

    def test_string_with_prefix(self):
        assert _safe_int("~2000") == 2000

    def test_empty_string(self):
        assert _safe_int("") is None

    def test_no_digits(self):
        assert _safe_int("N/A") is None

    def test_float_string(self):
        # Should strip the dot and parse digits
        assert _safe_int("3.5") == 35  # strips non-digit chars


class TestSafeFloat:
    def test_none(self):
        assert _safe_float(None) is None

    def test_int(self):
        assert _safe_float(42) == 42.0

    def test_float(self):
        assert _safe_float(3.14) == 3.14

    def test_string_dollar(self):
        assert _safe_float("$2.50") == 2.50

    def test_string_plain(self):
        assert _safe_float("1.23") == 1.23

    def test_empty(self):
        assert _safe_float("") is None

    def test_no_digits(self):
        assert _safe_float("N/A") is None
