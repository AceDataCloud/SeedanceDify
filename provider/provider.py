from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError

from client import APIError, Client


class Provider(ToolProvider):
    def _validate_credentials(self, credentials: dict) -> None:
        try:
            Client(credentials.get("api_key", "")).validate()
        except (APIError, ValueError):
            raise ToolProviderCredentialValidationError(
                "Unable to validate the API key. Check its service access and network connection."
            ) from None
