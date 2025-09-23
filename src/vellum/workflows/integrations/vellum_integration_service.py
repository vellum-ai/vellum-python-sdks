from typing import Any, Dict

from vellum.workflows.errors.types import WorkflowErrorCode
from vellum.workflows.exceptions import NodeException
from vellum.workflows.vellum_client import create_vellum_client


class VellumIntegrationService:
    """Vellum Integration Service for retrieving tool definitions and executing tools.

    This service uses the native Vellum client SDK to interact with Vellum's integration
    endpoints, providing functionality similar to ComposioService but using Vellum's
    own integration infrastructure.
    """

    def __init__(self) -> None:
        """Initialize the VellumIntegrationService with a Vellum client."""
        self._client = create_vellum_client()

    def get_tool_definition(
        self,
        integration: str,
        provider: str,
        tool_name: str,
    ) -> Dict[str, Any]:
        """Retrieve a tool definition from Vellum integrations.

        Args:
            integration: The integration name (e.g., "GITHUB", "SLACK")
            provider: The integration provider name (e.g., "COMPOSIO")
            tool_name: The tool's unique name as specified by the provider

        Returns:
            Dict containing the tool definition with name, description, and parameters

        Raises:
            NodeException: If the tool definition cannot be retrieved
        """
        try:
            response = self._client.integrations.retrieve_integration_tool_definition(
                integration=integration,
                provider=provider,
                tool_name=tool_name,
            )

            # Convert the response to a dict format matching what's expected
            return {
                "name": response.name,
                "description": response.description,
                "parameters": response.parameters,
                "provider": response.provider,
            }
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
            NodeException: If the tool execution fails
        """
        try:
            response = self._client.integrations.execute_integration_tool(
                integration=integration,
                provider=provider,
                tool_name=tool_name,
                arguments=arguments,
            )

            # Return the data from the response
            return response.data
        except Exception as e:
            error_message = f"Failed to execute tool {tool_name}: {str(e)}"
            raise NodeException(
                message=error_message,
                code=WorkflowErrorCode.INVALID_OUTPUTS,
            ) from e
