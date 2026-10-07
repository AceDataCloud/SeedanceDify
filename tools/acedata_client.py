"""Seedance API transport and task handling, using the published API contract."""

from __future__ import annotations

import json
import math
import re
import time
from typing import Any
from urllib.parse import quote

import requests
from jsonschema import Draft202012Validator

from tools.api_contracts import ENDPOINTS, TASK_PATH

BASE = "https://api.acedata.cloud"
FAILED = {"failed", "error", "cancelled", "canceled", "rejected"}
COMPLETE = {"complete", "completed", "succeeded", "succeed", "success", "finished"}
SENSITIVE_KEYS = {
    "request",
    "request_body",
    "user_id",
    "actor_user_id",
    "credential_id",
    "authorization_id",
    "application_id",
    "api_key",
    "access_token",
    "refresh_token",
    "authorization",
    "headers",
    "supplier",
    "supplier_id",
    "provider_route",
    "upstream",
    "upstream_model",
    "actual_model",
    "secret",
}
MEDIA_KEYS = {"image_url", "audio_url", "video_url", "file_url", "raw_image_url", "url"}


class AceDataSeedanceError(RuntimeError):
    """A public error which never includes raw service payloads or credentials."""


def clean_result(value: Any) -> Any:
    if isinstance(value, dict):
        result = {}
        for key, item in value.items():
            if key.lower() in SENSITIVE_KEYS or re.search(
                r"(^internal(?:_|$)|supplier|upstream|(?:^|_)secret(?:_|$))", key, re.I
            ):
                continue
            if key == "error" and item:
                result[key] = {
                    "code": item.get("code", "api_error")
                    if isinstance(item, dict)
                    else "api_error",
                    "message": "Operation failed; use the task or trace ID to inspect the request.",
                }
            else:
                result[key] = clean_result(item)
        return result
    if isinstance(value, list):
        return [clean_result(v) for v in value]
    return value


def media_urls(value: Any) -> list[str]:
    result: list[str] = []

    def walk(node: Any) -> None:
        if isinstance(node, dict):
            for key, item in node.items():
                if (
                    key in MEDIA_KEYS
                    and isinstance(item, str)
                    and item.startswith(("https://", "http://"))
                ):
                    result.append(item)
                elif isinstance(item, (dict, list)):
                    walk(item)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(value)
    return list(dict.fromkeys(result))


def parse_json(value: Any, name: str, *, lines: bool = False) -> Any:
    if not isinstance(value, str):
        return value
    value = value.strip()
    try:
        return json.loads(value)
    except ValueError:
        if lines:
            return [x.strip() for x in value.splitlines() if x.strip()]
        raise ValueError(f"{name} must contain valid JSON.") from None


def coerce(value: Any, name: str, schema: dict[str, Any]) -> Any:
    typ = schema.get("type")
    options = schema.get("oneOf", schema.get("anyOf", []))
    types = {s.get("type") for s in options if isinstance(s.get("type"), str)}
    if isinstance(typ, list):
        types.update(typ)
    if isinstance(typ, str) and typ in {"array", "object"}:
        value = parse_json(
            value, name, lines=typ == "array" and schema.get("items", {}).get("type") == "string"
        )
    elif (
        isinstance(value, str)
        and value.strip().startswith(("[", "{"))
        and types.intersection({"array", "object"})
    ):
        value = parse_json(value, name)
    if isinstance(typ, str) and typ in {"number", "integer"} and not isinstance(value, bool):
        if isinstance(value, str):
            try:
                value = float(value)
            except ValueError:
                raise ValueError(f"{name} must be a number.") from None
        if isinstance(value, (int, float)) and not math.isfinite(value):
            raise ValueError(f"{name} must be finite.")
        if typ == "integer" and isinstance(value, (int, float)) and value == int(value):
            value = int(value)
    if (
        isinstance(value, str)
        and types.intersection({"integer", "number"})
        and value.lstrip("-+").replace(".", "", 1).isdigit()
    ):
        number = float(value)
        value = int(number) if number.is_integer() else number
    if (
        (typ == "boolean" or types == {"boolean"})
        and isinstance(value, str)
        and value.lower() in {"true", "false"}
    ):
        value = value.lower() == "true"
    return value


def validate(value: Any, schema: dict[str, Any], context: str) -> None:
    errors = list(Draft202012Validator(schema).iter_errors(value))
    if errors:
        first = errors[0]
        location = ".".join(str(x) for x in first.absolute_path) or context
        raise ValueError(
            f"Invalid {location}: does not meet the API's {first.validator} constraint."
        )


def allows_property(schema: dict[str, Any], name: str, values: dict[str, Any]) -> bool:
    if name in schema.get("properties", {}):
        return True
    for group in ["oneOf", "anyOf", "allOf"]:
        for branch in schema.get(group, []):
            discriminators = {
                k: v
                for k, v in branch.get("properties", {}).items()
                if k in {"action", "mode"} and (v.get("enum") or "const" in v)
            }
            matches = all(
                k not in values or values[k] in v.get("enum", [v.get("const")])
                for k, v in discriminators.items()
            )
            if matches and allows_property(branch, name, values):
                return True
    return False


class AceDataSeedanceClient:
    def __init__(self, bearer_token: str) -> None:
        if not isinstance(bearer_token, str) or not bearer_token.strip():
            raise ValueError("An Ace Data Cloud token is required.")
        token = bearer_token.strip()
        self._token = token[7:].strip() if token.lower().startswith("bearer ") else token
        if not self._token:
            raise ValueError("An Ace Data Cloud token is required.")

    def _request(
        self,
        method: str,
        path: str,
        payload: dict[str, Any] | None = None,
        query: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        *,
        read_only: bool = False,
        validation: bool = False,
    ) -> dict[str, Any] | list[Any]:
        attempts = 3 if read_only else 1
        for attempt in range(attempts):
            try:
                with requests.request(
                    method,
                    BASE + path,
                    json=payload,
                    params=query,
                    headers={
                        "Authorization": "Bearer " + self._token,
                        "Accept": "application/json",
                        **(headers or {}),
                    },
                    timeout=(10, 60),
                    allow_redirects=False,
                ) as response:
                    if not 200 <= response.status_code < 300:
                        raise AceDataSeedanceError(
                            f"Ace Data Cloud HTTP {response.status_code}. Check service access and request history before submitting again."
                        )
                    if response.status_code == 204:
                        return {}
                    body = response.json()
                    trace = response.headers.get("x-trace-id")
                    if isinstance(body, dict) and trace and not body.get("trace_id"):
                        body["trace_id"] = trace
                break
            except requests.RequestException as exc:
                if attempt + 1 < attempts:
                    time.sleep(0.5 * (attempt + 1))
                    continue
                raise AceDataSeedanceError(
                    f"Connection failed ({type(exc).__name__}). Preserve any accepted task ID and inspect request history before resubmitting."
                ) from None
            except ValueError:
                raise AceDataSeedanceError("The service returned invalid JSON.") from None
        if body is None and (validation or path == TASK_PATH):
            return {}
        if not isinstance(body, (dict, list)):
            raise AceDataSeedanceError("The service returned an invalid result.")
        if (
            not validation
            and isinstance(body, dict)
            and (body.get("success") is False or body.get("error"))
        ):
            raise AceDataSeedanceError(
                "The service reported an error. Inspect the request using its task or trace ID."
            )
        return body

    def validate(self) -> None:
        if TASK_PATH:
            self._request(
                "POST",
                TASK_PATH,
                {"action": "retrieve", "id": "00000000-0000-0000-0000-000000000000"},
                read_only=True,
                validation=True,
            )

    def prepare(
        self, tool: str, parameters: dict[str, Any]
    ) -> tuple[str, str, dict[str, Any], dict[str, Any], dict[str, str], bool, bool]:
        endpoint = ENDPOINTS[tool]
        params = {k: v for k, v in parameters.items() if v is not None}
        if endpoint.get("selector"):
            choice = params.get("action", endpoint["selector_default"])
            if choice not in endpoint["selector"]:
                raise ValueError("Unsupported operation.")
            endpoint = ENDPOINTS[endpoint["selector"][choice]]
        params = adapt_parameters(tool, params, endpoint)
        values = {**endpoint.get("defaults", {}), **params, **endpoint.get("fixed", {})}
        properties = endpoint["properties"]
        body: dict[str, Any] = {}
        for name, schema in properties.items():
            if name in values and values[name] != "":
                body[name] = coerce(values[name], name, schema)
            elif name in values and name in endpoint.get("allow_empty", []):
                body[name] = values[name]
        query_action = values.get("action") in endpoint.get("query_actions", [])
        if (
            not query_action
            and "async" in properties
            and allows_property(endpoint["schema"], "async", values)
        ):
            body["async"] = True
        if "stream" in properties and allows_property(endpoint["schema"], "stream", values):
            body["stream"] = False
        if "response_format" in properties and endpoint.get("media_response"):
            body["response_format"] = "url"
        path = endpoint["path"]
        query: dict[str, Any] = {}
        request_headers: dict[str, str] = {}
        for parameter in endpoint.get("parameters", []):
            name = parameter["name"]
            input_name = "idempotency_key" if name.lower() == "idempotency-key" else name
            if input_name not in values or values[input_name] == "":
                if parameter.get("required"):
                    raise ValueError(f"{input_name} is required.")
                continue
            value = coerce(values[input_name], input_name, parameter.get("schema", {}))
            validate(value, parameter.get("schema", {}), input_name)
            if parameter["in"] == "path":
                path = path.replace("{" + name + "}", quote(str(value), safe=""))
            elif parameter["in"] == "query":
                query[name] = value
            elif parameter["in"] == "header":
                request_headers[name] = str(value)
        body = finalize_payload(tool, body, values, endpoint)
        validate(body, endpoint["schema"], "parameters")
        action = body.get("action")
        if endpoint.get("destructive") or action in {"delete", "archive"}:
            if params.get("confirm") is not True:
                raise ValueError(
                    "Set confirm to true to perform this deletion or archive operation."
                )
        read_only = (
            endpoint["method"] == "GET"
            or endpoint.get("read_only", False)
            or (endpoint.get("query_actions") and action in endpoint["query_actions"])
        )
        asynchronous = endpoint.get("asynchronous", False) or body.get("async") is True
        return (
            endpoint["method"],
            path,
            body,
            query,
            request_headers,
            bool(read_only),
            bool(asynchronous),
        )

    def invoke(self, tool: str, parameters: dict[str, Any]) -> dict[str, Any]:
        endpoint = ENDPOINTS[tool]
        if endpoint.get("operation") == "task":
            task_id = parameters.get("task_id") or parameters.get("id")
            trace_id = parameters.get("trace_id") if "trace_id" in endpoint["properties"] else None
            if not (isinstance(task_id, str) and task_id.strip()) and not (
                isinstance(trace_id, str) and trace_id.strip()
            ):
                raise ValueError("A task ID or supported trace ID is required.")
            lookup = {"action": "retrieve"}
            if task_id:
                lookup["id"] = task_id
            if trace_id:
                lookup["trace_id"] = trace_id
            wait = coerce(parameters.get("wait_seconds", 0), "wait_seconds", {"type": "integer"})
            validate(wait, {"type": "integer", "minimum": 0, "maximum": 240}, "wait_seconds")
            deadline = time.monotonic() + wait
            while True:
                body = self._request("POST", TASK_PATH, lookup, read_only=True)
                resolved_id = str(
                    task_id or (body.get("id") if isinstance(body, dict) else "") or ""
                )
                result = self.normalize(body, resolved_id, retrieved=True)
                if result["status"] != "pending" or time.monotonic() >= deadline:
                    return result
                time.sleep(min(5, max(0, deadline - time.monotonic())))
        method, path, body, query, headers, read_only, asynchronous = self.prepare(tool, parameters)
        result = self._request(
            method,
            path,
            body if method not in {"GET", "DELETE"} else None,
            query,
            headers,
            read_only=read_only,
        )
        if endpoint.get("operation") == "batch":
            items = (
                result
                if isinstance(result, list)
                else result.get("items", result.get("tasks", result.get("data", [])))
            )
            if not isinstance(items, list):
                items = []
            normalized = []
            for item in items:
                if not isinstance(item, dict):
                    continue
                try:
                    normalized.append(
                        self.normalize(
                            item, str(item.get("id") or item.get("task_id") or ""), retrieved=True
                        )
                    )
                except AceDataSeedanceError:
                    normalized.append(
                        {
                            "status": "failed",
                            "success": False,
                            "task_id": str(item.get("id") or item.get("task_id") or ""),
                            "trace_id": "",
                            "media_urls": [],
                            "data": {},
                            "result": {},
                        }
                    )
            status = (
                "pending"
                if any(x["status"] == "pending" for x in normalized)
                else "failed"
                if any(x["status"] == "failed" for x in normalized)
                else "succeeded"
            )
            return {
                "status": status,
                "success": status == "succeeded",
                "task_id": "",
                "trace_id": "",
                "media_urls": [u for x in normalized for u in x["media_urls"]],
                "data": normalized,
                "result": {"items": normalized},
            }
        task_id = (
            str(
                result.get("task_id")
                or (
                    result.get("task", {}).get("id") if isinstance(result.get("task"), dict) else ""
                )
                or ""
            )
            if isinstance(result, dict)
            else ""
        )
        return self.normalize(result, task_id, synchronous=not asynchronous)

    def normalize(
        self,
        body: dict[str, Any] | list[Any],
        task_id: str,
        *,
        retrieved: bool = False,
        synchronous: bool = False,
    ) -> dict[str, Any]:
        pending = {
            "status": "pending",
            "success": False,
            "task_id": task_id,
            "trace_id": "",
            "media_urls": [],
            "data": {},
            "result": {},
        }
        unfinished = (
            retrieved
            and isinstance(body, dict)
            and "finished_at" in body
            and body["finished_at"] is None
        )
        if retrieved and isinstance(body, dict) and "response" in body:
            result = body.get("response")
        else:
            result = body
        if isinstance(result, str):
            try:
                result = json.loads(result)
            except ValueError:
                result = {}
        if result is None or result == {} and retrieved:
            return pending
        states = []
        errors = []

        def visit(node: Any) -> None:
            if isinstance(node, dict):
                if node.get("success") is False or node.get("error"):
                    errors.append(True)
                for key, value in node.items():
                    if key in {"state", "status"} and isinstance(value, str):
                        states.append(value.lower())
                    elif key in {"data", "content", "task"}:
                        visit(value)
            elif isinstance(node, list):
                for item in node:
                    visit(item)

        if not (synchronous and not task_id):
            visit(result)
        urls = media_urls(clean_result(result))
        failures = errors or any(s in FAILED for s in states)
        if failures and not unfinished and not (urls and False):
            raise AceDataSeedanceError(
                "Task failed. Use its task or trace ID to inspect the service request."
            )
        done = (
            (synchronous and not task_id)
            or (bool(states) and all(s in COMPLETE for s in states))
            or (bool(urls) and not states)
        )
        if failures and urls and False:
            done = all(s in COMPLETE | FAILED for s in states)
        if (
            retrieved
            and isinstance(body, dict)
            and body.get("finished_at")
            and not states
            and result
        ):
            done = True
        if unfinished:
            done = False
        if not done and not task_id:
            raise AceDataSeedanceError(
                "No task ID or completed result was returned. Check request history before submitting again."
            )
        status = "partial" if done and failures else "succeeded" if done else "pending"
        data = (
            result.get("data", result.get("content", result))
            if isinstance(result, dict)
            else result
        )
        trace = (
            str(
                result.get("trace_id")
                or (body.get("trace_id") if isinstance(body, dict) else "")
                or ""
            )
            if isinstance(result, dict)
            else ""
        )
        return {
            "status": status,
            "success": status == "succeeded",
            "task_id": task_id,
            "trace_id": trace,
            "media_urls": urls if done else [],
            "data": clean_result(data),
            "result": clean_result(result if isinstance(result, dict) else {"items": result}),
        }


def adapt_parameters(tool: str, params: dict[str, Any], endpoint: dict[str, Any]) -> dict[str, Any]:
    if not endpoint["path"].endswith("/videos"):
        return params
    if "camera_fixed" in params:
        params["camerafixed"] = params.pop("camera_fixed")
    if "image_url" in params and "first_frame_url" not in params:
        params["first_frame_url"] = params.pop("image_url")
    helpers = [
        "prompt",
        "first_frame_url",
        "last_frame_url",
        "reference_image_urls",
        "reference_audio_urls",
        "reference_video_urls",
    ]
    if params.get("content"):
        if any(params.get(k) for k in helpers):
            raise ValueError("Use content JSON or the prompt/reference shortcuts, not both.")
    else:
        content = []
        if params.get("prompt"):
            content.append({"type": "text", "text": params["prompt"]})
        for name, role in [("first_frame_url", "first_frame"), ("last_frame_url", "last_frame")]:
            if params.get(name):
                content.append(
                    {"type": "image_url", "role": role, "image_url": {"url": params[name]}}
                )
        for name, typ, role in [
            ("reference_image_urls", "image_url", "reference_image"),
            ("reference_audio_urls", "audio_url", "reference_audio"),
            ("reference_video_urls", "video_url", "reference_video"),
        ]:
            if params.get(name):
                urls = parse_json(params[name], name, lines=True)
                if not isinstance(urls, list):
                    raise ValueError(name + " must be an array.")
                content.extend({"type": typ, "role": role, typ: {"url": url}} for url in urls)
        if not content:
            raise ValueError("A prompt or reference content is required.")
        params["content"] = content
    if params.get("frames") is not None and params.get("duration") is not None:
        raise ValueError("Use frames or duration, not both.")
    return params


def finalize_payload(
    tool: str, body: dict[str, Any], values: dict[str, Any], endpoint: dict[str, Any]
) -> dict[str, Any]:
    if endpoint["path"].endswith("/videos") and body.get("frames") is not None:
        body.pop("duration", None)
    return body
