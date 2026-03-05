import json
import re


def extract_json_block(text: str) -> dict | None:
    """Extract the last JSON code block from markdown text."""
    pattern = r"```json\s*\n(.*?)\n\s*```"
    matches = re.findall(pattern, text, re.DOTALL)
    if not matches:
        return None
    try:
        return json.loads(matches[-1])
    except json.JSONDecodeError:
        return None


def parse_markdown_table(text: str) -> list[dict]:
    """Fallback parser: extract data from markdown tables."""
    rows = []
    table_pattern = r"\|(.+)\|"
    lines = re.findall(table_pattern, text)

    if len(lines) < 3:
        return rows

    headers = [h.strip().lower().replace(" ", "_") for h in lines[0].split("|")]

    for line in lines[2:]:  # Skip header separator
        cells = [c.strip() for c in line.split("|")]
        if len(cells) == len(headers):
            row = {}
            for header, cell in zip(headers, cells):
                row[header] = cell
            rows.append(row)

    return rows


def parse_keywords_response(text: str) -> dict:
    """Parse keyword analysis response."""
    data = extract_json_block(text)
    if data and "keywords" in data:
        return data

    # Fallback: try markdown table
    table_data = parse_markdown_table(text)
    if table_data:
        keywords = []
        for row in table_data:
            kw = {
                "keyword": row.get("keyword", ""),
                "cluster": row.get("cluster", ""),
                "search_volume": _to_int(row.get("search_volume") or row.get("volume", "0")),
                "keyword_difficulty": _to_int(row.get("keyword_difficulty") or row.get("kd", "0")),
                "search_intent": row.get("search_intent") or row.get("intent", ""),
                "cpc": _to_float(row.get("cpc", "0")),
                "opportunity_score": _to_int(row.get("opportunity_score") or row.get("opportunity", "0")),
                "is_golden": "golden" in row.get("notes", "").lower() or row.get("is_golden", "").lower() == "true",
            }
            keywords.append(kw)
        return {"keywords": keywords, "summary": "Parsed from markdown table"}

    return {"keywords": [], "summary": "Could not parse structured data"}


def parse_competitor_response(text: str) -> dict:
    """Parse competitor analysis response."""
    data = extract_json_block(text)
    if data and "competitors" in data:
        return data
    return {"competitors": [], "keyword_gaps": [], "summary": "Could not parse structured data"}


def parse_content_response(text: str) -> dict:
    """Parse content brief response."""
    data = extract_json_block(text)
    if data:
        return data
    return {"summary": "Could not parse structured data"}


def parse_audit_response(text: str) -> dict:
    """Parse audit response."""
    data = extract_json_block(text)
    if data:
        return data
    return {"overall_score": None, "issues": [], "summary": "Could not parse structured data"}


def _to_int(val: str) -> int:
    try:
        return int(re.sub(r"[^\d]", "", str(val)))
    except (ValueError, TypeError):
        return 0


def _to_float(val: str) -> float:
    try:
        return float(re.sub(r"[^\d.]", "", str(val)))
    except (ValueError, TypeError):
        return 0.0
