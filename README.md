# BLT-NetGuardian

## Secure Vulnerability Reporting System

BLT-NetGuardian provides a **zero-trust, end-to-end encrypted** solution for AI bots to report security vulnerabilities to organizations. Using industry-standard PGP/GPG encryption, it ensures that only the intended recipient (with the private key) can decrypt and read vulnerability reports.

### 🔐 Key Security Features

- **Zero-Trust Architecture**: No shared secrets or pre-established trust required
- **End-to-End Encryption**: Only the company's private key can decrypt reports
- **Public Key Cryptography**: Based on battle-tested PGP/GPG standards
- **No Third-Party Dependencies**: No reliance on external encryption services
- **Secure by Design**: Vulnerability data never transmitted in plaintext

### 🎯 Why PGP/GPG Over Password-Protected Zip Files?

| Feature | PGP/GPG Encryption | Password-Protected Zip |
|---------|-------------------|------------------------|
| Key Management | Asymmetric (public/private key pair) | Symmetric (single password) |
| Password Transmission | No password needs to be shared | Password must be sent separately |
| Brute Force Resistance | Extremely high (4096-bit keys) | Depends on password strength |
| Industry Standard | Yes (RFC 4880) | No standardized security |
| Forward Secrecy | Supported | Not supported |
| Key Revocation | Supported | Not applicable |

### 📋 How It Works

1. **Company Setup** (One-time):
   - Company generates a PGP key pair (public + private key)
   - Public key is shared with the AI bot
   - Private key is kept secure by the company

2. **AI Bot Reports Vulnerability**:
   - Bot creates a structured vulnerability report
   - Bot encrypts report using company's public key
   - Encrypted report is sent via email or stored for retrieval

3. **Company Receives & Decrypts**:
   - Company receives encrypted report
   - Only company's private key can decrypt it
   - Vulnerability details are revealed only to authorized personnel

### 🚀 Quick Start

#### Prerequisites

- Python 3.7 or higher
- GnuPG (GPG) installed on your system

**Install GPG:**
```bash
# Ubuntu/Debian
sudo apt-get install gnupg

# macOS
brew install gnupg

# Windows
# Download from: https://www.gnupg.org/download/
```

#### Installation

```bash
# Clone the repository
git clone https://github.com/OWASP-BLT/BLT-NetGuardian.git
cd BLT-NetGuardian

# Install Python dependencies
pip install -r requirements.txt
```

### 📚 Usage Guide

#### For Companies: Initial Setup

Generate your organization's PGP key pair:

```bash
python example_company_setup.py
```

This creates:
- `company_public_key.asc` - Share this with the AI bot
- `company_private_key.asc` - **Keep this secure!** Never share or commit to version control

**Security Best Practices:**
- Use a strong passphrase (16+ characters)
- Store private key in a Hardware Security Module (HSM) if available
- Restrict access to private key to authorized personnel only
- Consider using key servers to publish your public key

#### For AI Bots: Report a Vulnerability

```python
from secure_reporter import SecureVulnerabilityReporter

# Initialize reporter
reporter = SecureVulnerabilityReporter()

# Import company's public key
reporter.import_public_key('company_public_key.asc')

# Create vulnerability report
vulnerability = reporter.create_vulnerability_report(
    title="SQL Injection in Authentication",
    description="Detailed description of the vulnerability...",
    severity="critical",
    affected_systems=["Web API v2.1.0"],
    remediation="Use parameterized queries..."
)

# Encrypt and save
encrypted_path = reporter.encrypt_vulnerability_report(
    vulnerability_data=vulnerability,
    recipient_fingerprint="<company-key-fingerprint>"
)

print(f"Encrypted report saved: {encrypted_path}")
```

Or use the example script:

```bash
python example_bot_report.py
```

#### For Companies: Decrypt Reports

```bash
python example_company_decrypt.py reports/vulnerability_report_20241213_120000.pgp
```

Or programmatically:

```python
from secure_reporter import DecryptionHelper

helper = DecryptionHelper()
report = helper.decrypt_report(
    'reports/vulnerability_report_20241213_120000.pgp',
    passphrase='your-private-key-passphrase'
)

print(f"Title: {report['data']['title']}")
print(f"Severity: {report['data']['severity']}")
```

### 📧 Email Delivery (Optional)

Configure email settings to automatically send encrypted reports:

1. Copy `.env.example` to `.env`
2. Configure your SMTP settings:

```bash
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=bot@example.com
SENDER_PASSWORD=your-app-password
RECIPIENT_EMAIL=security@company.com
```

3. Reports will be automatically emailed when using `example_bot_report.py`

### 🏗️ Architecture

```
┌─────────────┐                           ┌──────────────┐
│   AI Bot    │                           │   Company    │
│             │                           │              │
│  1. Creates │                           │ 4. Receives  │
│  Vuln Report│                           │ Encrypted    │
│             │                           │ Report       │
│  2. Encrypts│     ┌───────────┐        │              │
│  with Public│────▶│  Secure   │───────▶│ 5. Decrypts  │
│  Key        │     │  Channel  │        │ with Private │
│             │     │ (Email/   │        │ Key          │
│  3. Sends   │     │  Storage) │        │              │
│  Report     │     └───────────┘        │ 6. Processes │
└─────────────┘                           │ Vulnerability│
                                          └──────────────┘

┌──────────────────────────────────────────────────────┐
│           Zero-Trust Encryption Layer                │
│  • No cleartext vulnerability data in transit        │
│  • No shared passwords                               │
│  • Only recipient's private key can decrypt          │
└──────────────────────────────────────────────────────┘
```

### 🔧 API Reference

#### `SecureVulnerabilityReporter`

Main class for creating and encrypting vulnerability reports.

**Methods:**
- `import_public_key(public_key_path)` - Import company's public key
- `create_vulnerability_report(...)` - Create structured vulnerability report
- `encrypt_vulnerability_report(data, fingerprint)` - Encrypt report
- `send_encrypted_report_via_email(...)` - Send encrypted report via email

#### `DecryptionHelper`

Helper class for companies to decrypt reports.

**Methods:**
- `decrypt_report(encrypted_file_path, passphrase)` - Decrypt and parse report

#### `generate_key_pair(...)`

Utility function to generate PGP key pairs.

### 🔒 Security Considerations

#### Strengths

1. **Asymmetric Encryption**: Public key for encryption, private key for decryption
2. **No Password Sharing**: Unlike zip files, no password needs to be transmitted
3. **Strong Encryption**: 4096-bit RSA keys provide excellent security
4. **Industry Standard**: Based on OpenPGP (RFC 4880)
5. **Key Revocation**: Compromised keys can be revoked
6. **Signature Support**: Can add digital signatures for authenticity

#### Best Practices

1. **Key Storage**:
   - Store private keys in Hardware Security Modules (HSM)
   - Use strong passphrases (16+ characters)
   - Never commit private keys to version control
   - Regularly backup private keys securely

2. **Key Rotation**:
   - Rotate keys periodically (e.g., annually)
   - Maintain old keys for decrypting historical reports
   - Publish key expiration dates

3. **Access Control**:
   - Limit private key access to authorized personnel
   - Log all decryption operations
   - Use principle of least privilege

4. **Email Security**:
   - Use TLS for SMTP connections
   - Consider using app-specific passwords
   - Implement SPF/DKIM/DMARC for email authentication

### 🆚 Comparison with Alternatives

#### Alternative 1: Password-Protected Zip + Separate Email
- ❌ Password must be transmitted (security risk)
- ❌ Vulnerable to interception if emails are compromised
- ❌ No forward secrecy
- ✅ Simple to implement

#### Alternative 2: Third-Party Encrypted File Sharing
- ❌ Requires trust in third-party service
- ❌ Additional dependencies
- ❌ May have data residency concerns
- ✅ User-friendly interface

#### BLT-NetGuardian (PGP/GPG)
- ✅ Zero-trust architecture
- ✅ No third-party dependencies
- ✅ Industry standard encryption
- ✅ No password transmission needed
- ✅ Supports key revocation
- ⚠️ Requires GPG installation

### 📝 Report Format

Encrypted reports contain structured JSON data:

```json
{
  "timestamp": "2024-12-13T12:00:00Z",
  "report_type": "vulnerability",
  "version": "1.0",
  "data": {
    "title": "Vulnerability Title",
    "description": "Detailed description...",
    "severity": "critical|high|medium|low",
    "affected_systems": ["System 1", "System 2"],
    "discovery_timestamp": "2024-12-13T11:30:00Z",
    "cve_ids": ["CVE-2024-XXXXX"],
    "remediation": "Remediation steps...",
    "additional_data": {
      "proof_of_concept": "...",
      "affected_endpoints": [...],
      "discovered_by": "AI Security Bot",
      "confidence_level": "high|medium|low"
    }
  }
}
```

### 🧪 Testing

Run the example workflow:

```bash
# 1. Generate keys (company)
python example_company_setup.py

# 2. Create and encrypt report (bot)
python example_bot_report.py

# 3. Decrypt report (company)
python example_company_decrypt.py reports/vulnerability_report_*.pgp
```

### 🤝 Contributing

Contributions are welcome! Please ensure:
- Code follows existing style
- Security best practices are maintained
- Documentation is updated
- No private keys are committed

### 📄 License

See [LICENSE](LICENSE) file for details.

### 🔗 Resources

- [OpenPGP Specification (RFC 4880)](https://tools.ietf.org/html/rfc4880)
- [GnuPG Documentation](https://www.gnupg.org/documentation/)
- [Python GnuPG Library](https://gnupg.readthedocs.io/)
- [OWASP Secure Coding Practices](https://owasp.org/www-project-secure-coding-practices-quick-reference-guide/)

### 📞 Support

For security issues, please contact: security@owasp-blt.org

---

**⚠️ Security Notice**: This system is designed for secure vulnerability reporting. Always verify the authenticity of public keys before using them for encryption. Never share or commit private keys to version control systems.