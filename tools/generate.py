from dify_plugin import Tool

from client import Client


class MediaTool(Tool):
    def _invoke(self, tool_parameters: dict):
        result = Client(self.runtime.credentials.get("api_key", "")).execute(
            "generate", tool_parameters
        )
        yield self.create_json_message(result)
        for field in ["status", "task_id", "media_urls", "result"]:
            yield self.create_variable_message(field, result[field])
        for url in result["media_urls"]:
            yield self.create_link_message(url)
