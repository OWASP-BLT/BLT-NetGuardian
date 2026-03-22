# Quick Start Guide

## What is BLT-NetGuardian?

BLT-NetGuardian provides a **secure, zero-trust way** for AI bots to report vulnerabilities to companies using PGP/GPG encryption. Only the company with the private key can decrypt the reports.

## Why is this better than password-protected zip files?

| Feature | BLT-NetGuardian (PGP) | Password-Protected Zip |
|---------|------------------------|------------------------|
| Password sharing | ❌ Not needed | ✅ Required (security risk) |
| Brute force resistance | ✅ Extremely strong | ⚠️ Depends on password |
| Key management | ✅ Asymmetric keys | ❌ Shared password |
| Industry standard | ✅ RFC 4880 | ❌ Proprietary |
| Forward secrecy | ✅ Supported | ❌ Not supported |

## 3-Step Setup

### For Companies (One-time setup)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Generate your keys
python example_company_setup.py

# 3. Share company_public_key.asc with your AI bot
```

### For AI Bots (Every vulnerability)

```bash
# 1. Obtain company's public key (one-time)
# 2. Create and encrypt report
python example_bot_report.py
```

### For Companies (Decrypt reports)

```bash
# Decrypt received reports
python example_company_decrypt.py reports/vulnerability_report_*.pgp
```

## How It Works

```
┌─────────────┐                  ┌──────────────┐
│   AI Bot    │                  │   Company    │
│             │                  │              │
│ 1. Encrypt  │──────────────────▶│ 2. Decrypt   │
│ with PUBLIC │  Email/Storage   │ with PRIVATE │
│ key         │                  │ key          │
└─────────────┘                  └──────────────┘

🔒 Zero-trust: No shared secrets
🔐 End-to-end: Only company can decrypt
✅ Standard: Uses OpenPGP (RFC 4880)
```

## Security Features

- ✅ **4096-bit RSA encryption** - Extremely strong
- ✅ **No password transmission** - Unlike zip files
- ✅ **Zero-trust architecture** - No pre-shared secrets
- ✅ **Key revocation support** - Compromised keys can be revoked
- ✅ **No third-party services** - Complete control
- ✅ **Industry standard** - OpenPGP (RFC 4880)

## Minimal Code Example

### Bot encrypts:
```python
from secure_reporter import SecureVulnerabilityReporter

reporter = SecureVulnerabilityReporter()
reporter.import_public_key('company_public_key.asc')

vulnerability = reporter.create_vulnerability_report(
    title="SQL Injection Found",
    description="...",
    severity="critical",
    affected_systems=["Web API v2.1.0"]
)

encrypted_file = reporter.encrypt_vulnerability_report(
    vulnerability, 
    recipient_fingerprint="ABC123..."
)
# Send encrypted_file via email or secure channel
```

### Company decrypts:
```python
from secure_reporter import DecryptionHelper

helper = DecryptionHelper()
report = helper.decrypt_report(
    'vulnerability_report.pgp',
    passphrase='your-private-key-passphrase'
)

print(report['data']['title'])  # "SQL Injection Found"
```

## Requirements

- Python 3.7+
- GnuPG (GPG) installed on system
- Dependencies: `python-gnupg`, `cryptography`, `python-dotenv`

## Testing

```bash
# Run unit tests
python test_secure_reporter.py

# Run integration test
python integration_test.py
```

## Security Best Practices

### For Companies:
1. ✅ Use strong passphrase (16+ characters)
2. ✅ Store private key in Hardware Security Module (HSM)
3. ✅ Rotate keys annually
4. ✅ Publish public key on multiple channels
5. ✅ Monitor decryption operations

### For AI Bots:
1. ✅ Verify public key fingerprint before using
2. ✅ Use TLS for email transmission
3. ✅ Don't log sensitive vulnerability data
4. ✅ Implement retry logic
5. ✅ Monitor for errors

## Email Configuration (Optional)

Create a `.env` file for automated email delivery:

```bash
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=bot@example.com
SENDER_PASSWORD=app-specific-password
RECIPIENT_EMAIL=security@company.com
```

**Note**: Use app-specific passwords, not account passwords!

## Need Help?

- 📖 Full documentation: [README.md](README.md)
- 🔒 Security details: [SECURITY_ARCHITECTURE.md](SECURITY_ARCHITECTURE.md)
- 🐛 Issues: GitHub Issues
- 📧 Security contact: security@owasp-blt.org

## License

See [LICENSE](LICENSE) file for details.
