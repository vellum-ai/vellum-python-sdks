from typing import Any, Dict

from vellum.client.core.api_error import ApiError
from vellum.workflows.constants import VellumIntegrationProviderType
from vellum.workflows.errors.types import WorkflowErrorCode
from vellum.workflows.exceptions import NodeException
from vellum.workflows.types.definition import VellumIntegrationToolDetails
from vellum.workflows.vellum_client import Vellum


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
    ) -> VellumIntegrationToolDetails:
        """Retrieve a tool definition from Vellum integrations.

        Args:
            integration: The integration name (e.g., "GITHUB", "SLACK")
            provider: The integration provider name (e.g., "COMPOSIO")
            tool_name: The tool's unique name as specified by the provider

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
            )

            return VellumIntegrationToolDetails(
                provider=VellumIntegrationProviderType(response.provider),
                integration_name=integration,
                name=response.name,
                description=response.description,
                parameters=response.input_parameters,
            )
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
    ) -> Dict[str, Any]:
        """Execute a tool through Vellum integrations.

        Args:
            integration: The integration name (e.g., "GITHUB", "SLACK")
            provider: The integration provider name (e.g., "COMPOSIO")
            tool_name: The tool's unique name as specified by the provider
            arguments: Arguments to pass to the tool

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
            # Generic server error
            raise NodeException(
                message=f"Failed to execute tool {tool_name}: {str(e)}",
                code=WorkflowErrorCode.INTERNAL_ERROR,
            ) from e
        except Exception as e:
            # Catch-all for non-API errors
            error_message = f"Failed to execute tool {tool_name}: {str(e)}"
            raise NodeException(
                message=error_message,
                code=WorkflowErrorCode.INVALID_OUTPUTS,
            ) from e
