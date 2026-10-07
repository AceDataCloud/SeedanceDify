# Seedance by Ace Data Cloud

Generate Seedance text-to-video or first-frame image-to-video with Ace Data Cloud. Maintained by Ace Data Cloud. This is a free Dify tool plugin; API use requires your own Ace Data Cloud account and may incur usage charges.

## Setup

1. Sign in at [Ace Data Cloud](https://platform.acedata.cloud/console/applications), activate the service and check [current pricing](https://platform.acedata.cloud/models).
2. Create an API key authorized for this service. A service key is scoped; use a global key only for services your account can access.
3. Install this plugin from Dify Marketplace **after it is published**. During review, source/package tests do not imply official listing. A development package can use Dify's documented remote-debug workflow in an isolated workspace.
4. In Dify **Integrations → Tools** (or **Plugins** in older versions), authorize the plugin with the key. Credential validation makes only a read-only task query; it never generates media.

## Workflow

1. Create **Start → Generate → Output** and select this plugin's generation tool. Fill the required prompt/text, model and options. Disable automatic retries for generation.
2. Save `task_id` from the result. Status `pending` means accepted, not finished.
3. Pass the same ID to **Retrieve or wait for task**. Set **Wait up to seconds** to 120–240 for a bounded wait, or 0 for one read. If it still returns `pending`, wait and query the same ID again. Do not resubmit generation.
4. When `status` is `succeeded`, read `media_urls` for the image/audio/video links. Use **Output** (or Chatflow **Answer**) to return the URLs. Task failures raise a Dify tool error, rather than returning a false success.

Omit the first-frame image URL for text-to-video. Use a public HTTPS first-frame URL for image-to-video. Mini/Fast 2.0 models support up to 720p. This release does not advertise video edit/extend or multimodal reference modes.

This release covers text-to-video and first-frame image-to-video. Task queries return output fields only, excluding stored requests, account IDs and routing metadata. Generation uses asynchronous requests. Each HTTPS request has a 10-second connect and 60-second read timeout; a wait call polls for at most 240 seconds. No automatic paid retries or model fallback is implemented. On a submission timeout, check request history before attempting another submission.

## Billing, network and privacy

The plugin connects only to `api.acedata.cloud:443`; it does not download reference URLs or media itself. URLs are passed to the API as inputs or returned for downstream use. Only submit content you are authorized to process.

Check [Usage](https://platform.acedata.cloud/console/usages) by key and time after a real call. Charges are in Credits; USD = Credits × your current package price / amount. Dify tool execution counts are not the billing ledger. A completed task must also have usable media. See [PRIVACY.md](PRIVACY.md).

Python 3.12 and `dify-plugin==0.9.1` are required. Default models and listed options may change with the service; check the catalog before using a different model. Contact support for access errors; reduce concurrency on HTTP 429. Do not put keys into prompts or exported workflows.

## Source and support

- Source repository: https://github.com/AceDataCloud/SeedanceDify
- Contact: dev@acedata.cloud
- Issues: https://github.com/AceDataCloud/SeedanceDify/issues
- [Simplified Chinese](readme/README_zh_Hans.md)
- License: MIT

Development: install `requirements.txt`, run `python -m pytest tests -q`, `ruff check .`, and `dify plugin package .`. Test results and limits are recorded in the submission PR; Marketplace publication is separate from local validation.
