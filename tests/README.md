# Live E2E validation

`e2e-results.json` records real Dify CE workflows, not mocked API calls.
Use `e2e-cases.json` as the tool inputs for an isolated Dify 1.17.1 workspace.

1. Enable the official remote-debug connection in your workspace and run `python -m main` with the workspace debug host/key. Keep signature verification enabled.
2. Authorize this provider with your service API key. Credential validation only queries task metadata.
3. Build Start → this plugin tool → Output. Put form parameters in the tool configuration and prompt/text parameters in tool inputs. Return status, task_id, media_urls and result. Disable generation retries.
4. Run each generation/edit case once, preserving its task ID. Poll via this plugin's task tool until succeeded. Do not regenerate to recover a timeout.
5. Check each output URL, decode the media, and match the task/trace and nonzero deduction in Ace Data Cloud Usage.
6. Remove the test credential and stop the isolated test environment.

These cases consume real API usage. They are never part of CI. Results do not assert Dify Cloud, browser interaction, or Marketplace publication.
