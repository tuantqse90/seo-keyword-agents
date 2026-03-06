"""Structured logging with correlation IDs — pure ASGI middleware."""

import json
import logging
import time
import uuid
from contextvars import ContextVar

correlation_id_var: ContextVar[str] = ContextVar("correlation_id", default="")


class CorrelationIdFilter(logging.Filter):
    def filter(self, record):
        record.correlation_id = correlation_id_var.get("")
        return True


class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "correlation_id": getattr(record, "correlation_id", ""),
        }
        if record.exc_info and record.exc_info[1]:
            log_entry["exception"] = str(record.exc_info[1])
        return json.dumps(log_entry)


def setup_logging():
    """Configure structured JSON logging."""
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    handler.addFilter(CorrelationIdFilter())

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(logging.INFO)

    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


class LoggingMiddleware:
    """Pure ASGI middleware — avoids BaseHTTPMiddleware greenlet issues."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        headers = dict(scope.get("headers", []))
        cid = headers.get(b"x-correlation-id", str(uuid.uuid4())[:8].encode()).decode()
        correlation_id_var.set(cid)

        logger = logging.getLogger("api")
        path = scope.get("path", "")
        method = scope.get("method", "")
        start = time.time()

        logger.info(f"{method} {path}")

        status_code = 0

        async def send_wrapper(message):
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message.get("status", 0)
                # Inject correlation ID header
                headers_list = list(message.get("headers", []))
                headers_list.append((b"x-correlation-id", cid.encode()))
                message = {**message, "headers": headers_list}
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        except Exception as e:
            duration = round((time.time() - start) * 1000, 1)
            logger.error(f"{method} {path} 500 {duration}ms - {e}")
            raise

        duration = round((time.time() - start) * 1000, 1)
        logger.info(f"{method} {path} {status_code} {duration}ms")
