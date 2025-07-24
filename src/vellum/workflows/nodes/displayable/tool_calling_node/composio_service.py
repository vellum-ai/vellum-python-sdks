from dataclasses import dataclass
import json
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

    def _parse_arguments(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Simple argument parsing - handle kwargs wrapper if present"""
        if isinstance(arguments, dict) and len(arguments) == 1 and "kwargs" in arguments:
            kwargs_value = arguments["kwargs"]

            # Handle JSON string kwargs
            if isinstance(kwargs_value, str):
                try:
                    return json.loads(kwargs_value)
                except (json.JSONDecodeError, TypeError):
                    logger.warning("Failed to parse kwargs as JSON, using original arguments")
                    return arguments

            # Handle dict kwargs
            elif isinstance(kwargs_value, dict):
                return kwargs_value

            # Handle None kwargs
            elif kwargs_value is None:
                return {}

        # Return arguments as-is for all other cases
        return arguments

    def execute_tool(self, tool_name: str, arguments: Dict[str, Any], connection_id: str) -> Any:
        """Execute a tool using composio-core with simplified argument processing

        Args:
            tool_name: The name of the tool to execute (e.g., "GMAIL_CREATE_EMAIL_DRAFT")
            arguments: Dictionary of arguments to pass to the tool
            connection_id: The connection ID for the authenticated account

        Returns:
            The result of the tool execution
        """
        logger.info(f"Executing Composio tool: {tool_name}")
        logger.info(f"Raw arguments: {arguments}")
        logger.info(f"Connection ID: {connection_id}")

        try:
            # Simple argument parsing - let Composio API handle validation
            parsed_args = self._parse_arguments(arguments)
            logger.info(f"Parsed arguments: {parsed_args}")

            # Convert tool name string to Action enum and execute
            action = getattr(Action, tool_name)
            result = self.core_client.actions.execute(
                action,
                params=parsed_args,
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

    def get_tool_definition(self, tool_name: str) -> Optional[ComposioToolDefinition]:
        """Fetch tool definition from Composio API

        Args:
            tool_name: The name of the tool to get definition for (e.g., "GITHUB_CREATE_AN_ISSUE")

        Returns:
            ComposioToolDefinition instance or None if tool not found
        """
        try:
            # Get tool details from Composio API
            actions = self.core_client.actions.get(actions=[tool_name], limit=1)

            if not actions or len(actions) == 0:
                logger.warning(f"Tool '{tool_name}' not found in Composio API")
                return None

            tool_info = actions[0]

            # Convert the API response to our ComposioToolDefinition
            return ComposioToolDefinition.from_composio_api(tool_info)

        except Exception as e:
            logger.error(f"Failed to fetch tool definition for '{tool_name}': {str(e)}")
            return None

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
