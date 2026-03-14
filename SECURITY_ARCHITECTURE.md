# Security Architecture

## Overview

BLT-NetGuardian implements a zero-trust security architecture for vulnerability reporting using public key cryptography (PGP/GPG). This document details the security design, threat model, and security considerations.

## Security Design Principles

### 1. Zero-Trust Architecture

- **No Shared Secrets**: No passwords or keys are transmitted between parties
- **Public Key Distribution**: Only public keys need to be shared
- **Private Key Security**: Private keys never leave the company's secure environment
- **End-to-End Encryption**: Data is encrypted at source and decrypted only at destination

### 2. Defense in Depth

- **Encryption Layer**: PGP/GPG encryption for data at rest and in transit
- **Access Control**: Private key access restricted to authorized personnel
- **Audit Logging**: All decryption operations should be logged
- **Key Management**: Proper key lifecycle management (generation, rotation, revocation)

### 3. Principle of Least Privilege

- **Bot Permissions**: AI bot only has access to public key (encryption only)
- **Company Permissions**: Only authorized personnel can access private key
- **Separation of Duties**: Key generation, storage, and usage can be separated

## Threat Model

### Assets to Protect

1. **Vulnerability Information**: Sensitive security data about discovered vulnerabilities
2. **Private Key**: Company's private PGP key
3. **Private Key Passphrase**: Passphrase protecting the private key

### Threat Actors

1. **External Attackers**: Attempting to intercept vulnerability reports
2. **Man-in-the-Middle**: Attempting to intercept communications
3. **Insider Threats**: Unauthorized access to systems or keys
4. **Compromised Infrastructure**: Email servers, storage systems

### Attack Vectors & Mitigations

#### 1. Interception of Encrypted Reports

**Attack**: Attacker intercepts encrypted vulnerability report in transit.

**Impact**: Low - Attacker cannot decrypt without private key.

**Mitigations**:
- Strong encryption (4096-bit RSA)
- No password/key transmitted with report
- Even with quantum computers, would take significant time to break

#### 2. Public Key Substitution

**Attack**: Attacker substitutes legitimate public key with their own.

**Impact**: High - Reports would be encrypted with attacker's key.

**Mitigations**:
- Verify public key fingerprint through out-of-band channel
- Use key servers with reputation systems
- Implement key pinning in bot configuration
- Support for signed public keys

#### 3. Private Key Compromise

**Attack**: Attacker gains access to company's private key.

**Impact**: Critical - All past and future reports can be decrypted.

**Mitigations**:
- Store private key in Hardware Security Module (HSM)
- Use strong passphrase (16+ characters)
- Implement key rotation policy
- Monitor key usage and alert on anomalies
- Use key expiration dates
- Implement key revocation procedures

#### 4. Passphrase Compromise

**Attack**: Attacker obtains private key passphrase.

**Impact**: High - Combined with private key, can decrypt reports.

**Mitigations**:
- Use strong, unique passphrase
- Store in enterprise password manager
- Never log or display passphrase
- Implement passphrase rotation
- Use hardware tokens for additional authentication

#### 5. Replay Attacks

**Attack**: Attacker resends previously captured encrypted reports.

**Impact**: Low - Reports are timestamped, and duplicate reports are identifiable.

**Mitigations**:
- Include timestamps in reports
- Implement report tracking system
- Use unique identifiers for each report

#### 6. Denial of Service

**Attack**: Attacker floods system with fake encrypted reports.

**Impact**: Medium - Legitimate reports may be delayed or missed.

**Mitigations**:
- Implement rate limiting on email reception
- Use sender authentication (SPF, DKIM, DMARC)
- Monitor for unusual patterns
- Implement priority queuing for verified senders

## Cryptographic Details

### Encryption Algorithm

- **Primary**: RSA-4096
- **Fallback**: RSA-2048 (minimum)
- **Standard**: OpenPGP (RFC 4880)

### Key Properties

```
Algorithm: RSA
Key Length: 4096 bits
Encryption: CAST5, AES256, AES192, AES, 3DES
Digest: SHA512, SHA384, SHA256, SHA224, SHA1
Compression: ZLIB, BZIP2, ZIP
```

### Security Margins

- **RSA-4096**: Estimated secure until ~2030+ against classical computers
- **Quantum Resistance**: Not quantum-resistant, but migration path available (post-quantum PGP)

## Key Management

### Key Lifecycle

1. **Generation**
   - Generate using secure random number generator
   - Use appropriate key length (4096 bits)
   - Set expiration date (e.g., 1-2 years)
   - Add user ID with company information

2. **Distribution**
   - Publish public key to key servers
   - Host on company website with HTTPS
   - Verify fingerprint through multiple channels
   - Sign key with other trusted keys

3. **Usage**
   - Bot: Only encryption operations
   - Company: Decryption operations only by authorized personnel
   - Log all key operations

4. **Rotation**
   - Generate new key before expiration
   - Transition period with both keys active
   - Communicate new key to all stakeholders
   - Revoke old key after transition

5. **Revocation**
   - Generate revocation certificate during key creation
   - Store revocation certificate securely
   - Publish revocation if key is compromised
   - Notify all stakeholders immediately

### Key Storage Best Practices

#### For Companies (Private Key)

1. **Hardware Security Module (HSM)**
   - Ideal: Store in FIPS 140-2 Level 2+ HSM
   - Tamper-resistant hardware
   - Audit logging built-in

2. **Encrypted Storage**
   - Encrypt private key at rest
   - Use strong passphrase
   - Store on encrypted filesystem

3. **Access Control**
   - Multi-factor authentication required
   - Role-based access control (RBAC)
   - Minimum number of authorized users
   - Regular access reviews

4. **Backup**
   - Encrypted backup of private key
   - Store in secure, separate location
   - Test restore procedures regularly
   - Document key recovery process

#### For Bots (Public Key)

1. **Configuration Management**
   - Store public key in secure configuration
   - Version control (public keys are not secret)
   - Verify fingerprint on import

2. **Key Pinning**
   - Pin expected key fingerprint
   - Alert on fingerprint mismatch
   - Require manual intervention for key changes

## Comparison with Alternatives

### vs. Password-Protected Zip Files

**Security Advantages**:
- No password transmission required
- Stronger encryption (RSA-4096 vs. ZIP AES-256 with weak password derivation)
- No brute-force vulnerability
- Better key management
- Supports key revocation

**Operational Advantages**:
- No need to coordinate password sharing
- Simpler workflow (one-step encryption)
- Standard tools available everywhere
- Better audit trail

### vs. S/MIME

**Advantages**:
- Similar security model
- PGP more widely used in security community
- No certificate authority required
- Better tool support in security contexts

**Disadvantages of S/MIME**:
- Requires certificate authority (cost, dependency)
- More complex certificate management
- Less familiar to security researchers

### vs. Third-Party Encrypted Sharing

**Security Advantages**:
- No third-party trust required
- No data residency concerns
- Complete control over encryption
- No service availability dependency

**Privacy Advantages**:
- No metadata leakage to third parties
- No usage tracking
- No terms of service restrictions

## Implementation Security

### Code Security

1. **Dependency Management**
   - Use well-maintained libraries (`python-gnupg`, `cryptography`)
   - Regular security updates
   - Pin specific versions
   - Monitor for vulnerabilities

2. **Input Validation**
   - Validate all inputs
   - Sanitize file paths
   - Check key fingerprints
   - Verify encryption success before sending

3. **Error Handling**
   - Don't leak sensitive information in errors
   - Generic error messages for authentication failures
   - Log detailed errors securely
   - Fail securely (fail closed)

4. **Secure Defaults**
   - Always trust imported keys (after verification)
   - Use ASCII armor for better compatibility
   - Maximum key length by default
   - TLS for email transmission

### Operational Security

1. **Email Security**
   - Use TLS for SMTP
   - Implement SPF/DKIM/DMARC
   - Use app-specific passwords
   - Monitor for suspicious activity

2. **Logging & Monitoring**
   - Log all encryption operations
   - Log all decryption attempts
   - Alert on key import events
   - Monitor for unusual patterns

3. **Incident Response**
   - Document key compromise procedures
   - Prepare revocation certificates
   - Maintain contact list for notifications
   - Regular incident response drills

## Compliance & Standards

### Standards Compliance

- **OpenPGP**: RFC 4880
- **Encryption**: NIST-approved algorithms
- **Key Length**: Meets NIST recommendations

### Regulatory Considerations

- **GDPR**: End-to-end encryption supports data protection
- **HIPAA**: Can be part of encryption compliance
- **PCI DSS**: Meets encryption requirements for data in transit
- **SOC 2**: Supports security and confidentiality criteria

## Future Enhancements

### Planned Improvements

1. **Post-Quantum Cryptography**
   - Monitor PQC standardization (NIST)
   - Plan migration to quantum-resistant algorithms
   - Support hybrid encryption (classical + PQC)

2. **Hardware Token Support**
   - Support for YubiKey and other tokens
   - Hardware-backed key generation
   - Additional authentication factor

3. **Key Transparency**
   - Implement key transparency logs
   - Monitor for key substitution attacks
   - Public audit trail

4. **Automated Key Rotation**
   - Automated key generation
   - Gradual rollout of new keys
   - Automated revocation of expired keys

5. **Digital Signatures**
   - Sign reports with bot's key
   - Verify report authenticity
   - Non-repudiation

## Security Recommendations

### For Companies

1. ✅ Generate 4096-bit RSA key
2. ✅ Use strong passphrase (16+ characters)
3. ✅ Store private key in HSM if possible
4. ✅ Publish public key on multiple channels
5. ✅ Set key expiration date (1-2 years)
6. ✅ Generate and store revocation certificate
7. ✅ Implement key rotation policy
8. ✅ Restrict private key access
9. ✅ Log all decryption operations
10. ✅ Regular security audits

### For AI Bots

1. ✅ Verify public key fingerprint
2. ✅ Pin expected key
3. ✅ Alert on fingerprint mismatch
4. ✅ Verify encryption success
5. ✅ Use TLS for email transmission
6. ✅ Don't log sensitive data
7. ✅ Implement retry logic
8. ✅ Monitor for errors
9. ✅ Regular security updates
10. ✅ Incident response plan

## Conclusion

The BLT-NetGuardian architecture provides a robust, zero-trust solution for secure vulnerability reporting. By leveraging industry-standard PGP/GPG encryption and following security best practices, it ensures that vulnerability data remains confidential and accessible only to authorized personnel.

The architecture is designed to be simple to use while maintaining strong security guarantees. It requires minimal trust assumptions and no complex coordination, making it ideal for automated vulnerability reporting systems.
