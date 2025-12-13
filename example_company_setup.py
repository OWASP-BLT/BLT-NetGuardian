"""
Example: Company Setup - Generate PGP Key Pair

This script demonstrates how a company should set up their PGP keys
for receiving encrypted vulnerability reports.

Run this ONCE to generate your organization's key pair.
"""

from secure_reporter import generate_key_pair
import os


def main():
    print("=== Company PGP Key Generation ===\n")
    
    # Configuration
    COMPANY_NAME = "OWASP BLT Security Team"
    COMPANY_EMAIL = "security@owasp-blt.org"
    
    # IMPORTANT: Use a strong passphrase and store it securely!
    # In production, use a secure method to obtain the passphrase
    passphrase = input("Enter a strong passphrase for the private key: ")
    
    if len(passphrase) < 16:
        print("WARNING: Passphrase should be at least 16 characters for security!")
        confirm = input("Continue anyway? (yes/no): ")
        if confirm.lower() != 'yes':
            print("Aborted.")
            return
    
    print("\nGenerating 4096-bit RSA key pair...")
    print("This may take a minute...\n")
    
    # Generate key pair
    result = generate_key_pair(
        name=COMPANY_NAME,
        email=COMPANY_EMAIL,
        passphrase=passphrase,
        key_type='RSA',
        key_length=4096,
        gpg_home='./gpg_home'  # Use custom directory for this example
    )
    
    print("✓ Key pair generated successfully!\n")
    print(f"Fingerprint: {result['fingerprint']}\n")
    
    # Save public key (safe to distribute)
    with open('company_public_key.asc', 'w') as f:
        f.write(result['public_key'])
    print("✓ Public key saved to: company_public_key.asc")
    
    # Save private key (MUST BE KEPT SECURE!)
    with open('company_private_key.asc', 'w') as f:
        f.write(result['private_key'])
    print("✓ Private key saved to: company_private_key.asc")
    
    print("\n" + "="*60)
    print("IMPORTANT SECURITY INSTRUCTIONS:")
    print("="*60)
    print("1. SECURE THE PRIVATE KEY:")
    print("   - Store company_private_key.asc in a secure location")
    print("   - Use hardware security module (HSM) if available")
    print("   - Never commit to version control")
    print("   - Restrict access to authorized personnel only")
    print("\n2. DISTRIBUTE THE PUBLIC KEY:")
    print("   - Share company_public_key.asc with the AI bot")
    print("   - Can be published on your website")
    print("   - Can be uploaded to public key servers")
    print("\n3. REMEMBER THE PASSPHRASE:")
    print("   - Store it in a password manager")
    print("   - You need it to decrypt reports")
    print("="*60)


if __name__ == "__main__":
    main()
