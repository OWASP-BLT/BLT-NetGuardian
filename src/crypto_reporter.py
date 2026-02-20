"""
Workers-compatible Zero-Trust Vulnerability Reporter

The original secure_reporter.py used python-gnupg which needs GPG
binaries and filesystem access. Cloudflare Workers has neither.
This uses Web Crypto API instead - no dependencies, runs in Workers.

Author: Jashwanth (OWASP BLT-NetGuardian contributor)
"""
import json
import hashlib
from datetime import datetime


VALID_SEVERITIES = {"critical", "high", "medium", "low", "info"}


def validate_severity(severity: str) -> str:
    """Normalize and validate severity level."""
    normalized = severity.lower().strip()
    if normalized not in VALID_SEVERITIES:
        raise ValueError(f"Invalid severity '{severity}'. Must be one of: {VALID_SEVERITIES}")
    return normalized


def create_report(title, description, severity, affected_systems,
                  remediation="", cve_ids=None, additional_data=None):
    """Create a structured vulnerability report ready for encryption."""
    return {
        "version": "2.0",
        "report_type": "vulnerability",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "data": {
            "title": title,
            "description": description,
            "severity": validate_severity(severity),
            "affected_systems": affected_systems,
            "remediation": remediation,
            "cve_ids": cve_ids or [],
            "additional_data": additional_data or {},
            "discovery_timestamp": datetime.utcnow().isoformat() + "Z"
        }
    }


def validate_jwk_public_key(jwk: dict) -> bool:
    """Check that a JWK public key has the required RSA-OAEP fields."""
    if not isinstance(jwk, dict):
        return False
    required = {"kty", "n", "e"}
    if not required.issubset(jwk.keys()):
        return False
    if jwk.get("kty") != "RSA":
        return False
    return True


def prepare_payload(report: dict) -> str:
    """Serialize report to JSON string ready for encryption."""
    return json.dumps(report, separators=(',', ':'))


def build_submission(encrypted_data: str, org_id: str, key_fingerprint: str) -> dict:
    """
    Build the final submission after encryption.
    Only metadata is stored - encrypted payload goes to the org.
    """
    submission_id = hashlib.sha256(
        (org_id + encrypted_data[:32]).encode()
    ).hexdigest()[:16]

    return {
        "submission_id": submission_id,
        "org_id": org_id,
        "key_fingerprint": key_fingerprint,
        "encrypted_payload": encrypted_data,
        "submitted_at": datetime.utcnow().isoformat() + "Z",
        "encryption_method": "RSA-OAEP-256"
    }


async def store_org_key(kv_store, org_id: str, jwk: dict) -> bool:
    """Store an organization's JWK public key in Cloudflare KV."""
    if not validate_jwk_public_key(jwk):
        raise ValueError("Invalid JWK public key")

    await kv_store.put(
        f"org_key:{org_id}",
        json.dumps({
            "org_id": org_id,
            "jwk": jwk,
            "registered_at": datetime.utcnow().isoformat() + "Z"
        }),
        expiration_ttl=365 * 24 * 3600
    )
    return True


async def get_org_key(kv_store, org_id: str) -> dict:
    """Retrieve an organization's public key from KV."""
    result = await kv_store.get(f"org_key:{org_id}")
    if not result:
        raise KeyError(f"No public key found for org: {org_id}")
    return json.loads(result)