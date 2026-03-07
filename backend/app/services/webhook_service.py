"""Webhook notification service for Slack/Discord integration."""

import logging
import httpx

from app.config import settings

logger = logging.getLogger(__name__)


async def send_webhook(payload: dict) -> bool:
    """Send a webhook notification. Returns True if successful."""
    url = settings.webhook_url
    if not url:
        return False

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            # Discord and Slack both accept {"content": "..."} or {"text": "..."}
            if "discord.com" in url:
                resp = await client.post(url, json=payload)
            else:
                # Slack format
                resp = await client.post(url, json=payload)

            if resp.status_code < 300:
                logger.info(f"Webhook sent successfully to {url[:40]}...")
                return True
            else:
                logger.warning(f"Webhook returned {resp.status_code}: {resp.text[:200]}")
                return False
    except Exception as e:
        logger.error(f"Webhook failed: {e}")
        return False


def _format_slack_message(title: str, fields: list[tuple[str, str]], color: str = "#2563eb", url: str | None = None) -> dict:
    """Format a Slack-compatible webhook message."""
    attachment = {
        "color": color,
        "title": title,
        "fields": [{"title": k, "value": v, "short": True} for k, v in fields],
    }
    if url:
        attachment["title_link"] = url
    return {"attachments": [attachment]}


def _format_discord_message(title: str, fields: list[tuple[str, str]], color: int = 0x2563EB, url: str | None = None) -> dict:
    """Format a Discord webhook message."""
    embed = {
        "title": title,
        "color": color,
        "fields": [{"name": k, "value": v, "inline": True} for k, v in fields],
    }
    if url:
        embed["url"] = url
    return {"embeds": [embed]}


def _build_payload(title: str, fields: list[tuple[str, str]], color_hex: str = "#2563eb", url: str | None = None) -> dict:
    """Build webhook payload based on configured URL type."""
    webhook_url = settings.webhook_url
    if "discord.com" in webhook_url:
        color_int = int(color_hex.lstrip("#"), 16)
        return _format_discord_message(title, fields, color_int, url)
    else:
        return _format_slack_message(title, fields, color_hex, url)


async def notify_report_completed(module: str, query: str, report_id: str, summary: str | None = None):
    """Send webhook when analysis completes."""
    fields = [
        ("Module", module.upper()),
        ("Query", query),
        ("Report ID", report_id[:8] + "..."),
    ]
    if summary:
        fields.append(("Summary", summary[:200]))

    payload = _build_payload(
        title="SEO Analysis Completed",
        fields=fields,
        color_hex="#22c55e",
    )
    await send_webhook(payload)


async def notify_report_failed(module: str, query: str, error: str):
    """Send webhook when analysis fails."""
    fields = [
        ("Module", module.upper()),
        ("Query", query),
        ("Error", error[:200]),
    ]
    payload = _build_payload(
        title="SEO Analysis Failed",
        fields=fields,
        color_hex="#ef4444",
    )
    await send_webhook(payload)
