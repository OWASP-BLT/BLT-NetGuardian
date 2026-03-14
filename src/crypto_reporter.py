"""
Workers-compatible Zero-Trust Vulnerability Reporter

The original secure_reporter.py used python-gnupg which needs GPG
binaries and filesystem access. Cloudflare Workers has neither.
This uses Web Crypto API instead - no dependencies, runs in Workers.

Updated to use Cloudflare D1 database instead of KV store,
following architectural change in PR #12.

Security fixes applied:
- Full SHA-256 everywhere, no truncation
- org_id hashed before storage, never plaintext
- AES non-extractable, wrapped with RSA-OAEP
- AAD binding in AES-GCM for ciphertext integrity
- JWK validation rejects malformed/private keys
- UUID for submission_id

(OWASP BLT-NetGuardian contributor)
"""
import json
import hashlib
import uuid
from datetime import datetime


VALID_SEVERITIES = {"critical", "high", "medium", "low", "info"}


def validate_severity(severity: str) -> str:
    """Normalize and validate severity level."""
    normalized = severity.lower().strip()
    if normalized not in VALID_SEVERITIES:
        raise ValueError(
            f"Invalid severity '{severity}'. "
            f"Must be one of: {VALID_SEVERITIES}"
        )
    return normalized


def validate_jwk_public_key(jwk: dict) -> bool:
    """
    Validate JWK public key has required RSA-OAEP fields.
    Rejects malformed keys and accidentally submitted private keys.
    """
    if not isinstance(jwk, dict):
        return False
    if jwk.get("kty") != "RSA":
        return False
    if not jwk.get("n") or not jwk.get("e"):
        return False
    if "d" in jwk:  # reject private keys submitted by mistake
        return False
    return True


def hash_org_id(org_id: str) -> str:
    """
    Hash org_id using full SHA-256 - 256 bits, no truncation.
    Never store or use plaintext org_id as a database key.
    """
    return hashlib.sha256(org_id.encode()).hexdigest()


def create_report(
    title: str,
    description: str,
    severity: str,
    affected_systems: list,
    remediation: str = "",
    cve_ids: list = None,
    additional_data: dict = None
) -> dict:
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


def prepare_payload(report: dict) -> str:
    """Serialize report to JSON string ready for encryption."""
    return json.dumps(report, separators=(',', ':'))


def build_submission(
    encrypted_data: str,
    org_id: str,
    key_fingerprint: str
) -> dict:
    """
    Build final submission object after encryption.
    org_id is hashed - never stored in plaintext.
    submission_id uses UUID for guaranteed uniqueness.
    """
    return {
        "submission_id": str(uuid.uuid4()),
        "org_id_hash": hash_org_id(org_id),
        "key_fingerprint": key_fingerprint,
        "encrypted_payload": encrypted_data,
        "submitted_at": datetime.utcnow().isoformat() + "Z",
        "encryption_method": "AES-GCM-256 + RSA-OAEP wrapped key"
    }


# D1 database functions
# Migrated from KV store to D1 following PR #12 architecture change

async def store_org_key(db, org_id: str, jwk: dict) -> bool:
    """
    Store org's JWK public key in Cloudflare D1.
    KV key uses hashed org_id - never stores plaintext org_id.
    """
    if not validate_jwk_public_key(jwk):
        raise ValueError("Invalid or malformed JWK public key")

    org_id_hash = hash_org_id(org_id)

    await db.prepare(
        """INSERT INTO org_keys (org_id_hash, jwk, registered_at)
           VALUES (?, ?, ?)
           ON CONFLICT(org_id_hash) DO UPDATE SET
           jwk=excluded.jwk,
           registered_at=excluded.registered_at"""
    ).bind(
        org_id_hash,
        json.dumps(jwk),
        datetime.utcnow().isoformat() + "Z"
    ).run()
    return True


async def get_org_key(db, org_id: str) -> dict:
    """Retrieve org's public key from D1 using hashed org_id."""
    org_id_hash = hash_org_id(org_id)
    row = await db.prepare(
        "SELECT jwk FROM org_keys WHERE org_id_hash = ?"
    ).bind(org_id_hash).first()
    if row is None:
        raise KeyError("No public key found for org")
    return json.loads(row['jwk'])


async def delete_org_key(db, org_id: str) -> bool:
    """Remove org's public key from D1 - used during key rotation."""
    org_id_hash = hash_org_id(org_id)
    await db.prepare(
        "DELETE FROM org_keys WHERE org_id_hash = ?"
    ).bind(org_id_hash).run()
    return True