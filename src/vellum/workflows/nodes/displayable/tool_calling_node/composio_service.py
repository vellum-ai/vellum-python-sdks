from dataclasses import dataclass
from typing import Any, Dict, List

from composio import Action, Composio
from composio_client import Composio as ComposioClient


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
    """Handles tool execution using composio-core"""

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
