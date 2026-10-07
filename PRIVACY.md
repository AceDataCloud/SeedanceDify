# Privacy policy — Seedance by Ace Data Cloud

Effective date: 2026-10-07. Maintainer/contact: Ace Data Cloud, dev@acedata.cloud.

This plugin sends your API key in an HTTPS Authorization header to `api.acedata.cloud`. It sends the inputs you choose for the selected Seedance operation, including prompts, text, settings, reference media URLs and identifiers as applicable. Such inputs may contain personal information if you include it. The API receives ordinary connection metadata, including the Dify server's IP address, and usage information required to operate and bill the service.

The plugin's only direct API recipient is Ace Data Cloud. API processing, retention and service providers follow the [Ace Data Cloud privacy policy](https://platform.acedata.cloud/privacy). The plugin passes reference URLs to the API without fetching those references itself. It returns public result fields and output links to Dify. Dify may fetch or render the links under your deployment's policies.

The plugin excludes credentials, private stored request bodies, account/routing metadata and raw service-error details from normalized outputs. It has no database, telemetry or additional persistent storage. Dify handles credential storage, workflow histories and downstream rendering. The plugin does not promise API-side zero retention.

Only submit content and recordings that you are authorized to process. Delete/archive operations exposed by the plugin require an explicit confirmation input. Remove the credential from Dify or revoke it in the Ace Data Cloud console to stop use. Contact dev@acedata.cloud for API data questions and your Dify administrator for local history.
