"""
Example: Company - Decrypt Vulnerability Report

This script demonstrates how the company decrypts and reads
the vulnerability reports they receive.
"""

from secure_reporter import DecryptionHelper
import json
import sys


def main():
    print("=== Company: Decrypt Vulnerability Report ===\n")
    
    if len(sys.argv) < 2:
        print("Usage: python example_company_decrypt.py <encrypted_report.pgp>")
        print("\nExample:")
        print("  python example_company_decrypt.py reports/vulnerability_report_20241213_120000.pgp")
        return
    
    encrypted_file = sys.argv[1]
    
    # Initialize decryption helper
    helper = DecryptionHelper(gpg_home='./gpg_home')
    
    # Get passphrase securely
    # In production, use a secure method (e.g., HSM, key management service)
    import getpass
    passphrase = getpass.getpass("Enter private key passphrase: ")
    
    print("\nDecrypting report...")
    
    try:
        # Decrypt the report
        report = helper.decrypt_report(encrypted_file, passphrase)
        
        print("✓ Report decrypted successfully!\n")
        print("="*60)
        print("VULNERABILITY REPORT")
        print("="*60)
        
        # Display report metadata
        print(f"\nReport Version: {report.get('version', 'N/A')}")
        print(f"Report Type: {report.get('report_type', 'N/A')}")
        print(f"Timestamp: {report.get('timestamp', 'N/A')}")
        
        # Display vulnerability details
        data = report.get('data', {})
        print(f"\n--- Vulnerability Details ---")
        print(f"Title: {data.get('title', 'N/A')}")
        print(f"Severity: {data.get('severity', 'N/A').upper()}")
        print(f"Discovery Time: {data.get('discovery_timestamp', 'N/A')}")
        
        print(f"\nDescription:")
        print(f"  {data.get('description', 'N/A')}")
        
        if 'affected_systems' in data:
            print(f"\nAffected Systems:")
            for system in data['affected_systems']:
                print(f"  - {system}")
        
        if 'cve_ids' in data:
            print(f"\nCVE IDs:")
            for cve in data['cve_ids']:
                print(f"  - {cve}")
        
        if 'remediation' in data:
            print(f"\nRemediation:")
            print(f"  {data['remediation']}")
        
        if 'additional_data' in data:
            print(f"\nAdditional Data:")
            for key, value in data['additional_data'].items():
                if isinstance(value, list):
                    print(f"  {key}:")
                    for item in value:
                        print(f"    - {item}")
                else:
                    print(f"  {key}: {value}")
        
        print("\n" + "="*60)
        
        # Optionally save decrypted report as JSON
        save = input("\nSave decrypted report as JSON? (yes/no): ")
        if save.lower() == 'yes':
            output_file = encrypted_file.replace('.pgp', '_decrypted.json')
            with open(output_file, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"✓ Saved to: {output_file}")
        
    except FileNotFoundError as e:
        print(f"✗ Error: {e}")
    except ValueError as e:
        print(f"✗ Error: {e}")
        print("  Possible causes:")
        print("  - Incorrect passphrase")
        print("  - Wrong private key")
        print("  - Corrupted encrypted file")
    except json.JSONDecodeError:
        print("✗ Error: Failed to parse decrypted data as JSON")
        print("  The file may be corrupted or not a valid report")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")


if __name__ == "__main__":
    main()
