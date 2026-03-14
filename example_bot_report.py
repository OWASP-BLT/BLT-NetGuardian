"""
Example: AI Bot - Report a Vulnerability

This script demonstrates how the AI bot reports a vulnerability
using PGP encryption to ensure only the company can read it.
"""

from secure_reporter import SecureVulnerabilityReporter
from dotenv import load_dotenv
import os


def main():
    print("=== AI Bot: Secure Vulnerability Reporting ===\n")
    
    # Initialize reporter
    reporter = SecureVulnerabilityReporter(gpg_home='./gpg_home')
    
    # Step 1: Import company's public key
    print("Step 1: Importing company's public key...")
    try:
        import_result = reporter.import_public_key('company_public_key.asc')
        print(f"✓ Imported {import_result['count']} key(s)")
        fingerprint = import_result['fingerprints'][0]
        print(f"✓ Fingerprint: {fingerprint}\n")
    except FileNotFoundError:
        print("ERROR: company_public_key.asc not found!")
        print("Please obtain the company's public key first.")
        return
    
    # Step 2: Create vulnerability report
    print("Step 2: Creating vulnerability report...")
    vulnerability = reporter.create_vulnerability_report(
        title="SQL Injection in User Authentication Module",
        description=(
            "A SQL injection vulnerability was discovered in the user authentication "
            "module at /api/auth/login. The 'username' parameter is not properly "
            "sanitized, allowing an attacker to inject arbitrary SQL commands. "
            "This could lead to unauthorized access to user accounts and database exposure."
        ),
        severity="critical",
        affected_systems=[
            "Web API v2.1.0",
            "Authentication Service",
            "User Database"
        ],
        cve_ids=["CVE-2024-XXXXX"],
        remediation=(
            "1. Implement parameterized queries for all database operations\n"
            "2. Add input validation for username field\n"
            "3. Deploy web application firewall (WAF) rules\n"
            "4. Conduct security code review of authentication module"
        ),
        additional_data={
            "proof_of_concept": "username=' OR '1'='1' --",
            "affected_endpoints": ["/api/auth/login", "/api/auth/validate"],
            "discovered_by": "AI Security Bot",
            "confidence_level": "high"
        }
    )
    print("✓ Vulnerability report created\n")
    
    # Step 3: Encrypt the report
    print("Step 3: Encrypting report with company's public key...")
    encrypted_path = reporter.encrypt_vulnerability_report(
        vulnerability_data=vulnerability,
        recipient_fingerprint=fingerprint
    )
    print(f"✓ Report encrypted: {encrypted_path}\n")
    
    # Step 4: Send via email (optional)
    print("Step 4: Email delivery (optional)...")
    load_dotenv()
    
    # Check if email credentials are configured
    if all([
        os.getenv('SMTP_SERVER'),
        os.getenv('SMTP_PORT'),
        os.getenv('SENDER_EMAIL'),
        os.getenv('SENDER_PASSWORD'),
        os.getenv('RECIPIENT_EMAIL')
    ]):
        print("Sending encrypted report via email...")
        success = reporter.send_encrypted_report_via_email(
            encrypted_report_path=encrypted_path,
            recipient_email=os.getenv('RECIPIENT_EMAIL'),
            smtp_server=os.getenv('SMTP_SERVER'),
            smtp_port=int(os.getenv('SMTP_PORT')),
            sender_email=os.getenv('SENDER_EMAIL'),
            sender_password=os.getenv('SENDER_PASSWORD'),
            use_tls=True
        )
        
        if success:
            print("✓ Email sent successfully!")
        else:
            print("✗ Failed to send email")
    else:
        print("⊘ Email not configured (set environment variables in .env)")
        print("  Encrypted file is saved locally for manual delivery")
    
    print("\n" + "="*60)
    print("REPORT SUMMARY:")
    print("="*60)
    print(f"Status: Successfully encrypted")
    print(f"File: {encrypted_path}")
    print(f"Security: Only the company can decrypt this report")
    print("="*60)


if __name__ == "__main__":
    main()
