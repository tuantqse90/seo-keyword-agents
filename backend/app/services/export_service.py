import csv
import io
import html as html_module

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.report import Report


async def export_csv(db: AsyncSession, report: Report) -> str:
    """Export report data as CSV string."""
    output = io.StringIO()
    writer = csv.writer(output)

    if report.keywords:
        writer.writerow(["Keyword", "Cluster", "Search Volume", "KD", "Intent", "CPC", "Opportunity", "Golden"])
        for kw in report.keywords:
            writer.writerow([
                kw.keyword, kw.cluster, kw.search_volume, kw.keyword_difficulty,
                kw.search_intent, kw.cpc, kw.opportunity_score, kw.is_golden,
            ])
    elif report.competitors:
        writer.writerow(["Name", "URL", "Est. Traffic", "DA"])
        for comp in report.competitors:
            writer.writerow([comp.name, comp.url, comp.estimated_traffic, comp.domain_authority])
    elif report.raw_markdown:
        writer.writerow(["Report Content"])
        writer.writerow([report.raw_markdown])

    return output.getvalue()


MODULE_LABELS = {
    "keywords": "Nghien cuu Tu khoa",
    "competitor": "Phan tich Doi thu",
    "content": "Content Brief",
    "audit": "Kiem tra SEO",
    "full": "Phan tich Day du",
    "strategy": "Chien luoc SEO",
    "fix": "Sua loi nhanh",
}


def _esc(text: str | None) -> str:
    """HTML-escape text safely."""
    if not text:
        return ""
    return html_module.escape(str(text))


async def export_pdf_html(db: AsyncSession, report: Report) -> str:
    """Generate branded HTML for PDF conversion."""
    brand = _esc(settings.brand_name)
    color = settings.brand_color
    module_label = MODULE_LABELS.get(report.module.value, report.module.value)
    date_str = report.created_at.strftime("%d/%m/%Y %H:%M")
    query = _esc(report.input_query)

    html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
@page {{
    size: A4;
    margin: 20mm 15mm 25mm 15mm;
    @bottom-center {{
        content: "{brand} — Trang " counter(page) " / " counter(pages);
        font-size: 9px;
        color: #9ca3af;
    }}
}}
* {{ box-sizing: border-box; }}
body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 0; color: #1f2937; font-size: 13px; line-height: 1.6; }}

/* Cover header */
.cover {{
    background: linear-gradient(135deg, {color}, {color}dd);
    color: white;
    padding: 40px 35px;
    margin: -20mm -15mm 30px -15mm;
    page-break-after: avoid;
}}
.cover h1 {{ margin: 0 0 8px 0; font-size: 28px; font-weight: 700; }}
.cover .subtitle {{ font-size: 16px; opacity: 0.9; margin: 0 0 20px 0; }}
.cover .meta {{ display: flex; gap: 30px; font-size: 13px; opacity: 0.85; }}
.cover .meta span {{ display: inline-block; }}
.brand-logo {{ font-size: 13px; font-weight: 700; letter-spacing: 1px; text-transform: uppercase; opacity: 0.7; margin-bottom: 15px; }}

/* Section headings */
h2 {{
    color: {color};
    font-size: 18px;
    border-bottom: 2px solid {color}33;
    padding-bottom: 6px;
    margin-top: 30px;
}}
h3 {{ color: #374151; font-size: 15px; margin-top: 20px; }}

/* Tables */
table {{ border-collapse: collapse; width: 100%; margin: 15px 0; font-size: 12px; }}
th {{
    background: {color}11;
    color: {color};
    font-weight: 600;
    text-align: left;
    padding: 10px 8px;
    border-bottom: 2px solid {color}33;
}}
td {{ padding: 8px; border-bottom: 1px solid #e5e7eb; }}
tr:nth-child(even) td {{ background: #f9fafb; }}

/* Badges */
.badge {{ padding: 3px 10px; border-radius: 12px; font-size: 11px; font-weight: 600; display: inline-block; }}
.critical {{ background: #fef2f2; color: #dc2626; border: 1px solid #fecaca; }}
.warning {{ background: #fffbeb; color: #d97706; border: 1px solid #fde68a; }}
.info {{ background: #eff6ff; color: #2563eb; border: 1px solid #bfdbfe; }}
.golden {{ background: #fefce8; color: #a16207; border: 1px solid #fde047; }}

/* Score card */
.score-card {{
    text-align: center;
    padding: 25px;
    border-radius: 12px;
    background: linear-gradient(135deg, {color}08, {color}15);
    border: 1px solid {color}22;
    margin: 20px 0;
}}
.score-card .score {{ font-size: 48px; font-weight: 800; color: {color}; }}
.score-card .grade {{ font-size: 20px; color: #6b7280; margin-top: 4px; }}

/* Summary box */
.summary {{
    background: #f0f9ff;
    border-left: 4px solid {color};
    padding: 15px 20px;
    margin: 20px 0;
    border-radius: 0 8px 8px 0;
}}

/* Full analysis */
.analysis-content {{
    background: #f9fafb;
    padding: 20px;
    border-radius: 8px;
    border: 1px solid #e5e7eb;
    white-space: pre-wrap;
    font-family: 'Courier New', monospace;
    font-size: 11px;
    line-height: 1.5;
    word-wrap: break-word;
}}

/* Content brief */
.meta-preview {{
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    padding: 15px;
    margin: 15px 0;
}}
.meta-preview .title {{ color: #1a0dab; font-size: 18px; margin-bottom: 4px; }}
.meta-preview .url {{ color: #006621; font-size: 13px; margin-bottom: 4px; }}
.meta-preview .desc {{ color: #545454; font-size: 13px; }}
</style></head><body>

<!-- Cover -->
<div class="cover">
    <div class="brand-logo">{brand}</div>
    <h1>{query}</h1>
    <p class="subtitle">{module_label}</p>
    <div class="meta">
        <span>Ngay: {date_str}</span>
        <span>Report ID: {_esc(str(report.id)[:8])}...</span>
        <span>Trang thai: {_esc(report.status.value)}</span>
    </div>
</div>
"""

    # Summary
    if report.summary:
        html += f'<div class="summary"><strong>Tom tat:</strong> {_esc(report.summary)}</div>'

    # Keywords section
    if report.keywords:
        golden_count = sum(1 for kw in report.keywords if kw.is_golden)
        html += f"<h2>Tu khoa ({len(report.keywords)} tu khoa"
        if golden_count:
            html += f', {golden_count} golden'
        html += ")</h2>"

        html += "<table><tr><th>Tu khoa</th><th>Cluster</th><th>Volume</th><th>KD</th><th>Intent</th><th>CPC</th><th>Score</th><th></th></tr>"
        for kw in report.keywords:
            golden_badge = '<span class="badge golden">Golden</span>' if kw.is_golden else ""
            html += f"<tr><td><strong>{_esc(kw.keyword)}</strong></td><td>{_esc(kw.cluster)}</td><td>{kw.search_volume or '-'}</td><td>{kw.keyword_difficulty or '-'}</td><td>{_esc(kw.search_intent)}</td><td>{kw.cpc or '-'}</td><td>{kw.opportunity_score or '-'}</td><td>{golden_badge}</td></tr>"
        html += "</table>"

    # Competitors section
    if report.competitors:
        html += f"<h2>Doi thu ({len(report.competitors)})</h2>"
        html += "<table><tr><th>Ten</th><th>URL</th><th>Traffic uoc tinh</th><th>DA</th></tr>"
        for comp in report.competitors:
            html += f"<tr><td><strong>{_esc(comp.name)}</strong></td><td>{_esc(comp.url)}</td><td>{comp.estimated_traffic or '-'}</td><td>{comp.domain_authority or '-'}</td></tr>"
        html += "</table>"

    # Content briefs
    if report.content_briefs:
        for brief in report.content_briefs:
            html += "<h2>Content Brief</h2>"
            if brief.title_tag or brief.meta_description:
                html += '<div class="meta-preview">'
                if brief.title_tag:
                    html += f'<div class="title">{_esc(brief.title_tag)}</div>'
                html += f'<div class="url">{_esc(report.input_query)}</div>'
                if brief.meta_description:
                    html += f'<div class="desc">{_esc(brief.meta_description)}</div>'
                html += '</div>'
            if brief.target_word_count:
                html += f"<p><strong>So tu muc tieu:</strong> {brief.target_word_count}</p>"
            if brief.snippet_strategy:
                html += f"<p><strong>Chien luoc snippet:</strong> {_esc(brief.snippet_strategy)}</p>"

    # Audit section
    if report.audit_results:
        ar = report.audit_results[0]
        html += '<h2>Ket qua kiem tra SEO</h2>'
        html += f'<div class="score-card"><div class="score">{ar.overall_score}/100</div><div class="grade">Grade: {_esc(ar.letter_grade)}</div></div>'

        if ar.issues:
            # Group by severity
            critical = [i for i in ar.issues if i.severity.lower() == "critical"]
            warning = [i for i in ar.issues if i.severity.lower() == "warning"]
            info = [i for i in ar.issues if i.severity.lower() == "info"]

            html += f"<h3>Van de ({len(ar.issues)} van de: {len(critical)} critical, {len(warning)} warning, {len(info)} info)</h3>"
            html += "<table><tr><th>Muc do</th><th>Danh muc</th><th>Van de</th><th>Cach sua</th></tr>"
            for issue in sorted(ar.issues, key=lambda x: {"critical": 0, "warning": 1, "info": 2}.get(x.severity.lower(), 3)):
                html += f'<tr><td><span class="badge {issue.severity.lower()}">{_esc(issue.severity)}</span></td><td>{_esc(issue.category)}</td><td>{_esc(issue.title)}</td><td>{_esc(issue.fix_suggestion)}</td></tr>'
            html += "</table>"

    # Keyword gaps
    if report.keyword_gaps:
        html += f"<h2>Keyword Gaps ({len(report.keyword_gaps)})</h2>"
        html += "<table><tr><th>Tu khoa</th><th>Vi tri muc tieu</th></tr>"
        for gap in report.keyword_gaps:
            html += f"<tr><td>{_esc(gap.keyword)}</td><td>{gap.target_rank or '-'}</td></tr>"
        html += "</table>"

    # Full analysis markdown
    if report.raw_markdown:
        content = _esc(report.raw_markdown[:8000])
        html += f'<h2>Phan tich chi tiet</h2><div class="analysis-content">{content}</div>'

    # Footer
    html += f"""
<div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #e5e7eb; text-align: center; color: #9ca3af; font-size: 11px;">
    <p>Bao cao duoc tao tu dong boi <strong>{brand}</strong> &mdash; {date_str}</p>
    <p>Du lieu SEO mang tinh tham khao. Kiem tra lai truoc khi ap dung.</p>
</div>
</body></html>"""

    return html
