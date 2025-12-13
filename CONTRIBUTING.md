# Contributing to BLT-NetGuardian

Thank you for your interest in contributing to BLT-NetGuardian! This document provides guidelines for contributing to the project.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/your-username/BLT-NetGuardian.git`
3. Create a new branch: `git checkout -b feature/your-feature-name`
4. Make your changes
5. Test your changes locally
6. Commit your changes: `git commit -m "Description of changes"`
7. Push to your fork: `git push origin feature/your-feature-name`
8. Open a Pull Request

## Development Setup

### Frontend Development

The frontend is static HTML/CSS/JavaScript. To develop locally:

```bash
# Serve the frontend
python -m http.server 8000
# or
npx serve
```

Navigate to `http://localhost:8000` in your browser.

### Backend Development

The backend is a Cloudflare Python Worker. To develop locally:

```bash
cd worker
wrangler dev
```

This starts a local development server at `http://localhost:8787`.

## Code Style

- Use consistent indentation (2 spaces for JavaScript, HTML, CSS; 4 spaces for Python)
- Follow existing code patterns in the repository
- Follow PEP 8 style guide for Python code
- Add comments for complex logic
- Keep functions small and focused

## Testing

Before submitting a PR:

1. Test the frontend in multiple browsers (Chrome, Firefox, Safari)
2. Test API endpoints with the worker running locally
3. Ensure all existing functionality still works
4. Test on mobile/responsive viewports

## Pull Request Guidelines

- Provide a clear description of the changes
- Reference any related issues
- Include screenshots for UI changes
- Update documentation if needed
- Ensure your code passes any linting/validation

## Reporting Issues

When reporting issues, please include:

- Clear description of the problem
- Steps to reproduce
- Expected behavior
- Actual behavior
- Browser/environment information
- Screenshots if applicable

## Feature Requests

We welcome feature requests! Please:

- Check if the feature has already been requested
- Provide a clear use case
- Explain how it benefits users
- Consider if it aligns with the project goals

## Security

If you discover a security vulnerability, please email security@owasp.org rather than opening a public issue.

## Code of Conduct

This project follows the OWASP Code of Conduct. Be respectful, inclusive, and constructive in all interactions.

## Questions?

Feel free to open an issue with the "question" label if you need help or clarification.

Thank you for contributing to BLT-NetGuardian! 🛡️
