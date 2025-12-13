"""
Secure Vulnerability Reporter using PGP/GPG Encryption

This module provides a zero-trust, end-to-end encrypted way to report vulnerabilities
discovered by the AI bot. It uses public key cryptography to ensure only the intended
recipient (the company) can decrypt the vulnerability reports.

Security Features:
- Zero-trust: No shared secrets or pre-established trust required
- End-to-end encryption: Only company's private key can decrypt
- No dependency on third-party encryption services
- Industry-standard PGP/GPG encryption
"""

import gnupg
import json
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from email.mime.text import MIMEText
from datetime import datetime
from typing import Dict, Optional, Any
import tempfile
import shutil


class SecureVulnerabilityReporter:
    """
    Handles secure vulnerability reporting using PGP encryption.
    
    The reporter encrypts vulnerability data using the company's public PGP key,
    ensuring that only the company (holding the corresponding private key) can
    decrypt and read the vulnerability information.
    """
    
    def __init__(self, gpg_home: Optional[str] = None):
        """
        Initialize the vulnerability reporter.
        
        Args:
            gpg_home: Optional custom GPG home directory. If None, uses system default.
        """
        if gpg_home:
            os.makedirs(gpg_home, exist_ok=True)
            self.gpg = gnupg.GPG(gnupghome=gpg_home)
        else:
            self.gpg = gnupg.GPG()
        
        self.reports_dir = "reports"
        os.makedirs(self.reports_dir, exist_ok=True)
    
    def import_public_key(self, public_key_path: str) -> Dict[str, Any]:
        """
        Import the company's public PGP key for encryption.
        
        Args:
            public_key_path: Path to the public key file (.asc or .gpg)
            
        Returns:
            Dictionary with import results including fingerprint
            
        Raises:
            FileNotFoundError: If the public key file doesn't exist
            ValueError: If the key import fails
        """
        if not os.path.exists(public_key_path):
            raise FileNotFoundError(f"Public key file not found: {public_key_path}")
        
        with open(public_key_path, 'r') as key_file:
            key_data = key_file.read()
        
        import_result = self.gpg.import_keys(key_data)
        
        if not import_result.count:
            raise ValueError("Failed to import public key. Please verify the key format.")
        
        return {
            'count': import_result.count,
            'fingerprints': import_result.fingerprints,
            'results': import_result.results
        }
    
    def list_keys(self) -> list:
        """
        List all public keys available in the keyring.
        
        Returns:
            List of key information dictionaries
        """
        return self.gpg.list_keys()
    
    def encrypt_vulnerability_report(
        self, 
        vulnerability_data: Dict[str, Any],
        recipient_fingerprint: str
    ) -> str:
        """
        Encrypt vulnerability data using recipient's public key.
        
        Args:
            vulnerability_data: Dictionary containing vulnerability details
            recipient_fingerprint: GPG fingerprint of the recipient's public key
            
        Returns:
            Path to the encrypted report file
            
        Raises:
            ValueError: If encryption fails
        """
        # Add metadata to the report
        report = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'report_type': 'vulnerability',
            'version': '1.0',
            'data': vulnerability_data
        }
        
        # Convert to JSON
        report_json = json.dumps(report, indent=2)
        
        # Encrypt the report
        encrypted_data = self.gpg.encrypt(
            report_json,
            recipient_fingerprint,
            always_trust=True,  # Trust the imported public key
            armor=True  # Use ASCII-armored output
        )
        
        if not encrypted_data.ok:
            raise ValueError(f"Encryption failed: {encrypted_data.status}")
        
        # Save encrypted report
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"vulnerability_report_{timestamp}.pgp"
        filepath = os.path.join(self.reports_dir, filename)
        
        with open(filepath, 'w') as f:
            f.write(str(encrypted_data))
        
        return filepath
    
    def create_vulnerability_report(
        self,
        title: str,
        description: str,
        severity: str,
        affected_systems: list,
        cve_ids: Optional[list] = None,
        remediation: Optional[str] = None,
        additional_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a structured vulnerability report.
        
        Args:
            title: Brief title of the vulnerability
            description: Detailed description of the vulnerability
            severity: Severity level (e.g., 'critical', 'high', 'medium', 'low')
            affected_systems: List of affected systems/components
            cve_ids: Optional list of related CVE identifiers
            remediation: Optional remediation guidance
            additional_data: Any additional data to include
            
        Returns:
            Dictionary containing the structured vulnerability report
        """
        report = {
            'title': title,
            'description': description,
            'severity': severity.lower(),
            'affected_systems': affected_systems,
            'discovery_timestamp': datetime.utcnow().isoformat() + 'Z',
        }
        
        if cve_ids:
            report['cve_ids'] = cve_ids
        
        if remediation:
            report['remediation'] = remediation
        
        if additional_data:
            report['additional_data'] = additional_data
        
        return report
    
    def send_encrypted_report_via_email(
        self,
        encrypted_report_path: str,
        recipient_email: str,
        smtp_server: str,
        smtp_port: int,
        sender_email: str,
        sender_password: str,
        use_tls: bool = True
    ) -> bool:
        """
        Send the encrypted report via email.
        
        Args:
            encrypted_report_path: Path to the encrypted report file
            recipient_email: Email address of the recipient
            smtp_server: SMTP server address
            smtp_port: SMTP server port
            sender_email: Sender's email address
            sender_password: Sender's email password
            use_tls: Whether to use TLS (default: True)
            
        Returns:
            True if email was sent successfully, False otherwise
        """
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = recipient_email
            msg['Subject'] = 'Encrypted Security Vulnerability Report'
            
            # Email body
            body = """
This email contains an encrypted security vulnerability report.

The report has been encrypted using PGP/GPG with your organization's public key.
Only holders of the corresponding private key can decrypt this report.

To decrypt the attached file:
1. Save the attachment to your system
2. Use GPG to decrypt: gpg --decrypt vulnerability_report_*.pgp

Security Notice:
- This report is encrypted end-to-end
- No third parties can access the contents
- Please process this report through your secure vulnerability management workflow

For questions or issues, please contact your security team.
            """.strip()
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Attach encrypted file
            with open(encrypted_report_path, 'rb') as attachment:
                part = MIMEBase('application', 'pgp-encrypted')
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename= {os.path.basename(encrypted_report_path)}'
                )
                msg.attach(part)
            
            # Send email
            if use_tls:
                server = smtplib.SMTP(smtp_server, smtp_port)
                server.starttls()
            else:
                server = smtplib.SMTP_SSL(smtp_server, smtp_port)
            
            server.login(sender_email, sender_password)
            server.send_message(msg)
            server.quit()
            
            return True
        
        except Exception as e:
            print(f"Failed to send email: {str(e)}")
            return False


class DecryptionHelper:
    """
    Helper class for the recipient to decrypt vulnerability reports.
    
    Note: This should only be used by the company receiving the reports,
    as it requires access to the private key.
    """
    
    def __init__(self, gpg_home: Optional[str] = None):
        """
        Initialize the decryption helper.
        
        Args:
            gpg_home: Optional custom GPG home directory
        """
        if gpg_home:
            self.gpg = gnupg.GPG(gnupghome=gpg_home)
        else:
            self.gpg = gnupg.GPG()
    
    def decrypt_report(self, encrypted_file_path: str, passphrase: str) -> Dict[str, Any]:
        """
        Decrypt an encrypted vulnerability report.
        
        Args:
            encrypted_file_path: Path to the encrypted report file
            passphrase: Passphrase for the private key
            
        Returns:
            Decrypted report as a dictionary
            
        Raises:
            ValueError: If decryption fails
            FileNotFoundError: If the encrypted file doesn't exist
        """
        if not os.path.exists(encrypted_file_path):
            raise FileNotFoundError(f"Encrypted file not found: {encrypted_file_path}")
        
        with open(encrypted_file_path, 'r') as f:
            encrypted_data = f.read()
        
        decrypted_data = self.gpg.decrypt(encrypted_data, passphrase=passphrase)
        
        if not decrypted_data.ok:
            raise ValueError(f"Decryption failed: {decrypted_data.status}")
        
        # Parse JSON
        report = json.loads(str(decrypted_data))
        
        return report


def generate_key_pair(
    name: str,
    email: str,
    passphrase: str,
    key_type: str = 'RSA',
    key_length: int = 4096,
    gpg_home: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate a new PGP key pair for the company.
    
    This function should be run once by the company to generate their keys.
    The public key should be made available to the AI bot, while the private
    key must be kept secure.
    
    Args:
        name: Name associated with the key
        email: Email associated with the key
        passphrase: Passphrase to protect the private key
        key_type: Type of key (default: RSA)
        key_length: Key length in bits (default: 4096)
        gpg_home: Optional custom GPG home directory
        
    Returns:
        Dictionary with key generation results including fingerprint
    """
    if gpg_home:
        os.makedirs(gpg_home, exist_ok=True)
        gpg = gnupg.GPG(gnupghome=gpg_home)
    else:
        gpg = gnupg.GPG()
    
    key_input = gpg.gen_key_input(
        name_real=name,
        name_email=email,
        passphrase=passphrase,
        key_type=key_type,
        key_length=key_length
    )
    
    key = gpg.gen_key(key_input)
    
    if not key:
        raise ValueError("Key generation failed")
    
    # Export public key
    public_key = gpg.export_keys(str(key))
    
    # Export private key (should be kept secure!)
    private_key = gpg.export_keys(str(key), secret=True, passphrase=passphrase)
    
    return {
        'fingerprint': str(key),
        'public_key': public_key,
        'private_key': private_key
    }
