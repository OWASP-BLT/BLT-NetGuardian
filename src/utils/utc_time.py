"""Timezone-aware UTC helpers.

``datetime.utcnow()`` is deprecated (Python 3.12+) and scheduled for removal.
Use these helpers for consistent, timezone-aware UTC timestamps in APIs and storage.
"""
from __future__ import annotations

from datetime import datetime, timezone


def utc_now() -> datetime:
    """Current instant in UTC (timezone-aware)."""
    return datetime.now(timezone.utc)


def utc_now_iso() -> str:
    """UTC instant as ISO 8601 with ``Z`` suffix (JSON / D1 friendly)."""
    return utc_now().isoformat().replace("+00:00", "Z")
