from typing import Dict, Any
from datetime import datetime

from models.result import ScanResult, VulnerabilityLevel

class ResultNormalizer:
    # Helper used before storing scan results.
    # Scanners currently return loosely structured dictionaries,
    # so this converts them into the ScanResult model used by the API.

    @staticmethod
    def normalize(task_id: str, agent_type: str, results: Dict[str, Any]) -> ScanResult:
        # Scanners can sometimes return malformed payloads.
        # Guard against unexpected types so ingestion doesn't break the pipeline.
        findings = results.get("findings", [])
        if not isinstance(findings, list):
            findings = []
        vulnerabilities = results.get("vulnerabilities", [])
        if not isinstance(vulnerabilities, list):
            vulnerabilities = []
        metadata = results.get("metadata", {})
        if not isinstance(metadata, dict):
            metadata = {}

        normalized_vulns = [
            ResultNormalizer._normalize_vulnerability(v)
            for v in vulnerabilities
            if isinstance(v, dict)
        ]

        return ScanResult(
            result_id="",
            task_id=task_id,
            agent_type=agent_type,
            findings=findings,
            vulnerabilities=normalized_vulns,
            metadata=metadata,
            timestamp=datetime.utcnow().isoformat()
        )
    
    @staticmethod
    def _normalize_vulnerability(vuln: Dict[str, Any]) -> Dict[str, Any]:
        # normalize severity to one of the supported vulnerability levels.
        # Unknown/unexpected values are downgraded to "info".
        severity = vuln.get("severity", "info").lower()

        valid_levels = [level.value for level in VulnerabilityLevel]
        if severity not in valid_levels:
            severity = "info"

        return {
            "type": vuln.get("type", "unknown"),
            "severity": severity,
            "title": vuln.get("title", "Unnamed vulnerability"),
            "description": vuln.get("description", ""),
            "affected_component": vuln.get("affected_component", "unknown"),
            "cve_id": vuln.get("cve_id"),
            "cvss_score": vuln.get("cvss_score"),
            "remediation": vuln.get("remediation"),
            "references": vuln.get("references", []),
        }