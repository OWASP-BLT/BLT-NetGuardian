"""
Validate user-supplied scan targets and discovery suggestions.

Reduces abuse where callers steer scanning toward cloud metadata hosts,
loopback, or RFC1918 addresses on shared internet-facing workers. See
``SECURITY.md`` and env ``ALLOW_PRIVATE_SCAN_TARGETS``.
"""
from __future__ import annotations

import ipaddress
from typing import Any, Optional, Tuple
from urllib.parse import urlparse

# Hostnames that are never accepted (metadata / control plane).
_BLOCKED_METADATA_HOSTS: frozenset = frozenset({
    "metadata.google.internal",
    "metadata.gce.internal",
    "kubernetes.default",
    "metadata.google.internal.",  # trailing dot
})


def _extract_host_for_ip_check(value: str) -> str:
    """
    Extract hostname or IP literal from a URL, bare host:port, or domain-like string.

    Returns lowercased host/IP without brackets for IPv6, or empty if unknown.
    """
    v = value.strip()
    if not v:
        return ""

    if "://" in v:
        parsed = urlparse(v)
        netloc = (parsed.netloc or "").strip()
    else:
        netloc = v.split("/")[0].strip()

    if not netloc:
        return ""

    if "@" in netloc:
        netloc = netloc.rsplit("@", 1)[-1]

    if netloc.startswith("["):
        end = netloc.find("]")
        if end != -1:
            return netloc[1:end].strip().lower()
        return netloc.lower()

    if netloc.count(":") > 1 and "." not in netloc.split(":")[0]:
        # Bare IPv6 without brackets (heuristic)
        return netloc.lower()

    host = netloc
    if ":" in host:
        possible_host, _, rest = host.rpartition(":")
        if rest.isdigit() or rest == "":
            host = possible_host
    return host.strip().lower()


def _ip_from_host(host: str) -> Optional[ipaddress.IPv4Address | ipaddress.IPv6Address]:
    """Parse host as IPv4/IPv6 or return None."""
    if not host:
        return None
    h = host
    if h.startswith("[") and h.endswith("]"):
        h = h[1:-1]
    try:
        return ipaddress.ip_address(h)
    except ValueError:
        return None


def validate_user_target_input(
    value: Any,
    *,
    max_len: int = 4096,
    allow_private_hosts: bool = False,
    field_name: str = "target",
) -> Tuple[Optional[str], Optional[str]]:
    """
    Validate a user-provided target string (URL, domain, or repo path).

    Args:
        value: Raw input (typically from JSON).
        max_len: Maximum length after strip.
        allow_private_hosts: If False, reject loopback, link-local, and private IPs,
            and the hostname ``localhost``.
        field_name: Used in error messages (e.g. ``suggestion`` vs ``target``).

    Returns:
        ``(normalized_string, None)`` on success, or ``(None, error_message)``.
    """
    if not isinstance(value, str):
        return None, f"{field_name} must be a string"

    s = value.strip()
    if not s:
        return None, f"{field_name} cannot be empty"

    if len(s) > max_len:
        return None, f"{field_name} exceeds maximum length of {max_len} characters"

    if "\x00" in s:
        return None, f"{field_name} contains invalid characters"

    host = _extract_host_for_ip_check(s)
    if not host:
        return s, None

    if host in _BLOCKED_METADATA_HOSTS or host.endswith(".gce.internal"):
        return None, f"{field_name} must not target cloud metadata or internal control-plane hosts"

    # Link-local / cloud instance metadata IP (always block, even if private allowed).
    ip = _ip_from_host(host)
    if ip is not None:
        if ip == ipaddress.ip_address("169.254.169.254"):
            return None, f"{field_name} must not target cloud instance metadata addresses"

    if not allow_private_hosts:
        if host == "localhost":
            return None, (
                f"{field_name} cannot use localhost "
                "(set ALLOW_PRIVATE_SCAN_TARGETS=true for self-hosted workers)"
            )
        if ip is not None:
            if ip.is_loopback or ip.is_link_local or ip.is_private:
                return None, (
                    f"{field_name} cannot use loopback, link-local, or private IP addresses "
                    "(set ALLOW_PRIVATE_SCAN_TARGETS=true on self-hosted workers to allow)"
                )

    return s, None
