from typing import Any, Dict, Optional

from vellum.client.core.api_error import ApiError
from vellum.workflows.constants import VellumIntegrationProviderType
from vellum.workflows.errors.types import WorkflowErrorCode
from vellum.workflows.exceptions import NodeException
from vellum.workflows.types.definition import VellumIntegrationToolDetails
from vellum.workflows.vellum_client import Vellum


def _extract_api_error_message(error: ApiError, fallback_message: str) -> str:
    """Extract a user-friendly error message from an ApiError.

    The ApiError.__str__ method returns verbose output including HTTP headers,
    status code, and body. This function extracts just the meaningful error
    message from the body's 'detail' field when available, or uses the body
    directly if it's a string (e.g., plain-text error pages, timeouts, 502/503).

    Args:
        error: The ApiError to extract a message from
        fallback_message: Message to use if no meaningful message can be extracted

    Returns:
        A user-friendly error message
    """
    if isinstance(error.body, dict):
        detail = error.body.get("detail")
        if detail:
            return str(detail)
    elif isinstance(error.body, str) and error.body:
        return error.body
    return fallback_message


class VellumIntegrationService:
    """Vellum Integration Service for retrieving tool definitions and executing tools.

    This service uses the native Vellum client SDK to interact with Vellum's integration
    endpoints, providing functionality similar to ComposioService but using Vellum's
    own integration infrastructure.
    """

    def __init__(self, client: Vellum) -> None:
        """Initialize the VellumIntegrationService with a Vellum client."""
        self._client = client

    def get_tool_definition(
        self,
        integration: str,
        provider: str,
        tool_name: str,
        toolkit_version: Optional[str] = None,
    ) -> VellumIntegrationToolDetails:
        """Retrieve a tool definition from Vellum integrations.

        Args:
            integration: The integration name (e.g., "GITHUB", "SLACK")
            provider: The integration provider name (e.g., "COMPOSIO")
            tool_name: The tool's unique name as specified by the provider
            toolkit_version: The version of the toolkit to use. Pass 'latest' to get the
                latest version, or a specific version string to pin it. If not provided,
                uses the provider's default.

        Returns:
            VellumIntegrationToolDetails containing the tool definition with parameters

        Raises:
            NodeException: If the tool definition cannot be retrieved
        """
        try:
            response = self._client.integrations.retrieve_integration_tool_definition(
                integration_name=integration,
                integration_provider=provider,
                tool_name=tool_name,
                toolkit_version=toolkit_version,
            )

            return VellumIntegrationToolDetails(
                provider=VellumIntegrationProviderType(response.provider),
                integration_name=integration,
                name=response.name,
                description=response.description,
                parameters=response.input_parameters,
                toolkit_version=response.toolkit_version,
            )
        except ApiError as e:
            fallback_message = f"Failed to retrieve tool definition for {tool_name}"
            error_message = _extract_api_error_message(e, fallback_message)
            raise NodeException(
                message=error_message,
                code=WorkflowErrorCode.INVALID_OUTPUTS,
            ) from e
        except Exception as e:
            error_message = f"Failed to retrieve tool definition for {tool_name}: {str(e)}"
            raise NodeException(
                message=error_message,
                code=WorkflowErrorCode.INVALID_OUTPUTS,
            ) from e

    def execute_tool(
        self,
        integration: str,
        provider: str,
        tool_name: str,
        arguments: Dict[str, Any],
        toolkit_version: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Execute a tool through Vellum integrations.

        Args:
            integration: The integration name (e.g., "GITHUB", "SLACK")
            provider: The integration provider name (e.g., "COMPOSIO")
            tool_name: The tool's unique name as specified by the provider
            arguments: Arguments to pass to the tool
            toolkit_version: The version of the toolkit to use. Pass 'latest' to get the
                latest version, or a specific version string to pin it. If not provided,
                uses the provider's default.

        Returns:
            Dict containing the execution result data

        Raises:
            NodeException: If the tool execution fails, including credential errors
                with integration details in raw_data
        """
        try:
            response = self._client.integrations.execute_integration_tool(
                integration_name=integration,
                integration_provider=provider,
                tool_name=tool_name,
                arguments=arguments,
                toolkit_version=toolkit_version,
            )

            # Return the data from the response
            return response.data
        except ApiError as e:
            # Handle structured 403 credential error responses
            if e.status_code == 403 and isinstance(e.body, dict):
                # Check for backend structure with integration as direct field
                integration_from_backend = e.body.get("integration")
                if integration_from_backend:
                    error_message = e.body.get(
                        "message", "You must authenticate with this integration before you can execute this tool."
                    )

                    # Wrap integration in raw_data for frontend consumption
                    raw_data = {"integration": integration_from_backend}

                    raise NodeException(
                        message=error_message,
                        code=WorkflowErrorCode.INTEGRATION_CREDENTIALS_UNAVAILABLE,
                        raw_data=raw_data,
                    ) from e
                else:
                    # Fallback for generic 403 responses
                    raise NodeException(
                        message=e.body.get("detail", "You do not have permission to execute this tool."),
                        code=WorkflowErrorCode.PROVIDER_CREDENTIALS_UNAVAILABLE,
                    ) from e
            elif e.status_code == 500 and isinstance(e.body, dict):
                error_message = e.body.get("detail", f"Internal server error occurred while executing tool {tool_name}")
                raise NodeException(
                    message=error_message,
                    code=WorkflowErrorCode.PROVIDER_ERROR,
                ) from e
            # Generic API error - extract meaningful message from body if available
            fallback_message = f"Failed to execute tool {tool_name}"
            error_message = _extract_api_error_message(e, fallback_message)
            raise NodeException(
                message=error_message,
                code=WorkflowErrorCode.INTERNAL_ERROR,
            ) from e
        except Exception as e:
            # Catch-all for non-API errors
            error_message = f"Failed to execute tool {tool_name}: {str(e)}"
            raise NodeException(
                message=error_message,
                code=WorkflowErrorCode.INVALID_OUTPUTS,
            ) from e
