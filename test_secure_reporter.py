"""
Test Suite for Secure Vulnerability Reporter

This test suite validates the core functionality of the secure reporting system.
"""

import unittest
import os
import json
import tempfile
import shutil
from secure_reporter import (
    SecureVulnerabilityReporter,
    DecryptionHelper,
    generate_key_pair
)


class TestSecureVulnerabilityReporter(unittest.TestCase):
    """Test cases for the secure vulnerability reporting system."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment once for all tests."""
        # Create temporary directory for GPG home
        cls.gpg_home = tempfile.mkdtemp(prefix='gpg_test_')
        
        # Generate test key pair
        # WARNING: This uses a test passphrase for testing purposes only.
        # NEVER use these test keys or passphrases in production!
        print("\nGenerating test key pair...")
        print("WARNING: Using test credentials - NOT FOR PRODUCTION USE")
        cls.key_result = generate_key_pair(
            name="Test User",
            email="test@example.com",
            passphrase="test_passphrase_12345",  # TEST ONLY - use strong passphrases in production
            key_length=2048,  # Smaller for faster tests
            gpg_home=cls.gpg_home
        )
        cls.fingerprint = cls.key_result['fingerprint']
        
        # Save public key to file
        cls.public_key_file = os.path.join(cls.gpg_home, 'test_public.asc')
        with open(cls.public_key_file, 'w') as f:
            f.write(cls.key_result['public_key'])
        
        print(f"Test key fingerprint: {cls.fingerprint}")
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test environment after all tests."""
        if os.path.exists(cls.gpg_home):
            shutil.rmtree(cls.gpg_home)
        if os.path.exists('reports'):
            shutil.rmtree('reports')
    
    def test_01_create_vulnerability_report(self):
        """Test creating a structured vulnerability report."""
        reporter = SecureVulnerabilityReporter(gpg_home=self.gpg_home)
        
        report = reporter.create_vulnerability_report(
            title="Test Vulnerability",
            description="This is a test vulnerability",
            severity="high",
            affected_systems=["System A", "System B"],
            cve_ids=["CVE-2024-TEST"],
            remediation="Apply the patch"
        )
        
        self.assertEqual(report['title'], "Test Vulnerability")
        self.assertEqual(report['severity'], "high")
        self.assertIn('discovery_timestamp', report)
        self.assertEqual(len(report['affected_systems']), 2)
        self.assertIn('CVE-2024-TEST', report['cve_ids'])
    
    def test_02_import_public_key(self):
        """Test importing a public key."""
        reporter = SecureVulnerabilityReporter(gpg_home=self.gpg_home)
        
        result = reporter.import_public_key(self.public_key_file)
        
        self.assertEqual(result['count'], 1)
        self.assertIn(self.fingerprint, result['fingerprints'])
    
    def test_03_list_keys(self):
        """Test listing available keys."""
        reporter = SecureVulnerabilityReporter(gpg_home=self.gpg_home)
        reporter.import_public_key(self.public_key_file)
        
        keys = reporter.list_keys()
        
        self.assertGreater(len(keys), 0)
        self.assertTrue(any(k['fingerprint'] == self.fingerprint for k in keys))
    
    def test_04_encrypt_vulnerability_report(self):
        """Test encrypting a vulnerability report."""
        reporter = SecureVulnerabilityReporter(gpg_home=self.gpg_home)
        reporter.import_public_key(self.public_key_file)
        
        vulnerability = reporter.create_vulnerability_report(
            title="Encryption Test Vulnerability",
            description="Testing encryption functionality",
            severity="medium",
            affected_systems=["Test System"]
        )
        
        encrypted_path = reporter.encrypt_vulnerability_report(
            vulnerability_data=vulnerability,
            recipient_fingerprint=self.fingerprint
        )
        
        self.assertTrue(os.path.exists(encrypted_path))
        self.assertTrue(encrypted_path.endswith('.pgp'))
        
        # Verify the file contains encrypted data
        with open(encrypted_path, 'r') as f:
            content = f.read()
            self.assertIn('BEGIN PGP MESSAGE', content)
            self.assertIn('END PGP MESSAGE', content)
    
    def test_05_decrypt_vulnerability_report(self):
        """Test decrypting a vulnerability report."""
        # Create and encrypt a report
        reporter = SecureVulnerabilityReporter(gpg_home=self.gpg_home)
        reporter.import_public_key(self.public_key_file)
        
        original_vulnerability = reporter.create_vulnerability_report(
            title="Decryption Test",
            description="Testing decryption",
            severity="low",
            affected_systems=["System X"],
            additional_data={"test_field": "test_value"}
        )
        
        encrypted_path = reporter.encrypt_vulnerability_report(
            vulnerability_data=original_vulnerability,
            recipient_fingerprint=self.fingerprint
        )
        
        # Decrypt the report
        helper = DecryptionHelper(gpg_home=self.gpg_home)
        decrypted_report = helper.decrypt_report(
            encrypted_path,
            passphrase="test_passphrase_12345"
        )
        
        # Verify decrypted content
        self.assertEqual(decrypted_report['report_type'], 'vulnerability')
        self.assertEqual(decrypted_report['version'], '1.0')
        self.assertIn('timestamp', decrypted_report)
        
        data = decrypted_report['data']
        self.assertEqual(data['title'], "Decryption Test")
        self.assertEqual(data['description'], "Testing decryption")
        self.assertEqual(data['severity'], "low")
        self.assertIn('System X', data['affected_systems'])
        self.assertEqual(data['additional_data']['test_field'], "test_value")
    
    def test_06_end_to_end_workflow(self):
        """Test complete end-to-end workflow."""
        # Step 1: Reporter encrypts
        reporter = SecureVulnerabilityReporter(gpg_home=self.gpg_home)
        reporter.import_public_key(self.public_key_file)
        
        vuln_data = reporter.create_vulnerability_report(
            title="End-to-End Test",
            description="Complete workflow test",
            severity="critical",
            affected_systems=["System 1", "System 2"],
            cve_ids=["CVE-2024-E2E"],
            remediation="Fix immediately"
        )
        
        encrypted_file = reporter.encrypt_vulnerability_report(
            vulnerability_data=vuln_data,
            recipient_fingerprint=self.fingerprint
        )
        
        # Step 2: Recipient decrypts
        helper = DecryptionHelper(gpg_home=self.gpg_home)
        decrypted = helper.decrypt_report(
            encrypted_file,
            passphrase="test_passphrase_12345"
        )
        
        # Step 3: Verify integrity
        self.assertEqual(decrypted['data']['title'], vuln_data['title'])
        self.assertEqual(decrypted['data']['severity'], vuln_data['severity'])
        self.assertEqual(
            decrypted['data']['affected_systems'],
            vuln_data['affected_systems']
        )
    
    def test_07_severity_normalization(self):
        """Test that severity is normalized to lowercase."""
        reporter = SecureVulnerabilityReporter(gpg_home=self.gpg_home)
        
        report = reporter.create_vulnerability_report(
            title="Test",
            description="Test",
            severity="CRITICAL",
            affected_systems=["Test"]
        )
        
        self.assertEqual(report['severity'], "critical")
    
    def test_08_invalid_public_key(self):
        """Test handling of invalid public key file."""
        reporter = SecureVulnerabilityReporter(gpg_home=self.gpg_home)
        
        with self.assertRaises(FileNotFoundError):
            reporter.import_public_key("nonexistent_key.asc")
    
    def test_09_decrypt_nonexistent_file(self):
        """Test handling of nonexistent encrypted file."""
        helper = DecryptionHelper(gpg_home=self.gpg_home)
        
        with self.assertRaises(FileNotFoundError):
            helper.decrypt_report("nonexistent_file.pgp", passphrase="any_passphrase")
    
    def test_10_report_structure(self):
        """Test that report has all required fields."""
        reporter = SecureVulnerabilityReporter(gpg_home=self.gpg_home)
        
        report = reporter.create_vulnerability_report(
            title="Structure Test",
            description="Testing report structure",
            severity="medium",
            affected_systems=["System"]
        )
        
        # Required fields
        self.assertIn('title', report)
        self.assertIn('description', report)
        self.assertIn('severity', report)
        self.assertIn('affected_systems', report)
        self.assertIn('discovery_timestamp', report)
        
        # Timestamp format (ISO 8601 with Z)
        self.assertTrue(report['discovery_timestamp'].endswith('Z'))


def run_tests():
    """Run all tests and display results."""
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(
        TestSecureVulnerabilityReporter
    )
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n✓ All tests passed!")
    else:
        print("\n✗ Some tests failed.")
    
    print("="*70)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
