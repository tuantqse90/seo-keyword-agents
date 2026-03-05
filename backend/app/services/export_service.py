import csv
import io

from sqlalchemy.ext.asyncio import AsyncSession

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


async def export_pdf_html(db: AsyncSession, report: Report) -> str:
    """Generate HTML for PDF conversion."""
    html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
body {{ font-family: Arial, sans-serif; margin: 40px; color: #333; }}
h1 {{ color: #1a56db; }}
table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
th {{ background: #f8f9fa; }}
.badge {{ padding: 2px 8px; border-radius: 4px; font-size: 12px; }}
.critical {{ background: #fee2e2; color: #dc2626; }}
.warning {{ background: #fef3c7; color: #d97706; }}
.info {{ background: #dbeafe; color: #2563eb; }}
</style></head><body>
<h1>SEO Report: {report.input_query}</h1>
<p>Module: {report.module.value} | Date: {report.created_at.strftime('%Y-%m-%d %H:%M')}</p>
"""

    if report.keywords:
        html += "<h2>Keywords</h2><table><tr><th>Keyword</th><th>Cluster</th><th>Volume</th><th>KD</th><th>Intent</th><th>CPC</th><th>Score</th><th>Golden</th></tr>"
        for kw in report.keywords:
            golden = "Yes" if kw.is_golden else ""
            html += f"<tr><td>{kw.keyword}</td><td>{kw.cluster or ''}</td><td>{kw.search_volume or ''}</td><td>{kw.keyword_difficulty or ''}</td><td>{kw.search_intent or ''}</td><td>{kw.cpc or ''}</td><td>{kw.opportunity_score or ''}</td><td>{golden}</td></tr>"
        html += "</table>"

    if report.audit_results:
        ar = report.audit_results[0]
        html += f"<h2>Audit Score: {ar.overall_score}/100 ({ar.letter_grade})</h2>"
        if ar.issues:
            html += "<h3>Issues</h3><table><tr><th>Severity</th><th>Category</th><th>Title</th><th>Fix</th></tr>"
            for issue in ar.issues:
                html += f'<tr><td><span class="badge {issue.severity.lower()}">{issue.severity}</span></td><td>{issue.category}</td><td>{issue.title}</td><td>{issue.fix_suggestion or ""}</td></tr>'
            html += "</table>"

    if report.raw_markdown:
        html += f"<h2>Full Analysis</h2><pre>{report.raw_markdown[:5000]}</pre>"

    html += "</body></html>"
    return html
