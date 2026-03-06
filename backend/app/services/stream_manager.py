"""Centralized stream manager with TTL cleanup for abandoned queues."""

import asyncio
import logging
import time

logger = logging.getLogger("app.streams")

STREAM_TTL = 300  # 5 minutes — auto-cleanup abandoned streams

_streams: dict[str, asyncio.Queue] = {}
_stream_created: dict[str, float] = {}
_cleanup_task: asyncio.Task | None = None


def create_stream(report_id: str) -> asyncio.Queue:
    queue = asyncio.Queue()
    _streams[report_id] = queue
    _stream_created[report_id] = time.time()
    return queue


def get_stream(report_id: str) -> asyncio.Queue | None:
    return _streams.get(report_id)


def remove_stream(report_id: str):
    _streams.pop(report_id, None)
    _stream_created.pop(report_id, None)


async def _cleanup_loop():
    """Periodically remove abandoned streams older than TTL."""
    while True:
        await asyncio.sleep(60)
        now = time.time()
        expired = [
            rid for rid, created in _stream_created.items()
            if now - created > STREAM_TTL
        ]
        for rid in expired:
            logger.warning(f"Cleaning up abandoned stream: {rid}")
            remove_stream(rid)
        if expired:
            logger.info(f"Cleaned {len(expired)} abandoned stream(s). Active: {len(_streams)}")


def start_cleanup():
    global _cleanup_task
    _cleanup_task = asyncio.create_task(_cleanup_loop())


def stop_cleanup():
    global _cleanup_task
    if _cleanup_task:
        _cleanup_task.cancel()
        _cleanup_task = None
