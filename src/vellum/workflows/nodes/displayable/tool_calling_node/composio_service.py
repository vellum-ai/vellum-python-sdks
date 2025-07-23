from dataclasses import dataclass
import logging
from typing import Any, Dict, List, Optional

from composio import Action, Composio
from composio_client import Composio as ComposioClient

from vellum.workflows.types.definition import ComposioToolDefinition

logger = logging.getLogger(__name__)


@dataclass
class ConnectionInfo:
    """Information about a user's authorized connection"""

    connection_id: str
    integration_name: str
    created_at: str
    updated_at: str
    status: str = "ACTIVE"  # TODO: Use enum if we end up supporting integrations that the user has not yet connected to


class ComposioAccountService:
    """Manages user authorized connections using composio-client"""

    def __init__(self, api_key: str):
        self.client = ComposioClient(api_key=api_key)

    def get_user_connections(self) -> List[ConnectionInfo]:
        """Get all authorized connections for the user"""
        response = self.client.connected_accounts.list()

        return [
            ConnectionInfo(
                connection_id=item.id,
                integration_name=item.toolkit.slug,
                status=item.status,
                created_at=item.created_at,
                updated_at=item.updated_at,
            )
            for item in response.items
        ]


class ComposioCoreService:
    """Handles tool execution and tool definition retrieval using composio-core"""

    def __init__(self, api_key: str):
        self.client = Composio(api_key=api_key)

    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Execute a tool using composio-core

        Args:
            tool_name: The name of the tool to execute (e.g., "HACKERNEWS_GET_USER")
            arguments: Dictionary of arguments to pass to the tool

        Returns:
            The result of the tool execution
        """
        # Convert tool name string to Action enum
        action = getattr(Action, tool_name)
        return self.client.actions.execute(action, params=arguments)

    def get_tool_definition(self, tool_name: str) -> Optional[ComposioToolDefinition]:
        """Fetch tool definition from Composio API

        Args:
            tool_name: The name of the tool to get definition for (e.g., "GITHUB_CREATE_AN_ISSUE")

        Returns:
            ComposioToolDefinition instance or None if tool not found
        """
        try:
            # Use composio.Composio.actions.get() to retrieve tool details
            tool_info = self.client.actions.get(tool_name)

            if not tool_info:
                logger.warning(f"Tool '{tool_name}' not found in Composio API")
                return None

            # Convert the API response to our ComposioToolDefinition
            return ComposioToolDefinition.from_composio_api(tool_info)

        except Exception as e:
            logger.error(f"Failed to fetch tool definition for '{tool_name}': {str(e)}")
            return None


class ComposioService:
    """Unified interface for Composio operations"""

    def __init__(self, api_key: str):
        self.accounts = ComposioAccountService(api_key)
        self.core = ComposioCoreService(api_key)

    def get_user_connections(self) -> List[ConnectionInfo]:
        """Get user's authorized connections"""
        return self.accounts.get_user_connections()

    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Execute a tool using composio-core

        Args:
            tool_name: The name of the tool to execute (e.g., "HACKERNEWS_GET_USER")
            arguments: Dictionary of arguments to pass to the tool

        Returns:
            The result of the tool execution
        """
        return self.core.execute_tool(tool_name, arguments)

    def get_tool_definition(self, tool_name: str) -> Optional[ComposioToolDefinition]:
        """Fetch tool definition from Composio API

        Args:
            tool_name: The name of the tool to get definition for

        Returns:
            ComposioToolDefinition instance or None if not found
        """
        return self.core.get_tool_definition(tool_name)

    def create_tool_definition_from_api(self, toolkit: str, action: str) -> Optional[ComposioToolDefinition]:
        """Create a ComposioToolDefinition by fetching from API

        Args:
            toolkit: The toolkit name (e.g., "GITHUB")
            action: The action name (e.g., "GITHUB_CREATE_AN_ISSUE")

        Returns:
            ComposioToolDefinition instance with API-fetched schema, or None if failed
        """
        tool_definition = self.get_tool_definition(action)

        if tool_definition:
            # Ensure toolkit and action are set correctly
            tool_definition.toolkit = toolkit
            tool_definition.action = action

        return tool_definition
