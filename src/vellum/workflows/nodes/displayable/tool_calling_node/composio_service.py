from dataclasses import dataclass
import logging
from typing import Any, Dict, List

from composio import Action, Composio
from composio_client import Composio as ComposioClient

logger = logging.getLogger(__name__)


@dataclass
class ConnectionInfo:
    """Information about a user's authorized connection"""

    connection_id: str
    integration_name: str
    created_at: str
    updated_at: str
    status: str = "ACTIVE"


class ComposioService:
    """Simplified unified interface for Composio operations"""

    def __init__(self, api_key: str):
        """Initialize with both Composio clients"""
        self.core_client = Composio(api_key=api_key)  # For tool execution
        self.account_client = ComposioClient(api_key=api_key)  # For account management
        logger.info(f"ComposioService initialized with API key length: {len(api_key)}")

    def get_user_connections(self) -> List[ConnectionInfo]:
        """Get all authorized connections for the user"""
        response = self.account_client.connected_accounts.list()

        return [
            ConnectionInfo(
                # Use deprecated UUID for older composio versions - this is what composio-core expects
                connection_id=getattr(item.deprecated, "uuid", item.id),
                integration_name=item.toolkit.slug,
                status=item.status,
                created_at=item.created_at,
                updated_at=item.updated_at,
            )
            for item in response.items
        ]

    def execute_tool(self, tool_name: str, arguments: Dict[str, Any], connection_id: str) -> Any:
        """Execute a tool using composio-core

        Args:
            tool_name: The name of the tool to execute (e.g., "GMAIL_CREATE_EMAIL_DRAFT")
            arguments: Dictionary of arguments to pass to the tool
            connection_id: The connection ID for the authenticated account

        Returns:
            The result of the tool execution
        """
        logger.info(f"Executing Composio tool: {tool_name}")
        logger.info(f"Arguments: {arguments}")
        logger.info(f"Connection ID: {connection_id}")

        try:
            # Convert tool name string to Action enum and execute
            action = getattr(Action, tool_name)
            result = self.core_client.actions.execute(
                action,
                params=arguments,
                connected_account=connection_id,
                session_id="None",
            )

            logger.info(f"Composio API returned result: {result}")
            return result

        except Exception as e:
            logger.error(f"Error executing Composio tool '{tool_name}': {str(e)}")
            import traceback

            logger.error(f"Traceback: {traceback.format_exc()}")
            raise
