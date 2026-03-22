# Security notes — BLT-NetGuardian

## User-supplied targets and discovery suggestions

Public deployments should avoid letting anonymous users steer the scanner toward **infrastructure the worker can reach but should not scan** (e.g. cloud metadata IPs, loopback, RFC1918 space on shared workers).

The API validates **`POST /api/discovery/suggest`** (`suggestion`) and **`POST /api/targets/register`** (`target`) using `utils.input_validation.validate_user_target_input`, which by default:

- Rejects **null bytes** and over-long strings (same upper bound as `MAX_TARGET_URL_LEN` in the worker).
- Blocks common **metadata / loopback literals** (e.g. `localhost`, `127.0.0.1`, `169.254.169.254`, `metadata.google.internal`).
- Rejects **loopback, link-local, and private IP addresses** when parsed from the host part of a URL or bare host.

### Self-hosted / lab use

To allow **private and loopback IPs** (e.g. scanning `http://192.168.1.1` on your own worker), set:

```text
ALLOW_PRIVATE_SCAN_TARGETS=true
```

in the Worker environment (`wrangler.toml` / dashboard). Default is **off**.

This does **not** replace network-level controls; combine with firewalls and authenticated APIs where appropriate.

## API authentication

Mutating API routes expect credentials when `API_SECRET` is configured. See `API.md` and `worker.py` (`authenticate_request`).

## Reporting issues

Please report security issues responsibly via the OWASP BLT channels listed in the main **README**.
