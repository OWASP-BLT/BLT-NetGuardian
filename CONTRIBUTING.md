# Contributing to BLT-NetGuardian

Thank you for your interest in contributing to BLT-NetGuardian! This document provides guidelines for contributing to the project.

## Code of Conduct

This project follows the OWASP Code of Conduct. Please be respectful and constructive in all interactions.

## How to Contribute

### Reporting Bugs

If you find a bug, please open an issue with:
- Clear description of the bug
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python version, GPG version)
- Relevant logs (sanitized of sensitive information)

### Security Vulnerabilities

**DO NOT** report security vulnerabilities in public issues!

Instead, email: security@owasp-blt.org

Include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

### Feature Requests

We welcome feature suggestions! Please open an issue with:
- Clear description of the feature
- Use case and motivation
- Proposed implementation approach (optional)

### Pull Requests

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Follow existing code style
   - Add tests for new functionality
   - Update documentation
   - Ensure all tests pass

4. **Test your changes**
   ```bash
   python test_secure_reporter.py
   python integration_test.py
   ```

5. **Commit your changes**
   ```bash
   git commit -m "Add feature: description"
   ```

6. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Open a Pull Request**
   - Describe what you changed and why
   - Reference any related issues
   - Include test results

## Development Guidelines

### Code Style

- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Add docstrings to all public functions
- Keep functions focused and small
- Use type hints where appropriate

### Security Guidelines

- **Never commit private keys or passwords**
- Sanitize all error messages
- Validate all inputs
- Use secure defaults
- Document security considerations
- Test security-critical code paths

### Testing

- Write tests for all new functionality
- Maintain test coverage above 80%
- Test both success and error paths
- Use temporary directories for test files
- Clean up test resources

### Documentation

- Update README.md for user-facing changes
- Update SECURITY_ARCHITECTURE.md for security changes
- Add inline comments for complex logic
- Update examples if APIs change

## Project Structure

```
BLT-NetGuardian/
├── secure_reporter.py          # Core encryption module
├── example_company_setup.py    # Company key generation
├── example_bot_report.py       # Bot reporting example
├── example_company_decrypt.py  # Decryption example
├── test_secure_reporter.py     # Unit tests
├── integration_test.py         # Integration tests
├── requirements.txt            # Python dependencies
├── README.md                   # Main documentation
├── SECURITY_ARCHITECTURE.md    # Security design docs
├── QUICKSTART.md              # Quick start guide
└── CONTRIBUTING.md            # This file
```

## Coding Standards

### Error Handling

```python
# Good - Specific error handling
try:
    result = risky_operation()
except FileNotFoundError:
    print("File not found")
    return None
except ValueError as e:
    print(f"Invalid value: {e}")
    return None

# Bad - Catching all exceptions
try:
    result = risky_operation()
except Exception as e:
    print(f"Error: {e}")  # May leak sensitive info
```

### Input Validation

```python
# Good - Validate inputs
def encrypt_report(data: dict, fingerprint: str):
    if not isinstance(data, dict):
        raise TypeError("data must be a dictionary")
    if not fingerprint or not fingerprint.strip():
        raise ValueError("fingerprint cannot be empty")
    # ... proceed with encryption

# Bad - No validation
def encrypt_report(data, fingerprint):
    # Assumes inputs are correct
    return encrypt(data, fingerprint)
```

### Secure by Default

```python
# Good - Secure defaults
def send_email(smtp_server, port=587, use_tls=True):
    # TLS enabled by default
    pass

# Bad - Insecure defaults
def send_email(smtp_server, port=25, use_tls=False):
    # No encryption by default
    pass
```

## Release Process

1. Update version in appropriate files
2. Update CHANGELOG.md
3. Run full test suite
4. Run security checks (CodeQL, dependency scan)
5. Create release tag
6. Update documentation
7. Announce release

## Community

- GitHub Issues: For bugs and features
- GitHub Discussions: For questions and ideas
- Email: security@owasp-blt.org (security only)

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (see LICENSE file).

## Questions?

If you have questions about contributing, please open a GitHub Discussion or contact the maintainers.

Thank you for contributing to BLT-NetGuardian! 🔒
