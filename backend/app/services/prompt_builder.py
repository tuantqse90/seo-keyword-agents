from pathlib import Path

PROMPT_FILE = Path(__file__).resolve().parent.parent.parent.parent / "seo-agent-prompt.txt"


def load_system_prompt() -> str:
    return PROMPT_FILE.read_text(encoding="utf-8")


def build_keyword_prompt(query: str) -> str:
    return f"""/keywords {query}

IMPORTANT: After your analysis, output a JSON block fenced with ```json that contains a "keywords" array. Each keyword object must have:
- "keyword": string
- "cluster": string
- "search_volume": number
- "keyword_difficulty": number (1-100)
- "search_intent": "informational" | "transactional" | "navigational" | "commercial"
- "cpc": number
- "opportunity_score": number (1-10)
- "is_golden": boolean

Also include a "summary" field with a brief text summary of findings.

Output the JSON block at the END of your response, after all markdown analysis."""


def build_competitor_prompt(query: str) -> str:
    return f"""/competitor {query}

IMPORTANT: After your analysis, output a JSON block fenced with ```json that contains:
- "competitors": array of objects with "name", "url", "estimated_traffic", "domain_authority", "top_keywords" (array of strings), "strengths" (array of strings), "weaknesses" (array of strings)
- "keyword_gaps": array of objects with "keyword", "target_rank" (null if not ranking), "competitor_ranks" (object mapping competitor name to rank)
- "summary": brief text summary

Output the JSON block at the END of your response."""


def build_content_prompt(query: str) -> str:
    return f"""/content {query}

IMPORTANT: After your analysis, output a JSON block fenced with ```json that contains:
- "title_tag": string (under 60 chars)
- "meta_description": string (under 155 chars)
- "target_word_count": number
- "outline": array of objects with "heading", "level" (2 or 3), "key_points" (array of strings)
- "lsi_keywords": array of strings (15-20 terms)
- "snippet_strategy": string
- "eeat_signals": array of strings
- "summary": brief text summary

Output the JSON block at the END of your response."""


def build_audit_prompt(query: str) -> str:
    return f"""/audit {query}

IMPORTANT: After your analysis, output a JSON block fenced with ```json that contains:
- "overall_score": number (0-100)
- "letter_grade": string
- "quick_wins": array of objects with "title", "description", "effort_level"
- "tech_checklist": object mapping check names to boolean pass/fail
- "issues": array of objects with "severity" ("Critical"|"Warning"|"Info"), "category", "title", "description", "fix_suggestion", "code_snippet" (optional), "effort_level" ("[Quick Win]"|"[Medium Effort]"|"[Strategic Investment]")
- "summary": brief text summary

Output the JSON block at the END of your response."""


PROMPT_BUILDERS = {
    "keywords": build_keyword_prompt,
    "competitor": build_competitor_prompt,
    "content": build_content_prompt,
    "audit": build_audit_prompt,
}
