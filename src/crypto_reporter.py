"""
Compatible zero-trust vulnerability reporter

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
    if "d" in jwk:
        return False
    return True


def hash_org_id(org_id: str) -> str:
    """
    Hash org_id using full SHA-256.
    Never store plaintext org_id as database key.
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
    Build final submission after encryption.
    org_id is hashed before storage - never stored plaintext.
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

async def store_org_key(db, org_id: str, jwk: dict) -> bool:
    """
    Store org's JWK public key in Cloudflare D1.
    Uses hashed org_id - never stores plaintext org_id.
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
    """Remove org's public key from D1 - used for key rotation."""
    org_id_hash = hash_org_id(org_id)
    await db.prepare(
        "DELETE FROM org_keys WHERE org_id_hash = ?"
    ).bind(org_id_hash).run()
    return True