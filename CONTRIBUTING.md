# Contributing to BLT-NetGuardian

Thanks for helping improve OWASP BLT-NetGuardian. This document is a short path from clone to a passing PR.

## Before you start

- Read [`README.md`](README.md) for architecture overview.
- For API details see [`API.md`](API.md); for deployment see [`DEPLOY.md`](DEPLOY.md).

## Local setup

### Python

Use **Python 3.11+** (matches CI).

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Unix: source .venv/bin/activate
pip install -r requirements.txt
```

### Run tests

```bash
python -m pytest -q
```

CI also runs `python -m compileall src tests` — you can run that locally before pushing:

```bash
python -m compileall src tests
```

### Backend (Cloudflare Worker) locally

Install [Wrangler](https://developers.cloudflare.com/workers/wrangler/) and run:

```bash
wrangler dev
```

Point the frontend at your local API by editing `public/assets/js/config.js` (`API_BASE_URL`), as described in [`README.md`](README.md) and [`DEPLOY.md`](DEPLOY.md).

### Frontend only (static)

From the repo root:

```bash
python -m http.server 8000
```

Open `http://localhost:8000/public/` (or the path your server uses). Without a running worker, API calls will fail unless `config.js` targets a deployed Worker.

## Making changes

1. **Fork** the repository and create a branch: `fix/…`, `feat/…`, or `docs/…`.
2. Keep PRs **focused** (one logical change when possible).
3. Add or update **tests** for Python changes under `tests/`.
4. Run **`pytest`** and **`compileall`** before opening the PR.

## Pull requests

- Describe **what** changed and **how you tested** it.
- Link **related issues** with `Fixes #123` when applicable.
- Expect review from maintainers; be responsive to feedback.

## Code style

- Prefer clear names and small functions.
- Match existing patterns in `src/worker.py` and `src/scanners/`.
- Do not add dependencies that are **incompatible with Cloudflare Workers Python** unless explicitly discussed (see comments in `requirements.txt`).

## Questions

- Open a **[GitHub issue](https://github.com/OWASP-BLT/BLT-NetGuardian/issues)** or ask in **OWASP Slack** `#project-blt`.

Thank you for contributing.
