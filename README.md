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

**⚠️ CRITICAL SECURITY STEP: Verify Public Key Fingerprint**

Before encrypting any vulnerability reports, you MUST verify the company's public key fingerprint through an out-of-band channel to prevent public key substitution attacks:

```bash
# Check the fingerprint of the imported key
gpg --fingerprint security@company.com

# Verify this matches the fingerprint published by the company:
# - On their official website (via HTTPS)
# - Via direct communication (phone, in-person)
# - On their key server profile
# - Through their security.txt file
```

Never trust a public key without verification!

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
🛡️ Autonomous Internet Security Scanner powered by Cloudflare Workers

## Deploy to Cloudflare

[![Deploy to Cloudflare Workers](https://deploy.workers.cloudflare.com/button)](https://deploy.workers.cloudflare.com/?url=https://github.com/OWASP-BLT/BLT-NetGuardian)

Click the button above to deploy BLT-NetGuardian to your Cloudflare account in one click!

## Overview

BLT-NetGuardian is an **autonomous security scanning system** that continuously discovers and scans the internet for security vulnerabilities. Unlike traditional scanners that require manual target submission, BLT-NetGuardian actively discovers domains, repositories, smart contracts, and APIs using multiple discovery methods, automatically scans them for vulnerabilities, and contacts stakeholders when issues are found.

## Features

### 🤖 Autonomous Discovery

- **Certificate Transparency Monitoring**: Discovers new domains from CT logs
- **GitHub Repository Scanning**: Tracks trending and newly updated repositories
- **Blockchain Monitoring**: Detects new smart contract deployments
- **Subdomain Enumeration**: Discovers subdomains of known targets
- **API Directory Scanning**: Monitors public API directories
- **User Suggestions**: Allows community to guide the scanner

### 📧 Automatic Contact & Notification

- **security.txt Integration**: RFC 9116 compliant contact discovery
- **WHOIS Lookup**: Finds domain registrant contacts
- **GitHub Security Advisory**: Direct security team notification
- **Responsible Disclosure**: 90-day disclosure timeline
- **Contact Logging**: Tracks all notification attempts

### 🔍 Security Scanners

1. **Web2 Crawler** - Web application vulnerability scanner
   - XSS, CSRF, SQLi detection
   - Security header analysis
   - Form and endpoint discovery
   - Authentication testing

2. **Web3 Monitor** - Blockchain and smart contract monitoring
   - Transaction pattern analysis
   - Malicious address detection
   - Gas usage optimization
   - Real-time blockchain monitoring

3. **Static Analyzer** - Source code security analysis
   - SAST tool integration
   - Dependency vulnerability scanning
   - Hardcoded secret detection
   - Multi-language support (Python, JavaScript, Java, Go, Rust)

4. **Contract Scanner** - Smart contract auditing
   - Reentrancy vulnerability detection
   - Access control analysis
   - Integer overflow/underflow checks
   - Gas optimization recommendations
   - Solidity and Vyper support

5. **Volunteer Agent Manager** - Community security testing
   - Distributed testing coordination
   - Agent registration and management
   - Result validation and aggregation
   - Contributor rewards

### 🌐 Web Interface

**Live Autonomous Scanner Dashboard:**
- Real-time scanning status with current target
- Live discovery feed showing newly found targets
- Simple suggestion input to guide the scanner
- Statistics: domains discovered, repos found, contacts made
- Recent discoveries with vulnerability status

**No Manual Forms Required** - The system continuously scans on its own!

## Architecture

BLT-NetGuardian uses a split architecture:
- **Frontend**: Static HTML/CSS/JS hosted on **GitHub Pages**
- **Backend**: Python API worker running on **Cloudflare Workers**

```
┌─────────────────────────────────────────────────────────────┐
│                     GitHub Pages                            │
│                   (Frontend - Static)                       │
│                                                             │
│  ┌──────────────┐  ┌─────────────┐  ┌──────────────────┐  │
│  │  index.html  │  │ dashboard   │  │ vulnerabilities  │  │
│  │  (Main UI)   │  │   .html     │  │    .html         │  │
│  └──────────────┘  └─────────────┘  └──────────────────┘  │
│                                                             │
│         │                                                   │
└─────────┼───────────────────────────────────────────────────┘
          │ HTTPS/REST API
          ▼
┌─────────────────────────────────────────────────────────────┐
│              Cloudflare Worker (Backend)                    │
│                    Python API Only                          │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │               API Endpoints                          │  │
│  │  • /api/tasks/queue                                  │  │
│  │  • /api/targets/register                            │  │
│  │  • /api/results/ingest                              │  │
│  │  • /api/jobs/status                                 │  │
│  │  • /api/vulnerabilities                             │  │
│  └──────────────────────────────────────────────────────┘  │
│                            │                                 │
│         ┌──────────────────┴──────────────────┐             │
│         │     Scanner Coordinator             │             │
│         └──────────┬──────────────────────────┘             │
│                    │                                         │
│  ┌─────────────────┼─────────────────────────────────────┐  │
│  │                 │                                     │  │
│  ▼                 ▼                 ▼                   ▼  │
│ Web2          Web3             Static            Contract   │
│ Crawler       Monitor          Analyzer          Scanner    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                        │
                        ▼
           ┌────────────────────────┐
           │   Cloudflare KV Store  │
           │  ├─ Job States         │
           │  ├─ Task Queue         │
           │  ├─ Vulnerability DB   │
           │  └─ Target Registry    │
           └────────────────────────┘
```

## How It Works

### 1. Autonomous Discovery
The system continuously discovers new targets using:
- **CT Log Monitoring**: Watches Certificate Transparency logs for new SSL certificates
- **GitHub API**: Monitors trending repositories and recent updates
- **Blockchain Scanners**: Tracks new smart contract deployments on Ethereum, Polygon, BSC
- **DNS Enumeration**: Discovers subdomains and related domains
- **Public Directories**: Scans API directories and service listings

### 2. Automatic Scanning
When a target is discovered:
1. Target is automatically registered in the system
2. Appropriate scanners are selected based on target type
3. Scan tasks are queued with priority based on discovery source
4. Multiple scanners run in parallel for comprehensive coverage
5. Results are aggregated and stored

### 3. Vulnerability Detection
Each scanner detects specific vulnerability types:
- **Web2**: XSS, CSRF, SQLi, security misconfigurations
- **Web3**: Reentrancy, access control, integer issues
- **Static**: Code vulnerabilities, dependency issues, secrets
- **Contract**: Smart contract specific vulnerabilities

### 4. Automatic Contact
When vulnerabilities are found:
1. System looks for contact information (security.txt, WHOIS, GitHub)
2. Prepares professional vulnerability disclosure report
3. Attempts contact through multiple channels
4. Logs all contact attempts for transparency
5. Follows 90-day responsible disclosure timeline

### 5. User Guidance
Community members can:
- Suggest specific targets for immediate scanning
- Mark suggestions as priority for faster processing
- View real-time discovery and scanning status
- Monitor contact attempts and responses

## API Endpoints

### Autonomous Discovery

#### Suggest a Target
```
POST /api/discovery/suggest
Content-Type: application/json

{
  "suggestion": "example.com",
  "priority": true
}
```

#### Get Discovery Status
```
GET /api/discovery/status
```

#### Get Recent Discoveries
```
GET /api/discovery/recent?limit=20
```

### Task Management

#### Queue Tasks
```
POST /api/tasks/queue
Content-Type: application/json

{
  "target_id": "abc123",
  "task_types": ["crawler", "static_analysis"],
  "priority": "high"
}
```

#### List Tasks
```
GET /api/tasks/list?job_id=job123
```

### Target Registration

#### Register Target
```
POST /api/targets/register
Content-Type: application/json

{
  "target_type": "web2",
  "target": "https://example.com",
  "scan_types": ["crawler", "vulnerability_scan"],
  "notes": "Focus on authentication flows"
}
```

### Results & Vulnerabilities

#### Ingest Results
```
POST /api/results/ingest
Content-Type: application/json

{
  "task_id": "task123",
  "agent_type": "web2_crawler",
  "results": {
    "findings": [...],
    "vulnerabilities": [...]
  }
}
```

#### Get Vulnerabilities
```
GET /api/vulnerabilities?limit=50&severity=critical
```

### Job Status

#### Check Job Status
```
GET /api/jobs/status?job_id=job123
```

## Installation & Deployment

### Quick Start - One-Click Deploy

[![Deploy to Cloudflare Workers](https://deploy.workers.cloudflare.com/button)](https://deploy.workers.cloudflare.com/?url=https://github.com/OWASP-BLT/BLT-NetGuardian)

**Quick Deploy**: Click the button above to instantly deploy the backend to your Cloudflare account!

BLT-NetGuardian is split into two parts:

1. **Frontend (GitHub Pages)** - Already live at `https://owasp-blt.github.io/BLT-NetGuardian/`
2. **Backend (Cloudflare Workers)** - Deploy with one click or manually (instructions below)

### Deploy the Backend (Cloudflare Workers)

#### Option 1: One-Click Deploy (Recommended)

Simply click the "Deploy to Cloudflare Workers" button above. This will:
- Fork the repository to your GitHub account (if needed)
- Guide you through connecting your Cloudflare account
- Automatically create required KV namespaces
- Deploy the worker to your Cloudflare account

#### Option 2: Manual Deployment

##### Prerequisites

- [Wrangler CLI](https://developers.cloudflare.com/workers/wrangler/install-and-update/)
- Cloudflare account

##### Steps

1. Install Wrangler:
```bash
npm install -g wrangler
```

2. Login to Cloudflare:
```bash
wrangler login
```

3. Create KV namespaces:
```bash
wrangler kv:namespace create "JOB_STATE"
wrangler kv:namespace create "TASK_QUEUE"
wrangler kv:namespace create "VULN_DB"
wrangler kv:namespace create "TARGET_REGISTRY"
```

4. Update `wrangler.toml` with your KV namespace IDs

5. Deploy:
```bash
wrangler publish
```

6. Update `assets/js/config.js` with your Worker URL:
```javascript
API_BASE_URL: 'https://blt-netguardian.your-subdomain.workers.dev'
```

7. Commit and push the config change to deploy to GitHub Pages

### Local Development

#### Frontend
```bash
# Serve static files
python -m http.server 8000
# Visit http://localhost:8000
```

#### Backend
```bash
wrangler dev
# API available at http://localhost:8787
```

Update `assets/js/config.js` to use local backend:
```javascript
API_BASE_URL: 'http://localhost:8787'
```

For detailed deployment instructions, see [DEPLOY.md](DEPLOY.md)

## Security Tools Reference

BLT-NetGuardian can integrate with a wide variety of security scanning tools. For a comprehensive list of vulnerability scanning tools and resources, see [SECURITY_TOOLS.md](SECURITY_TOOLS.md).

The document includes tools for:
- Static Application Security Testing (SAST)
- Dynamic Application Security Testing (DAST)
- Dependency and Supply Chain Security
- Container and Infrastructure Security
- Smart Contract Security
- Secret Detection
- And many more categories

## Configuration

Edit `wrangler.toml` to configure:

- KV namespace bindings
- Environment variables
- Worker routes
- Build settings

## Usage Examples

### Submit a Web Application Scan

```javascript
const response = await fetch('https://your-worker.workers.dev/api/targets/register', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    target_type: 'web2',
    target: 'https://example.com',
    scan_types: ['crawler', 'vulnerability_scan']
  })
});

const { target_id } = await response.json();

// Queue scanning tasks
await fetch('https://your-worker.workers.dev/api/tasks/queue', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    target_id,
    task_types: ['crawler', 'vulnerability_scan'],
    priority: 'high'
  })
});
```

### Check Scan Progress

```javascript
const response = await fetch(`https://your-worker.workers.dev/api/jobs/status?job_id=${jobId}`);
const status = await response.json();

console.log(`Progress: ${status.progress}% (${status.completed}/${status.total} tasks)`);
```

### View Vulnerabilities

```javascript
const response = await fetch('https://your-worker.workers.dev/api/vulnerabilities?severity=critical');
const { vulnerabilities } = await response.json();

vulnerabilities.forEach(vuln => {
  console.log(`${vuln.severity.toUpperCase()}: ${vuln.title}`);
});
```

## Security Considerations

- All API endpoints support CORS for web interface access
- Task deduplication prevents redundant scanning
- Vulnerability data is stored with 30-day expiration
- Results include LLM triage preparation for AI-powered analysis
- Volunteer agent submissions should be validated before acceptance

## Data Models

### Task
```typescript
{
  task_id: string
  job_id: string
  target_id: string
  task_type: "crawler" | "static_analysis" | "contract_audit" | ...
  priority: "low" | "medium" | "high"
  status: "queued" | "running" | "completed" | "failed"
  created_at: string
  completed_at?: string
  result_id?: string
}
```

### Vulnerability
```typescript
{
  vulnerability_id: string
  type: string
  severity: "critical" | "high" | "medium" | "low" | "info"
  title: string
  description: string
  affected_component: string
  cve_id?: string
  cvss_score?: number
  remediation?: string
  references?: string[]
}
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the GNU Affero General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- OWASP BLT Project
- Cloudflare Workers Platform
- Security research community

## Support

For issues and questions, please open an issue on GitHub.

---

Built with ❤️ by the OWASP BLT community
