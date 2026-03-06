import re
import html


def is_valid_url(url: str) -> bool:
    pattern = re.compile(
        r"^https?://"
        r"(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+"
        r"[a-zA-Z]{2,}"
        r"(?:/[^\s]*)?$"
    )
    return bool(pattern.match(url))


def normalize_url(url: str) -> str:
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    return url.rstrip("/")


def sanitize_input(text: str, max_length: int = 1000) -> str:
    """Strip HTML tags, escape special chars, enforce length limit."""
    text = text.strip()
    text = re.sub(r"<[^>]+>", "", text)
    text = html.escape(text)
    return text[:max_length]


def validate_query(query: str) -> str:
    """Validate and sanitize analysis query input."""
    query = query.strip()
    if not query:
        raise ValueError("Query cannot be empty")
    if len(query) > 2000:
        raise ValueError("Query too long (max 2000 characters)")
    return sanitize_input(query, max_length=2000)
