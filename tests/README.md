# Verification evidence

- `test_plugin.py` and `contract-examples.json`: SDK registration, Dify defaults, request shapes, read-only credential validation, task/batch states, error redaction and no paid retries.
- `branding-source.json`: exact source asset and SHA256.
- `parity-audit.json` / `mcp-parity.json`: current backend/MCP revisions and operation/parameter mapping.
- `e2e-results.json`: previous actual Dify primary-operation results, when available.
- `e2e-audit.json`: second-audit actual Dify workflows, when available.
- `e2e-blocked.json`: service failures, when present; these are not passing cases.

Paid real calls are never run by the unit suite or public CI. A passing schema test is not proof of service availability. Each browser case must include terminal workflow and service status; media outputs require decoding, and new paid calls require usage reconciliation. Marketplace installation is a separate gate after official publication.
