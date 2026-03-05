"""Tests for validators."""
from app.utils.validators import is_valid_url, normalize_url


class TestIsValidUrl:
    def test_valid_https(self):
        assert is_valid_url("https://example.com") is True

    def test_valid_http(self):
        assert is_valid_url("http://example.com") is True

    def test_valid_with_path(self):
        assert is_valid_url("https://example.com/page/sub") is True

    def test_invalid_no_protocol(self):
        assert is_valid_url("example.com") is False

    def test_invalid_empty(self):
        assert is_valid_url("") is False

    def test_invalid_just_text(self):
        assert is_valid_url("not a url") is False


class TestNormalizeUrl:
    def test_adds_https(self):
        assert normalize_url("example.com") == "https://example.com"

    def test_keeps_existing_https(self):
        assert normalize_url("https://example.com") == "https://example.com"

    def test_keeps_existing_http(self):
        assert normalize_url("http://example.com") == "http://example.com"

    def test_strips_trailing_slash(self):
        assert normalize_url("https://example.com/") == "https://example.com"
