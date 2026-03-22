"""Security policy tests: CORS, API key auth, and target validation on handlers."""
from pathlib import Path
import json
import sys
import types
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

if "workers" not in sys.modules:
    workers_module = types.ModuleType("workers")

    class _FakeResponse:
        def __init__(self, body="", status=200, headers=None):
            self.body = body
            self.status = status
            self.headers = dict(headers or {})

    workers_module.Response = _FakeResponse
    sys.modules["workers"] = workers_module

from worker import BLTWorker  # noqa: E402


class FakeRequest:
    """Request double with optional headers (CORS / auth)."""

    def __init__(self, url, method="GET", payload=None, headers=None):
        self.url = url
        self.method = method
        self._payload = payload
        self.headers = dict(headers or {})

    async def json(self):
        return self._payload or {}


def parse_json(response):
    return json.loads(response.body)


@pytest.mark.asyncio
async def test_handle_request_blocks_disallowed_origin_on_get():
    worker = BLTWorker(
        SimpleNamespace(
            DB=None,
            AUTHENTICATE_READ_ENDPOINTS="false",
            CORS_ALLOWED_ORIGINS="https://trusted.example",
        )
    )
    response = await worker.handle_request(
        FakeRequest(
            "https://api.example.com/api/vulnerabilities",
            headers={"Origin": "https://evil.example"},
        )
    )
    payload = parse_json(response)
    assert response.status == 403
    assert payload["error"] == "Origin not allowed"


@pytest.mark.asyncio
async def test_handle_request_options_preflight_rejects_bad_origin():
    worker = BLTWorker(
        SimpleNamespace(
            DB=None,
            CORS_ALLOWED_ORIGINS="https://trusted.example",
        )
    )
    response = await worker.handle_request(
        FakeRequest(
            "https://api.example.com/api/tasks/queue",
            method="OPTIONS",
            headers={"Origin": "https://evil.example"},
        )
    )
    assert response.status == 403


@pytest.mark.asyncio
async def test_handle_request_post_rejects_missing_api_key_when_configured():
    worker = BLTWorker(
        SimpleNamespace(DB=None, API_SECRET="supersecret", AUTHENTICATE_READ_ENDPOINTS="false")
    )
    response = await worker.handle_request(
        FakeRequest(
            "https://api.example.com/api/tasks/queue",
            method="POST",
            payload={"target_id": "t1", "task_types": ["crawler"], "priority": "medium"},
            headers={"Origin": "https://owasp-blt.github.io"},
        )
    )
    payload = parse_json(response)
    assert response.status == 401
    assert payload["error"] == "Unauthorized"


@pytest.mark.asyncio
async def test_handle_request_post_accepts_x_api_key_when_configured():
    worker = BLTWorker(
        SimpleNamespace(DB=None, API_SECRET="supersecret", AUTHENTICATE_READ_ENDPOINTS="false")
    )
    worker.deduplicator = SimpleNamespace(is_duplicate=AsyncMock(return_value=False))
    worker.task_queue = SimpleNamespace(save_task=AsyncMock())
    worker.job_store = SimpleNamespace(save_job=AsyncMock())
    worker.coordinator = SimpleNamespace(process_job=AsyncMock())

    response = await worker.handle_request(
        FakeRequest(
            "https://api.example.com/api/tasks/queue",
            method="POST",
            payload={"target_id": "t1", "task_types": ["crawler"], "priority": "medium"},
            headers={
                "Origin": "https://owasp-blt.github.io",
                "X-API-Key": "supersecret",
            },
        )
    )
    payload = parse_json(response)
    assert response.status == 200
    assert payload["success"] is True


@pytest.mark.asyncio
async def test_handle_discovery_suggest_rejects_loopback_target():
    worker = BLTWorker(SimpleNamespace(DB=None))
    response = await worker.handle_discovery_suggest(
        FakeRequest(
            "https://api.example.com/api/discovery/suggest",
            method="POST",
            payload={"suggestion": "http://127.0.0.1/admin", "priority": False},
        )
    )
    payload = parse_json(response)
    assert response.status == 400
    assert "127" in payload["error"] or "loopback" in payload["error"].lower()


@pytest.mark.asyncio
async def test_handle_target_registration_rejects_metadata_host():
    worker = BLTWorker(SimpleNamespace(DB=None))
    response = await worker.handle_target_registration(
        FakeRequest(
            "https://api.example.com/api/targets/register",
            method="POST",
            payload={
                "target_type": "web2",
                "target": "http://169.254.169.254/",
                "scan_types": ["crawler"],
            },
        )
    )
    payload = parse_json(response)
    assert response.status == 400
    assert "metadata" in payload["error"].lower()
