from __future__ import annotations

from typing import Any, Dict, Optional, Union

from vellum import Vellum
from vellum.client.core.api_error import ApiError
from vellum.workflows.constants import VellumIntegrationProviderType
from vellum.workflows.errors.types import WorkflowErrorCode
from vellum.workflows.exceptions import NodeException
from vellum.workflows.vellum_client import create_vellum_client


class VellumIntegrationService:
    """Vellum API client for fetching integration tool metadata and executing tools."""

    def __init__(self, vellum_client: Optional[Vellum] = None):
        self._client = vellum_client or create_vellum_client()

    @staticmethod
    def _normalize_provider(provider: Union[str, VellumIntegrationProviderType]) -> str:
        return provider.value if isinstance(provider, VellumIntegrationProviderType) else provider

    def _handle_api_error(self, error: ApiError) -> None:
        if error.status_code == 401:
            raise NodeException(
                message="Failed to authorize Vellum integration request. Ensure your VELLUM_API_KEY is configured.",
                code=WorkflowErrorCode.PROVIDER_CREDENTIALS_UNAVAILABLE,
            ) from error

        raise NodeException(
            message=(
                "Vellum integration API request failed with status "
                f"{error.status_code if error.status_code is not None else 'unknown'}: {error.body}"
            )
        ) from error

    def retrieve_integration_tool_definition(
        self,
        *,
        provider: Union[str, VellumIntegrationProviderType],
        integration: str,
        name: str,
    ) -> Dict[str, Any]:
        try:
            return self._client.integrations.retrieve_integration_tool_definition(
                provider=self._normalize_provider(provider),
                integration=integration,
                tool_name=name,
            )
        except ApiError as error:
            self._handle_api_error(error)
        except Exception as error:  # pragma: no cover - defensive catch-all
            raise NodeException(f"Unexpected error calling Vellum integration API: {error}") from error

    def execute_integration_tool(
        self,
        *,
        provider: Union[str, VellumIntegrationProviderType],
        integration: str,
        name: str,
        arguments: Dict[str, Any],
    ) -> Any:
        try:
            response = self._client.integrations.execute_integration_tool(
                provider=self._normalize_provider(provider),
                integration=integration,
                tool_name=name,
                arguments=arguments,
            )
        except ApiError as error:
            self._handle_api_error(error)
        except Exception as error:  # pragma: no cover - defensive catch-all
            raise NodeException(f"Unexpected error calling Vellum integration API: {error}") from error

        if not response.get("successful", True):
            return response.get("error", "Tool execution failed")
        return response.get("data", response)
