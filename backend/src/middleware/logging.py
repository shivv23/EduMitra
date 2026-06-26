import re
import logging
import json
from typing import Any, Dict

from src.config.settings import settings

PII_PATTERNS = [
    (re.compile(r'\b\d{10}\b'), "<PHONE>"),           # phone numbers
    (re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'), "<EMAIL>"),
    (re.compile(r'(sk-[a-zA-Z0-9]{20,}|[A-Za-z0-9]{32,})'), "<API_KEY>"),  # API keys
    (re.compile(r'\b\d{12}\b'), "<AADHAAR>"),         # aadhaar-like numbers
]


def redact_pii(message: str) -> str:
    for pattern, replacement in PII_PATTERNS:
        message = pattern.sub(replacement, message)
    return message


class PIIRedactingFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        original = super().format(record)
        return redact_pii(original)


class JSONLogFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_entry: Dict[str, Any] = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": redact_pii(record.getMessage()),
        }
        if record.exc_info and record.exc_info[0]:
            log_entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_entry)


def configure_logging() -> None:
    level = getattr(logging, settings.log_level.upper(), logging.INFO)
    handler = logging.StreamHandler()
    handler.setFormatter(JSONLogFormatter())
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level)

    # Silence noisy libs
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
