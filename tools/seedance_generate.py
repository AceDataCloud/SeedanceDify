from __future__ import annotations

from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from tools.acedata_client import AceDataSeedanceClient


class SeedanceGenerateVideoTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        client = AceDataSeedanceClient(
            bearer_token=self.runtime.credentials.get("acedata_bearer_token", "")
        )
        result = client.execute("generate", tool_parameters)
        yield self.create_json_message(result)
        for field in ["status", "task_id", "media_urls", "result"]:
            yield self.create_variable_message(field, result[field])
        yield self.create_variable_message("success", result["status"] == "succeeded")
        yield self.create_variable_message("trace_id", result["result"].get("trace_id") or "")
        yield self.create_variable_message(
            "data", result["result"].get("data", result["result"].get("content", {}))
        )
        for url in result["media_urls"]:
            yield self.create_link_message(url)
