"""
Simple tests for crypto_reporter.py
"""
import pytest
from src.crypto_reporter import (
    validate_severity,
    validate_jwk_public_key,
    hash_org_id,
    create_report,
    build_submission,
    VALID_SEVERITIES
)


def test_validate_severity_valid():
    for s in VALID_SEVERITIES:
        assert validate_severity(s) == s


def test_validate_severity_uppercase():
    assert validate_severity("CRITICAL") == "critical"


def test_validate_severity_invalid():
    with pytest.raises(ValueError):
        validate_severity("unknown")


def test_validate_jwk_rejects_private_key():
    fake_private = {"kty": "RSA", "n": "abc", "e": "AQAB", "d": "secret"}
    assert validate_jwk_public_key(fake_private) is False


def test_validate_jwk_rejects_missing_fields():
    assert validate_jwk_public_key({"kty": "RSA"}) is False


def test_validate_jwk_rejects_non_rsa():
    assert validate_jwk_public_key({"kty": "EC", "n": "x", "e": "y"}) is False


def test_validate_jwk_valid():
    valid = {"kty": "RSA", "n": "abc123", "e": "AQAB"}
    assert validate_jwk_public_key(valid) is True


def test_hash_org_id_full_length():
    result = hash_org_id("test-org")
    assert len(result) == 64 


def test_hash_org_id_consistent():
    assert hash_org_id("org-1") == hash_org_id("org-1")


def test_hash_org_id_different_orgs():
    assert hash_org_id("org-1") != hash_org_id("org-2")


def test_create_report_structure():
    report = create_report(
        title="Test Vuln",
        description="Test description",
        severity="high",
        affected_systems=["System A"]
    )
    assert report["version"] == "2.0"
    assert report["data"]["severity"] == "high"
    assert report["data"]["title"] == "Test Vuln"


def test_build_submission_uses_uuid():
    import uuid
    submission = build_submission("encrypted", "org-123", "fingerprint-abc")
    assert submission["org_id_hash"] == hash_org_id("org-123")
    uuid.UUID(submission["submission_id"])


def test_build_submission_no_plaintext_org_id():
    submission = build_submission("encrypted", "org-123", "fingerprint-abc")
    assert "org_id" not in submission
    assert "org-123" not in str(submission)