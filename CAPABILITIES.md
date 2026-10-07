# Seedance capability mapping

Compared with [MCPs at f0eed10abf31](https://github.com/AceDataCloud/MCPs/tree/f0eed10abf310824cb4c33d4944c63d3654ac95b/seedance) and the public API contract at PlatformBackend `fa94598267a82545fb1afed6ee26bafd6cbb9ca7`.

The table maps service operations to Dify tools. Different MCP helper functions may use the same action selector or structured JSON input.

| MCP function | Dify equivalent | Notes |
|---|---|---|
| `seedance_list_models` |  | Model/action selectors and the API reference; informational guidance does not submit a request. |
| `seedance_list_resolutions` |  | Model/action selectors and the API reference; informational guidance does not submit a request. |
| `seedance_list_actions` |  | Model/action selectors and the API reference; informational guidance does not submit a request. |
| `seedance_get_task` | `seedance_task_retrieve` | Set action=retrieve |
| `seedance_get_tasks_batch` | `seedance_tasks_retrieve_batch` | Set action=retrieve_batch |
| `seedance_generate_video` | `seedance_generate_video` |  |
| `seedance_generate_video_from_image` | `seedance_generate_video` |  |

## Parameter equivalents

- `seedance_get_tasks_batch`: `task_ids` → ids.
- `seedance_generate_video`: `camera_fixed` → camerafixed.

## Verification boundary

Contract examples and regression tests cover request validation, transport and task handling. Actual Dify browser cases are recorded separately in `tests/e2e-results.json` and `tests/e2e-audit.json` when available. A schema test is not a successful paid generation. Unsupported service availability and untested advanced combinations must not be described as passed.
