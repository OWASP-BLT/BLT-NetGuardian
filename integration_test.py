#!/usr/bin/env python3
"""
Full Integration Test

This script demonstrates the complete end-to-end workflow:
1. Company generates keys
2. AI bot reports vulnerability
3. Company decrypts and reads report
"""

import os
import sys
import tempfile
import shutil
from secure_reporter import (
    SecureVulnerabilityReporter,
    DecryptionHelper,
    generate_key_pair
)


def print_section(title):
    """Print a formatted section header."""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\n")


def main():
    """Run full integration test."""
    # Use temporary directory for this demo
    demo_dir = tempfile.mkdtemp(prefix='blt_netguardian_demo_')
    gpg_home = os.path.join(demo_dir, 'gpg_home')
    os.makedirs(gpg_home)
    
    print_section("INTEGRATION TEST: Full Vulnerability Reporting Workflow")
    
    try:
        # Step 1: Company generates keys
        print_section("STEP 1: Company Generates Key Pair")
        print("Generating 2048-bit RSA key pair (using 2048 for faster demo)...")
        
        COMPANY_NAME = "OWASP BLT Security Team"
        COMPANY_EMAIL = "security@owasp-blt.org"
        PASSPHRASE = "demo_secure_passphrase_12345"
        
        key_result = generate_key_pair(
            name=COMPANY_NAME,
            email=COMPANY_EMAIL,
            passphrase=PASSPHRASE,
            key_type='RSA',
            key_length=2048,  # Smaller for demo speed
            gpg_home=gpg_home
        )
        
        fingerprint = key_result['fingerprint']
        print(f"✓ Key pair generated successfully")
        print(f"  Fingerprint: {fingerprint}")
        
        # Save public key
        public_key_file = os.path.join(demo_dir, 'company_public_key.asc')
        with open(public_key_file, 'w') as f:
            f.write(key_result['public_key'])
        print(f"✓ Public key saved: {public_key_file}")
        
        # Step 2: AI Bot reports vulnerability
        print_section("STEP 2: AI Bot Creates and Encrypts Vulnerability Report")
        
        # Initialize reporter
        reporter = SecureVulnerabilityReporter(gpg_home=gpg_home)
        
        # Import company's public key
        print("Importing company's public key...")
        import_result = reporter.import_public_key(public_key_file)
        print(f"✓ Imported key: {import_result['fingerprints'][0]}")
        
        # Create vulnerability report
        print("\nCreating vulnerability report...")
        vulnerability = reporter.create_vulnerability_report(
            title="Critical SQL Injection in Authentication Module",
            description=(
                "A SQL injection vulnerability was discovered in the user authentication "
                "module at /api/auth/login endpoint. The 'username' parameter is not "
                "properly sanitized, allowing an attacker to inject arbitrary SQL commands. "
                "This could lead to unauthorized database access, data exfiltration, and "
                "complete system compromise."
            ),
            severity="critical",
            affected_systems=[
                "Web API v2.1.0",
                "Authentication Service v1.5.2",
                "User Database (PostgreSQL 14)"
            ],
            cve_ids=["CVE-2024-12345"],
            remediation=(
                "1. Immediately apply parameterized queries for all database operations\n"
                "2. Implement input validation and sanitization for username field\n"
                "3. Deploy web application firewall (WAF) rules to block SQL injection attempts\n"
                "4. Conduct comprehensive security code review of authentication module\n"
                "5. Enable database query logging for monitoring\n"
                "6. Update to latest framework version with security patches"
            ),
            additional_data={
                "proof_of_concept": "username=' OR '1'='1' -- ",
                "affected_endpoints": ["/api/auth/login", "/api/auth/validate"],
                "discovered_by": "AI Security Bot v3.0",
                "confidence_level": "high",
                "cvss_score": 9.8,
                "attack_vector": "Network",
                "privileges_required": "None"
            }
        )
        print("✓ Vulnerability report created")
        
        # Encrypt the report
        print("\nEncrypting report with company's public key...")
        encrypted_path = reporter.encrypt_vulnerability_report(
            vulnerability_data=vulnerability,
            recipient_fingerprint=fingerprint
        )
        print(f"✓ Report encrypted: {encrypted_path}")
        print(f"  File size: {os.path.getsize(encrypted_path)} bytes")
        
        # Step 3: Company decrypts report
        print_section("STEP 3: Company Receives and Decrypts Report")
        
        print("Decrypting report with private key...")
        helper = DecryptionHelper(gpg_home=gpg_home)
        decrypted_report = helper.decrypt_report(encrypted_path, PASSPHRASE)
        print("✓ Report decrypted successfully")
        
        # Display the report
        print_section("DECRYPTED VULNERABILITY REPORT")
        
        print(f"Report Metadata:")
        print(f"  Version: {decrypted_report.get('version')}")
        print(f"  Type: {decrypted_report.get('report_type')}")
        print(f"  Timestamp: {decrypted_report.get('timestamp')}")
        
        data = decrypted_report['data']
        print(f"\n--- Vulnerability Details ---")
        print(f"Title: {data['title']}")
        print(f"Severity: {data['severity'].upper()}")
        print(f"Discovery Time: {data['discovery_timestamp']}")
        
        print(f"\nDescription:")
        print(f"{data['description']}")
        
        print(f"\nAffected Systems:")
        for system in data['affected_systems']:
            print(f"  • {system}")
        
        if 'cve_ids' in data:
            print(f"\nCVE IDs:")
            for cve in data['cve_ids']:
                print(f"  • {cve}")
        
        if 'remediation' in data:
            print(f"\nRemediation Steps:")
            for line in data['remediation'].split('\n'):
                print(f"  {line}")
        
        if 'additional_data' in data:
            print(f"\nAdditional Information:")
            for key, value in data['additional_data'].items():
                if isinstance(value, list):
                    print(f"  {key}:")
                    for item in value:
                        print(f"    - {item}")
                else:
                    print(f"  {key}: {value}")
        
        print_section("✓ INTEGRATION TEST COMPLETED SUCCESSFULLY")
        
        print("Summary:")
        print("  1. ✓ Company generated key pair")
        print("  2. ✓ AI bot imported public key")
        print("  3. ✓ AI bot created vulnerability report")
        print("  4. ✓ AI bot encrypted report (end-to-end encryption)")
        print("  5. ✓ Company decrypted report with private key")
        print("  6. ✓ Vulnerability data successfully transmitted securely")
        
        print("\nSecurity Notes:")
        print("  • Report was encrypted with strong PGP/GPG encryption")
        print("  • Only the company's private key could decrypt it")
        print("  • No passwords or keys were transmitted")
        print("  • Zero-trust architecture maintained throughout")
        
        return True
        
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Cleanup
        print(f"\nCleaning up temporary files: {demo_dir}")
        shutil.rmtree(demo_dir)
        if os.path.exists('reports'):
            shutil.rmtree('reports')


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
