"""Tests for the response parser."""
from app.services.parser import (
    extract_json_block,
    parse_markdown_table,
    parse_keywords_response,
    parse_competitor_response,
    parse_content_response,
    parse_audit_response,
    _to_int,
    _to_float,
)


class TestExtractJsonBlock:
    def test_extracts_json(self):
        text = 'Some text\n```json\n{"key": "value"}\n```\nMore text'
        result = extract_json_block(text)
        assert result == {"key": "value"}

    def test_extracts_last_json_block(self):
        text = '```json\n{"first": 1}\n```\nMiddle\n```json\n{"second": 2}\n```'
        result = extract_json_block(text)
        assert result == {"second": 2}

    def test_returns_none_for_no_json(self):
        assert extract_json_block("No json here") is None

    def test_returns_none_for_invalid_json(self):
        text = '```json\n{invalid json}\n```'
        assert extract_json_block(text) is None

    def test_handles_multiline_json(self):
        text = '```json\n{\n  "keywords": [\n    {"keyword": "test"}\n  ]\n}\n```'
        result = extract_json_block(text)
        assert result["keywords"][0]["keyword"] == "test"


class TestParseMarkdownTable:
    def test_parses_simple_table(self):
        text = """| Name | Value |
| --- | --- |
| foo | 123 |
| bar | 456 |"""
        rows = parse_markdown_table(text)
        assert len(rows) == 2
        assert rows[0]["name"] == "foo"
        assert rows[1]["value"] == "456"

    def test_returns_empty_for_no_table(self):
        assert parse_markdown_table("No table here") == []

    def test_returns_empty_for_header_only(self):
        text = "| Name | Value |\n| --- | --- |"
        assert parse_markdown_table(text) == []


class TestToInt:
    def test_plain_number(self):
        assert _to_int("123") == 123

    def test_with_commas(self):
        assert _to_int("1,234") == 1234

    def test_with_text(self):
        assert _to_int("500K+") == 500

    def test_empty(self):
        assert _to_int("") == 0

    def test_no_digits(self):
        assert _to_int("abc") == 0


class TestToFloat:
    def test_plain_float(self):
        assert _to_float("1.23") == 1.23

    def test_with_dollar(self):
        assert _to_float("$3.50") == 3.50

    def test_empty(self):
        assert _to_float("") == 0.0


class TestParseKeywordsResponse:
    def test_parses_json_block(self):
        text = """Analysis here.
```json
{
  "keywords": [
    {"keyword": "seo tool", "cluster": "tools", "search_volume": 1000, "keyword_difficulty": 45, "search_intent": "commercial", "cpc": 2.5, "opportunity_score": 8, "is_golden": true}
  ],
  "summary": "Good keywords"
}
```"""
        result = parse_keywords_response(text)
        assert len(result["keywords"]) == 1
        assert result["keywords"][0]["keyword"] == "seo tool"
        assert result["keywords"][0]["is_golden"] is True
        assert result["summary"] == "Good keywords"

    def test_fallback_to_table(self):
        text = """| Keyword | Volume | KD | Intent | CPC | Opportunity |
| --- | --- | --- | --- | --- | --- |
| seo tips | 5000 | 30 | informational | 1.20 | 7 |"""
        result = parse_keywords_response(text)
        assert len(result["keywords"]) == 1
        assert result["keywords"][0]["keyword"] == "seo tips"

    def test_returns_empty_on_no_data(self):
        result = parse_keywords_response("Just some text with no data")
        assert result["keywords"] == []


class TestParseCompetitorResponse:
    def test_parses_json(self):
        text = """```json
{
  "competitors": [{"name": "Rival Co", "url": "https://rival.com", "estimated_traffic": 50000, "domain_authority": 60}],
  "keyword_gaps": [{"keyword": "seo", "target_rank": null, "competitor_ranks": {"Rival Co": 3}}],
  "summary": "Analysis done"
}
```"""
        result = parse_competitor_response(text)
        assert len(result["competitors"]) == 1
        assert result["competitors"][0]["name"] == "Rival Co"
        assert len(result["keyword_gaps"]) == 1

    def test_returns_empty_on_no_data(self):
        result = parse_competitor_response("No structured data")
        assert result["competitors"] == []
        assert result["keyword_gaps"] == []


class TestParseContentResponse:
    def test_parses_json(self):
        text = """```json
{
  "title_tag": "Best SEO Tips 2024",
  "meta_description": "Learn the best SEO tips",
  "target_word_count": 2500,
  "outline": [{"heading": "Intro", "level": 2, "key_points": ["point1"]}],
  "lsi_keywords": ["optimization", "ranking"],
  "snippet_strategy": "paragraph",
  "eeat_signals": ["expert author"],
  "summary": "Brief created"
}
```"""
        result = parse_content_response(text)
        assert result["title_tag"] == "Best SEO Tips 2024"
        assert result["target_word_count"] == 2500
        assert len(result["lsi_keywords"]) == 2

    def test_returns_fallback(self):
        result = parse_content_response("No data")
        assert "summary" in result


class TestParseAuditResponse:
    def test_parses_json(self):
        text = """```json
{
  "overall_score": 75,
  "letter_grade": "B",
  "quick_wins": [{"title": "Fix meta", "description": "Add meta desc", "effort_level": "[Quick Win]"}],
  "tech_checklist": {"robots.txt": true, "sitemap": false},
  "issues": [{"severity": "Critical", "category": "Meta", "title": "Missing meta", "description": "No meta desc", "fix_suggestion": "Add it", "effort_level": "[Quick Win]"}],
  "summary": "Audit done"
}
```"""
        result = parse_audit_response(text)
        assert result["overall_score"] == 75
        assert result["letter_grade"] == "B"
        assert len(result["issues"]) == 1
        assert result["issues"][0]["severity"] == "Critical"

    def test_returns_fallback(self):
        result = parse_audit_response("No data")
        assert result["overall_score"] is None
