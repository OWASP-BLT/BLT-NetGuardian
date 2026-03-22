"""Tests for autonomous discovery API handlers (api/discovery/*)."""
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
async def test_handle_discovery_suggest_rejects_non_post():
    worker = BLTWorker(SimpleNamespace(DB=None))

    response = await worker.handle_discovery_suggest(
        FakeRequest("https://api.example.com/api/discovery/suggest", method="GET")
    )
    payload = parse_json(response)

    assert response.status == 405
    assert payload["error"] == "Method not allowed"


@pytest.mark.asyncio
async def test_handle_discovery_suggest_requires_suggestion():
    worker = BLTWorker(SimpleNamespace(DB=None))

    response = await worker.handle_discovery_suggest(
        FakeRequest(
            "https://api.example.com/api/discovery/suggest",
            method="POST",
            payload={"priority": True},
        )
    )
    payload = parse_json(response)

    assert response.status == 400
    assert payload["error"] == "Missing required field: suggestion"


@pytest.mark.asyncio
async def test_handle_discovery_suggest_queues_target_and_job():
    worker = BLTWorker(SimpleNamespace(DB=None))
    worker.discovery = SimpleNamespace(
        process_user_suggestion=AsyncMock(
            return_value={
                "discovery_id": "disc-abc",
                "type": "web2",
            }
        )
    )
    worker.target_registry = SimpleNamespace(save_target=AsyncMock())
    worker.task_queue = SimpleNamespace(save_task=AsyncMock())
    worker.job_store = SimpleNamespace(save_job=AsyncMock())

    response = await worker.handle_discovery_suggest(
        FakeRequest(
            "https://api.example.com/api/discovery/suggest",
            method="POST",
            payload={"suggestion": "https://example.org", "priority": True},
        )
    )
    payload = parse_json(response)

    assert response.status == 200
    assert payload["success"] is True
    assert payload["discovery_id"] == "disc-abc"
    assert "job_id" in payload
    worker.discovery.process_user_suggestion.assert_awaited_once_with(
        "https://example.org", True
    )
    worker.target_registry.save_target.assert_awaited_once()
    worker.task_queue.save_task.assert_awaited_once()
    worker.job_store.save_job.assert_awaited_once()


@pytest.mark.asyncio
async def test_handle_discovery_status_aggregates_stats():
    worker = BLTWorker(SimpleNamespace(DB=None))
    worker.discovery = SimpleNamespace(
        get_discovery_stats=AsyncMock(return_value={"domains": 3}),
        get_current_scanning_target=AsyncMock(
            return_value={"target": "https://scan.example"}
        ),
    )
    worker.task_queue = SimpleNamespace(count_completed_tasks_today=AsyncMock(return_value=7))
    worker.vuln_db = SimpleNamespace(get_stats=AsyncMock(return_value={"total": 12}))

    response = await worker.handle_discovery_status(
        FakeRequest("https://api.example.com/api/discovery/status")
    )
    payload = parse_json(response)

    assert response.status == 200
    assert payload["status"] == "active"
    assert payload["current_target"] == "https://scan.example"
    assert payload["scanned_today"] == 7
    assert payload["vulnerabilities_found"] == 12
    assert payload["stats"] == {"domains": 3}


@pytest.mark.asyncio
async def test_handle_discovery_recent_rejects_invalid_limit():
    worker = BLTWorker(SimpleNamespace(DB=None))

    response = await worker.handle_discovery_recent(
        FakeRequest("https://api.example.com/api/discovery/recent?limit=0")
    )
    payload = parse_json(response)

    assert response.status == 400
    assert payload["error"] == "Invalid limit parameter"


@pytest.mark.asyncio
async def test_handle_discovery_recent_returns_discoveries():
    worker = BLTWorker(SimpleNamespace(DB=None))
    sample = [{"id": "d1", "target": "a.example"}]
    worker.discovery = SimpleNamespace(discover_targets=AsyncMock(return_value=sample))

    response = await worker.handle_discovery_recent(
        FakeRequest("https://api.example.com/api/discovery/recent?limit=5")
    )
    payload = parse_json(response)

    assert response.status == 200
    assert payload["success"] is True
    assert payload["count"] == 1
    assert payload["discoveries"] == sample
    worker.discovery.discover_targets.assert_awaited_once_with(5)
