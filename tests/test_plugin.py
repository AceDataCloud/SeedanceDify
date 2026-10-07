import json
from pathlib import Path

import dify_plugin  # noqa: F401
import pytest
import requests
from dify_plugin.config.config import DifyPluginEnv
from dify_plugin.core.plugin_registration import PluginRegistration

from tools.acedata_client import BASE, SERVICE, https_urls
from tools.acedata_client import AceDataSeedanceClient as Client
from tools.acedata_client import AceDataSeedanceError as APIError


def response(body, status=200):
    r = requests.Response()
    r.status_code = status
    r._content = json.dumps(body).encode()
    r.close = lambda: None
    return r


def test_plugin_loads_all_declared_tools():
    registration = PluginRegistration(DifyPluginEnv())
    assert registration.configuration.name
    assert Path("_assets/" + registration.configuration.icon).is_file()


def test_credential_validation_is_read_only(monkeypatch):
    calls = []

    def request(method, url, **kwargs):
        calls.append((method, url, kwargs))
        return response({})

    monkeypatch.setattr(requests, "request", request)
    Client("sample").validate()
    method, url, kwargs = calls[0]
    assert method == "POST" and url == BASE + SERVICE["prefix"] + "/tasks"
    assert kwargs["json"]["action"] == "retrieve"
    assert kwargs["allow_redirects"] is False


@pytest.mark.parametrize("status", [400, 401, 403, 429, 500])
def test_api_errors_redact_bodies(monkeypatch, status):
    monkeypatch.setattr(
        requests, "request", lambda *a, **k: response({"error": "private-user-data"}, status)
    )
    with pytest.raises(APIError) as exc:
        Client("secret").validate()
    assert str(status) in str(exc.value)
    assert "private-user-data" not in str(exc.value)
    assert "secret" not in str(exc.value)


def test_network_failure_does_not_retry_submission(monkeypatch):
    calls = []

    def fail(*a, **kw):
        calls.append(1)
        raise requests.Timeout("private-user-data")

    monkeypatch.setattr(requests, "request", fail)
    with pytest.raises(APIError) as exc:
        Client("sample").request("POST", SERVICE["prefix"] + "/tasks", {})
    assert len(calls) == 1 and "private-user-data" not in str(exc.value)


def test_task_strips_request_and_identity(monkeypatch):
    key = {"image": "image_url", "video": "video_url", "audio": "audio_url"}[SERVICE["media"]]
    body = {
        "id": "task",
        "finished_at": 10,
        "user_id": "private",
        "request": {"prompt": "private"},
        "response": {
            "success": True,
            "state": "complete",
            "data": [{key: "https://cdn.example.org/result", "internal": "private"}],
        },
    }
    monkeypatch.setattr(requests, "request", lambda *a, **k: response(body))
    result = Client("sample").execute("task", {"task_id": "task", "wait_seconds": 0})
    assert result["status"] == "succeeded"
    assert result["media_urls"] == ["https://cdn.example.org/result"]
    assert "private" not in json.dumps(result)


def test_pending_media_is_not_reported_complete(monkeypatch):
    key = {"image": "image_url", "video": "video_url", "audio": "audio_url"}[SERVICE["media"]]
    body = {
        "id": "task",
        "response": {
            "success": True,
            "state": "pending",
            "data": [{key: "https://cdn.example.org/preview"}],
        },
    }
    monkeypatch.setattr(requests, "request", lambda *a, **k: response(body))
    result = Client("sample").execute("task", {"task_id": "task", "wait_seconds": 0})
    assert result["status"] == "pending" and result["media_urls"] == []


def test_failed_task_is_not_reported_as_success(monkeypatch):
    monkeypatch.setattr(
        requests,
        "request",
        lambda *a, **k: response({"response": {"success": False, "error": "private"}}),
    )
    with pytest.raises(APIError):
        Client("sample").execute("task", {"task_id": "task", "wait_seconds": 0})


def test_input_validation_before_network(monkeypatch):
    monkeypatch.setattr(
        requests, "request", lambda *a, **k: pytest.fail("invalid input made a request")
    )
    with pytest.raises(ValueError):
        Client("sample").execute("generate", {})
    with pytest.raises(ValueError):
        https_urls(["http://example.org/private"])


def test_service_specific_payload():
    p = {"prompt": "test", "text": "test", "model": SERVICE["default"]}
    data, path, header = Client("sample").payload("generate", p)
    assert data["async"] is True
    assert path.startswith(SERVICE["prefix"] + "/")
    if SERVICE["family"] == "fish":
        assert header == SERVICE["default"] and "model" not in data
    else:
        assert data["model"] == SERVICE["default"]
    if SERVICE["family"] == "seedance":
        assert data["content"] == [{"type": "text", "text": "test"}]
    if SERVICE["family"] in {"nano", "gpt"}:
        with pytest.raises(ValueError):
            Client("sample").payload("edit", p)
        data, _, _ = Client("sample").payload(
            "edit", {**p, "image_urls": "https://example.org/input.png"}
        )
        assert data.get("image_urls", data.get("image")) == ["https://example.org/input.png"]


@pytest.mark.parametrize("complete", [False, True])
def test_task_tool_uses_legacy_credentials_and_output_messages(monkeypatch, complete):
    from dify_plugin.entities.tool import ToolRuntime

    from tools.seedance_task_retrieve import SeedanceTaskRetrieveTool

    key = {"image": "image_url", "video": "video_url", "audio": "audio_url"}[SERVICE["media"]]
    url = "https://cdn.example.org/output"
    body = {
        "id": "existing-task",
        "finished_at": 10 if complete else None,
        "response": {
            "success": True,
            "state": "complete" if complete else "pending",
            "trace_id": "test-trace",
            "data": [{key: url}],
        },
    }
    calls = []

    def request(method, endpoint, **kwargs):
        calls.append((method, endpoint, kwargs))
        return response(body)

    monkeypatch.setattr(requests, "request", request)
    tool = SeedanceTaskRetrieveTool(
        runtime=ToolRuntime(
            credentials={"acedata_bearer_token": "owned-test-token"}, user_id=None, session_id=None
        ),
        session=None,
    )
    messages = list(tool._invoke({"task_id": "existing-task", "wait_seconds": 0}))
    variables = {
        m.message.variable_name: m.message.variable_value
        for m in messages
        if m.type.value == "variable"
    }
    assert len(calls) == 1
    assert calls[0][2]["headers"]["Authorization"] == "Bearer owned-test-token"
    assert calls[0][2]["json"] == {"action": "retrieve", "id": "existing-task"}
    assert variables["success"] is complete
    assert variables["status"] == ("succeeded" if complete else "pending")
    assert variables["trace_id"] == "test-trace"
    assert variables["data"] == [{key: url}]
    media_type = "image" if SERVICE["media"] == "image" else "link"
    assert len([m for m in messages if m.type.value == media_type]) == int(complete)
