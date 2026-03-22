"""Unit tests for utils.input_validation."""
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from utils.input_validation import validate_user_target_input  # noqa: E402


@pytest.mark.parametrize(
    "value",
    [
        "https://example.com/path",
        "example.com",
        "github.com/org/repo",
        "https://8.8.8.8",
    ],
)
def test_validate_accepts_public_targets(value):
    normalized, err = validate_user_target_input(value, allow_private_hosts=False)
    assert err is None
    assert normalized == value.strip()


@pytest.mark.parametrize(
    "value",
    [
        "http://127.0.0.1/",
        "https://localhost/foo",
        "http://10.0.0.1/",
        "192.168.0.1",
        "http://[::1]/",
    ],
)
def test_validate_rejects_private_and_loopback_by_default(value):
    normalized, err = validate_user_target_input(value, allow_private_hosts=False)
    assert normalized is None
    assert err is not None


def test_validate_allows_private_when_flag_true():
    normalized, err = validate_user_target_input(
        "http://192.168.1.1/", allow_private_hosts=True
    )
    assert err is None
    assert normalized == "http://192.168.1.1/"


def test_validate_always_blocks_metadata_ip():
    normalized, err = validate_user_target_input(
        "http://169.254.169.254/latest/meta-data/", allow_private_hosts=True
    )
    assert normalized is None
    assert "metadata" in err.lower()


def test_validate_always_blocks_metadata_hostname():
    normalized, err = validate_user_target_input(
        "http://metadata.google.internal/computeMetadata/v1/",
        allow_private_hosts=True,
    )
    assert normalized is None


def test_validate_rejects_non_string():
    assert validate_user_target_input(123)[1] is not None


def test_validate_rejects_empty_and_oversize():
    assert validate_user_target_input("   ")[1] is not None
    assert validate_user_target_input("x" * 5000, max_len=10)[1] is not None


def test_validate_rejects_null_byte():
    assert validate_user_target_input("evil.com\0.evil")[1] is not None


def test_validate_localhost_in_path_allowed_when_host_public():
    """Substring 'localhost' in path must not false-positive."""
    normalized, err = validate_user_target_input(
        "https://example.com/docs?q=localhost",
        allow_private_hosts=False,
    )
    assert err is None
    assert normalized is not None
