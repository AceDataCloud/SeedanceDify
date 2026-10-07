# Seedance for Dify

Use the Ace Data Cloud Seedance APIs in Dify workflows. Maintained by Ace Data Cloud. The plugin is free; API calls require your own authorized account and use the current service pricing.

## Setup

1. Activate the service at [Ace Data Cloud](https://platform.acedata.cloud/console/applications), check [current pricing](https://platform.acedata.cloud/models), and create an API token with the required service access.
2. Install from the official Dify Marketplace once the submission is approved and published. During review, use Dify's documented package/debug installation in a test workspace. A GitHub PR does not establish Marketplace availability or default installation.
3. In Dify's **Plugins / Tools** page, authorize this provider with **Bearer Token** (`acedata_bearer_token`). Do not include credentials in prompts or exported workflows. Credential validation never generates media. Authorization performs a read-only task query.

## Tools

| Tool | API |
|---|---|
| `seedance_generate_video` | `POST /seedance/videos` |
| `seedance_task_retrieve` | `POST /seedance/tasks` |
| `seedance_tasks_retrieve_batch` | `POST /seedance/tasks` |

See [CAPABILITIES.md](CAPABILITIES.md) for the current MCP comparison and parameter equivalents. All exposed inputs follow the current published API; model combinations and availability still depend on the service.

## Run a workflow

For generation, use **Start → generation tool → task retrieval → Output**. Fill the prompt/text and model, and enter arrays/objects as JSON. Optional values can be left empty. The example requests in [tests/contract-examples.json](https://github.com/AceDataCloud/SeedanceDify/blob/main/tests/contract-examples.json) show valid shapes; example.org URLs are placeholders that must be replaced with your own accessible media.

A submission can return `status=pending` with `task_id`. Save that ID, then use the retrieval tool with `wait_seconds=0` to read once, or 1–240 for a bounded wait. If still pending, query the same task again. Disable automatic retries on generation nodes. No paid request is automatically retried and no substitute model is selected.

`status`, `success`, `task_id`, `trace_id`, `media_urls`, `data`, and `result` are available as Dify variables. Only a terminal successful result has `success=true`; intermediate previews remain pending. Batch queries preserve the state of each item. Terminal task failures raise a tool error. Synchronous search, text and management results are returned directly in `data`/`result`. The plugin does not execute model-generated tools.

The table maps service operations to Dify tools. Different MCP helper functions may use the same action selector or structured JSON input.

Task/query calls retry transport failures at most twice. Generation has one attempt and a 10-second connect / 60-second read timeout. After a timeout, inspect [request history](https://platform.acedata.cloud/console/usages) before resubmitting; the accepted task may still be running. Delete/archive operations require `confirm=true`.

## Branding and privacy

The plugin uses the exact existing system asset recorded in [branding provenance](https://github.com/AceDataCloud/SeedanceDify/blob/main/tests/branding-source.json), for both light and dark icons. No logo was generated or redrawn. Asset SHA256: `6a5b07c1d33d2910eb9fe1c8549874a004d13a0e75d9b30a7cfdc255c586a83d`.

Requests go directly to `https://api.acedata.cloud`. The plugin passes reference URLs to that API and returns media links; it does not fetch arbitrary reference URLs. Dify may fetch/render output links under its own policies. Never submit media you lack permission to process. See [PRIVACY.md](PRIVACY.md).

API charges are recorded in Credits in your Ace Data Cloud account. Check the actual usage ledger; Dify execution counts are not a billing ledger. USD = Credits × your current package price / amount.

## Development and evidence

Python 3.12 is required. Install `requirements.txt`, then run:

```sh
python -m pytest tests -q
ruff check .
ruff format --check .
dify plugin package .
```

Source contracts, MCP mappings, brand provenance and offline cases are in `tests/`. Recorded real Dify results state their exact coverage; they do not establish all models/options or Dify Cloud/Marketplace installation. See [tests/README.md](https://github.com/AceDataCloud/SeedanceDify/blob/main/tests/README.md).

- Source: https://github.com/AceDataCloud/SeedanceDify
- Issues: https://github.com/AceDataCloud/SeedanceDify/issues
- Contact: dev@acedata.cloud
- License: MIT
- [Simplified Chinese](readme/README_zh_Hans.md)
