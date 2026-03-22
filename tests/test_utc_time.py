"""Tests for timezone-aware UTC helpers."""
from pathlib import Path
import re
import sys
from datetime import datetime

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from utils.utc_time import utc_now, utc_now_iso  # noqa: E402


def test_utc_now_is_timezone_aware():
    now = utc_now()
    assert now.tzinfo is not None
    assert now.utcoffset() is not None
    assert now.utcoffset().total_seconds() == 0


def test_utc_now_iso_matches_z_suffix_pattern():
    s = utc_now_iso()
    assert re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?Z$", s), s


def test_utc_now_iso_roundtrips_as_utc():
    s = utc_now_iso()
    # fromisoformat does not accept trailing Z before 3.11 in all cases; normalize
    normalized = s[:-1] + "+00:00" if s.endswith("Z") else s
    parsed = datetime.fromisoformat(normalized)
    assert parsed.tzinfo is not None


def test_utc_now_iso_stable_suffix():
    assert utc_now_iso().endswith("Z")
