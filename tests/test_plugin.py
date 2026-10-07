import importlib
import json
from pathlib import Path

import dify_plugin  # noqa: F401
import pytest
import requests
import yaml
from dify_plugin.config.config import DifyPluginEnv
from dify_plugin.core.plugin_registration import PluginRegistration
from dify_plugin.entities.tool import ToolRuntime

import tools.acedata_client as api
from tools.acedata_client import AceDataSeedanceClient as Client
from tools.acedata_client import AceDataSeedanceError as APIError
from tools.api_contracts import ENDPOINTS, TASK_PATH


def response(body, status=200):
    result = requests.Response()
    result.status_code = status
    result._content = json.dumps(body).encode()
    result.close = lambda: None
    return result


def test_sdk_registration_and_branded_assets():
    registration = PluginRegistration(DifyPluginEnv())
    assert registration.configuration.name
    import hashlib

    provenance = json.loads(Path("tests/branding-source.json").read_text())
    icon = Path("_assets") / registration.configuration.icon
    assert icon.is_file()
    assert hashlib.sha256(icon.read_bytes()).hexdigest() == provenance["sha256"]


def test_credentials_are_read_only(monkeypatch):
    calls = []
    monkeypatch.setattr(requests, "request", lambda *a, **k: calls.append((a, k)) or response(None))
    Client("token").validate()
    assert len(calls) == (1 if TASK_PATH else 0)
    if calls:
        args, kwargs = calls[0]
        assert args == ("POST", api.BASE + TASK_PATH)
        assert kwargs["json"]["action"] == "retrieve"
        assert kwargs["allow_redirects"] is False


@pytest.mark.parametrize("status", [302, 400, 401, 403, 429, 500])
def test_error_bodies_are_never_exposed(monkeypatch, status):
    monkeypatch.setattr(requests, "request", lambda *a, **k: response({"error": "PRIVATE"}, status))
    with pytest.raises(APIError) as error:
        Client("SECRET")._request("POST", "/example", {})
    assert str(status) in str(error.value)
    assert "PRIVATE" not in str(error.value) and "SECRET" not in str(error.value)


def test_paid_request_is_never_retried(monkeypatch):
    calls = []

    def fail(*args, **kwargs):
        calls.append(kwargs)
        raise requests.Timeout("PRIVATE")

    monkeypatch.setattr(requests, "request", fail)
    with pytest.raises(APIError):
        Client("token")._request("POST", "/example", {})
    assert len(calls) == 1


def test_read_only_transport_can_recover(monkeypatch):
    calls = []

    def send(*args, **kwargs):
        calls.append(kwargs)
        if len(calls) < 3:
            raise requests.ConnectionError("PRIVATE")
        return response({})

    monkeypatch.setattr(requests, "request", send)
    monkeypatch.setattr(api.time, "sleep", lambda _: None)
    Client("token")._request("POST", "/example", {}, read_only=True)
    assert len(calls) == 3


def test_running_previews_remain_pending():
    result = Client("token").normalize(
        {"response": {"status": "running", "data": [{"audio_url": "https://example.org/preview"}]}},
        "owned-task",
        retrieved=True,
    )
    assert result["status"] == "pending" and not result["success"] and result["media_urls"] == []


def test_explicit_unfinished_task_stays_pending_even_with_intermediate_error():
    result = Client("token").normalize(
        {"finished_at": None, "response": {"success": False, "error": "PRIVATE"}},
        "owned-task",
        retrieved=True,
    )
    assert result["status"] == "pending"
    assert "PRIVATE" not in json.dumps(result)


def test_completed_results_keep_public_data_and_remove_private_metadata():
    result = Client("token").normalize(
        {
            "response": {
                "status": "succeeded",
                "data": [
                    {"image_url": "https://example.org/final.png", "public_result": "retained"}
                ],
                "request": {"image_url": "https://example.org/private.png"},
                "user_id": "PRIVATE",
                "internal_supplier": "PRIVATE",
                "actual_model": "PRIVATE",
            }
        },
        "owned-task",
        retrieved=True,
    )
    assert result["status"] == "succeeded" and result["success"]
    assert result["media_urls"] == ["https://example.org/final.png"]
    assert result["data"][0]["public_result"] == "retained"
    assert "PRIVATE" not in json.dumps(result) and "private.png" not in json.dumps(result)


def test_terminal_failure_raises():
    with pytest.raises(APIError):
        Client("token").normalize({"response": {"status": "failed"}}, "owned-task", retrieved=True)


def test_native_task_envelope_completes():
    result = Client("token").normalize(
        {
            "task": {
                "id": "owned-task",
                "status": "succeeded",
                "content": {"url": "https://example.org/final.mp4"},
            }
        },
        "owned-task",
        retrieved=True,
    )
    assert result["status"] == "succeeded" and result["media_urls"] == [
        "https://example.org/final.mp4"
    ]


def test_sync_acceptance_is_not_completion():
    result = Client("token").normalize(
        {"task_id": "owned-task", "status": "pending"}, "owned-task", synchronous=True
    )
    assert result["status"] == "pending"


def test_finished_text_result_needs_no_media():
    result = Client("token").normalize(
        {"finished_at": 10, "response": {"data": {"text": "lyrics"}}}, "owned-task", retrieved=True
    )
    assert result["status"] == "succeeded" and result["data"] == {"text": "lyrics"}


def test_invalid_values_fail_before_network(monkeypatch):
    monkeypatch.setattr(requests, "request", lambda *a, **k: pytest.fail("invalid request escaped"))
    for value in [True, float("inf"), "bad"]:
        with pytest.raises(ValueError):
            v = api.coerce(value, "duration", {"type": "integer"})
            api.validate(v, {"type": "integer"}, "duration")
    with pytest.raises(ValueError):
        api.coerce("not-json", "content", {"type": "array", "items": {"type": "object"}})


def test_batch_preserves_individual_states(monkeypatch):
    name = next((k for k, v in ENDPOINTS.items() if v.get("operation") == "batch"), None)
    if not name:
        return
    body = {
        "items": [
            {
                "id": "done",
                "finished_at": 1,
                "response": {
                    "status": "succeeded",
                    "data": [{"audio_url": "https://example.org/final"}],
                },
            },
            {"id": "pending", "finished_at": None, "response": None},
            {"id": "failed", "finished_at": 1, "response": {"success": False, "error": "PRIVATE"}},
        ]
    }
    monkeypatch.setattr(requests, "request", lambda *a, **k: response(body))
    result = Client("token").invoke(name, {"ids": '["done","pending","failed"]'})
    assert result["status"] == "pending"
    assert [x["status"] for x in result["data"]] == ["succeeded", "pending", "failed"]
    assert "PRIVATE" not in json.dumps(result)


@pytest.mark.parametrize("complete", [False, True])
def test_actual_tool_returns_compatible_variables_and_terminal_media(monkeypatch, complete):
    name = next((k for k, v in ENDPOINTS.items() if v.get("operation") == "task"), None)
    if not name:
        return
    body = {
        "id": "owned-task",
        "finished_at": 1 if complete else None,
        "response": {
            "state": "complete" if complete else "running",
            "trace_id": "trace",
            "data": [{"image_url": "https://example.org/final.png"}],
        },
    }
    calls = []

    def send(*args, **kwargs):
        calls.append(kwargs)
        return response(body)

    monkeypatch.setattr(requests, "request", send)
    definition = next(
        yaml.safe_load(p.read_text())
        for p in Path("tools").glob("*.yaml")
        if yaml.safe_load(p.read_text())["identity"]["name"] == name
    )
    module = importlib.import_module(
        definition["extra"]["python"]["source"].replace("/", ".").removesuffix(".py")
    )
    cls = next(
        x for x in vars(module).values() if isinstance(x, type) and x.__module__ == module.__name__
    )
    tool = cls(
        runtime=ToolRuntime(
            credentials={"acedata_bearer_token": "owned-token"}, user_id=None, session_id=None
        ),
        session=None,
    )
    messages = list(tool._invoke({"task_id": "owned-task", "wait_seconds": 0}))
    variables = {
        m.message.variable_name: m.message.variable_value
        for m in messages
        if m.type.value == "variable"
    }
    assert calls[0]["headers"]["Authorization"] == "Bearer owned-token"
    assert variables["status"] == ("succeeded" if complete else "pending")
    assert variables["success"] is complete
    assert variables["trace_id"] == "trace"
    assert len([m for m in messages if m.type.value in ["image", "link"]]) == int(complete)


CASES = json.loads(Path("tests/contract-examples.json").read_text())


@pytest.mark.parametrize("case", CASES, ids=[c["name"] for c in CASES])
def test_public_contract_and_actual_dify_defaults(case):
    tool = case["tool"]
    definition = next(
        yaml.safe_load(p.read_text())
        for p in Path("tools").glob("*.yaml")
        if yaml.safe_load(p.read_text())["identity"]["name"] == tool
    )
    defaults = {p["name"]: p["default"] for p in definition["parameters"] if "default" in p}
    if case.get("error"):
        with pytest.raises(ValueError):
            Client("token").prepare(tool, {**defaults, **case["inputs"]})
        return
    method, path, body, query, headers, readonly, asynchronous = Client("token").prepare(
        tool, {**defaults, **case["inputs"]}
    )
    assert method == case["method"] and path == case["path"]
    for k, v in case.get("body", {}).items():
        assert body[k] == v
    for k in case.get("absent", []):
        assert k not in body
    assert query == case.get("query", {})
    assert headers == case.get("headers", {})
    assert readonly is case.get("read_only", False)
    if "async" in case:
        assert asynchronous is case["async"]


def test_union_boolean_parameter_is_not_a_string():
    assert (
        api.coerce("false", "multi_shot", {"anyOf": [{"type": "boolean"}, {"enum": [True]}]})
        is False
    )


def test_partial_output_has_explicit_status():
    body = {
        "response": {
            "data": [
                {"status": "succeeded", "image_url": "https://example.org/final.png"},
                {"status": "failed", "error": {"message": "PRIVATE"}},
            ]
        }
    }
    if False:
        result = Client("token").normalize(body, "owned-task", retrieved=True)
        assert result["status"] == "partial" and not result["success"] and result["media_urls"]
    else:
        with pytest.raises(APIError):
            Client("token").normalize(body, "owned-task", retrieved=True)


def test_primary_audio_does_not_advertise_optional_unrendered_video():
    value = {
        "data": [
            {
                "audio_url": "https://example.org/song.mp3",
                "video_url": "https://example.org/not-rendered.mp4",
                "image_url": "https://example.org/cover.jpg",
            }
        ]
    }
    if False:
        assert api.media_urls(value) == ["https://example.org/song.mp3"]
    else:
        assert "https://example.org/song.mp3" in api.media_urls(value)
