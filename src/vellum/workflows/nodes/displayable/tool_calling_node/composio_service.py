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
                # Use deprecated UUID for older composio versions - this is what composio-core expects
                connection_id=getattr(item.deprecated, "uuid", item.id),
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
        logger.info(f"ComposioCoreService.__init__ called with API key length: {len(api_key)}")
        self.client = Composio(api_key=api_key)
        logger.info("ComposioCoreService initialized successfully")

    def get_tool_arguments(self, tool_slug: str, provided_arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get tool arguments using Composio API and map provided arguments

        Args:
            tool_slug: The tool slug (e.g., "GMAIL_CREATE_EMAIL_DRAFT")
            provided_arguments: Arguments provided by the model (with kwargs wrapper)

        Returns:
            Properly formatted arguments for the Composio API call
        """
        logger.info(f"Fetching tool schema for: {tool_slug}")

        try:
            # Try multiple ways to get the tool schema
            tool_details = None
            properties = {}
            required_params = []

            # Method 1: Try the new client API
            try:
                actions = self.client.actions.get(actions=[tool_slug], limit=50)
                if actions and len(actions) > 0:
                    tool_details = actions[0]
                    logger.info(f"Retrieved tool via client API: {getattr(tool_details, 'name', 'Unknown')}")

                    # Try to extract schema
                    input_params = getattr(tool_details, "input_parameters", {}) or {}
                    if isinstance(input_params, dict):
                        properties = input_params.get("properties", {})
                        required_params = input_params.get("required", [])
                        logger.info(
                            f"Client API returned {len(properties)} properties, {len(required_params)} required"
                        )
            except Exception as e:
                logger.warning(f"Client API method failed: {e}")

            # Method 2: If schema is empty, try direct access to parameters
            if not properties and tool_details:
                try:
                    # Try different attribute names that might contain the schema
                    for attr_name in ["parameters", "input_schema", "schema", "input_parameters"]:
                        if hasattr(tool_details, attr_name):
                            attr_value = getattr(tool_details, attr_name)
                            logger.info(f"Found attribute '{attr_name}': {type(attr_value)} = {attr_value}")
                            if isinstance(attr_value, dict) and "properties" in attr_value:
                                properties = attr_value["properties"]
                                required_params = attr_value.get("required", [])
                                break
                except Exception as e:
                    logger.warning(f"Direct attribute access failed: {e}")

            # Method 3: If still no schema, use hardcoded fallback for Gmail
            if not properties and tool_slug == "GMAIL_CREATE_EMAIL_DRAFT":
                logger.warning("Using hardcoded Gmail schema fallback")
                properties = {
                    "recipient_email": {"type": "string", "description": "Email recipient"},
                    "subject": {"type": "string", "description": "Email subject"},
                    "body": {"type": "string", "description": "Email body"},
                    "is_html": {"type": "boolean", "description": "Whether body is HTML", "default": False},
                }
                required_params = ["recipient_email", "subject", "body"]

            logger.info(f"Final schema: {len(properties)} parameters, {len(required_params)} required")
            logger.info(f"Properties: {list(properties.keys())}")
            logger.info(f"Required parameters: {required_params}")

            # Parse and map arguments to schema
            return self._map_arguments_to_schema(
                properties=properties, required_params=required_params, provided_arguments=provided_arguments
            )

        except Exception as e:
            logger.error(f"Failed to fetch tool schema for {tool_slug}: {e}")
            # Fallback to basic argument parsing
            return self._parse_raw_arguments(provided_arguments)

    def _parse_raw_arguments(self, provided_arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Parse raw arguments from model response (fallback method)"""
        if isinstance(provided_arguments, dict) and "kwargs" in provided_arguments:
            if provided_arguments["kwargs"] is None:
                return {}
            elif isinstance(provided_arguments["kwargs"], str):
                try:
                    return json.loads(provided_arguments["kwargs"])
                except (json.JSONDecodeError, TypeError):
                    logger.warning("Failed to parse kwargs as JSON, returning original arguments")
                    return provided_arguments
            else:
                return provided_arguments["kwargs"]
        return provided_arguments

    def _map_arguments_to_schema(
        self, properties: Dict[str, Any], required_params: List[str], provided_arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Map provided arguments to the tool's parameter schema with field name mapping

        Args:
            properties: Parameter schema from input_parameters.properties
            required_params: List of required parameter names
            provided_arguments: Arguments from the model (with kwargs wrapper)

        Returns:
            Mapped and validated arguments
        """
        # First, parse the raw arguments from the kwargs wrapper
        parsed_args = self._parse_raw_arguments(provided_arguments)
        logger.info(f"Parsed arguments from model: {parsed_args}")

        # Define field name mappings (model field -> API field)
        field_mappings = {
            # Gmail mappings
            "to": "recipient_email",
            "body": "body",
            "subject": "subject",
            "is_html": "is_html",
            # Add more mappings as needed for other tools
        }

        # Map and validate against schema
        validated_args = {}

        # First, map known field names
        for model_field, api_field in field_mappings.items():
            if model_field in parsed_args and api_field in properties:
                value = parsed_args[model_field]
                param_schema = properties[api_field]
                validated_args[api_field] = self._validate_parameter(api_field, value, param_schema)
                logger.info(f"Mapped '{model_field}' -> '{api_field}': {validated_args[api_field]}")

        # Then handle direct matches (same field name in model and API)
        for param_name, param_schema in properties.items():
            if param_name in parsed_args and param_name not in validated_args:
                value = parsed_args[param_name]
                validated_args[param_name] = self._validate_parameter(param_name, value, param_schema)
                logger.info(f"Direct match '{param_name}': {validated_args[param_name]}")

        # Add defaults for missing optional parameters
        for param_name, param_schema in properties.items():
            if param_name not in validated_args:
                param_default = param_schema.get("default")
                if param_default is not None:
                    validated_args[param_name] = param_default
                    logger.info(f"Using default for '{param_name}': {param_default}")

        # Check for missing required parameters
        missing_required = []
        for required_param in required_params:
            if required_param not in validated_args:
                missing_required.append(required_param)

        if missing_required:
            # Don't raise error, let the API handle it and log the issue
            logger.warning(f"Missing required parameters: {missing_required}")
            logger.warning(f"Available model parameters: {list(parsed_args.keys())}")
            logger.warning(f"Expected API parameters: {required_params}")

        logger.info(f"Final validated arguments: {validated_args}")
        return validated_args

    def _validate_parameter(self, param_name: str, value: Any, param_schema: Dict[str, Any]) -> Any:
        """Validate a single parameter against its schema

        Args:
            param_name: Name of the parameter
            value: Value provided by the model
            param_schema: Schema definition for this parameter

        Returns:
            Validated (and possibly converted) value
        """
        param_type = param_schema.get("type", "string")

        try:
            # Type conversion/validation
            if param_type == "string":
                return str(value) if value is not None else ""
            elif param_type == "boolean":
                if isinstance(value, bool):
                    return value
                elif isinstance(value, str):
                    return value.lower() in ("true", "1", "yes", "on")
                else:
                    return bool(value)
            elif param_type == "array":
                if isinstance(value, list):
                    return value
                elif isinstance(value, str):
                    # Try to parse as JSON array
                    try:
                        return json.loads(value)
                    except (json.JSONDecodeError, TypeError):
                        return [value]  # Wrap single value in array
                else:
                    return [value]  # Wrap single value in array
            elif param_type == "object":
                if isinstance(value, dict):
                    return value
                elif isinstance(value, str):
                    try:
                        return json.loads(value)
                    except (json.JSONDecodeError, TypeError):
                        return value
                else:
                    return value
            else:
                return value

        except Exception as e:
            logger.warning(f"Failed to validate parameter '{param_name}': {e}")
            return value  # Return as-is if validation fails

    def execute_tool(self, tool_name: str, arguments: Dict[str, Any], connection_id: str) -> Any:
        """Execute a tool using composio-core with API-validated arguments"""

        logger.info("@" * 80)
        logger.info("COMPOSIO CORE SERVICE EXECUTE_TOOL CALLED")
        logger.info("@" * 80)
        logger.info(f"Tool name: {tool_name}")
        logger.info(f"Raw arguments: {arguments}")
        logger.info(f"Connection ID: {connection_id}")

        try:
            # Get properly formatted arguments using Composio API schema
            formatted_arguments = self.get_tool_arguments(tool_name, arguments)
            logger.info(f"Schema-validated arguments: {formatted_arguments}")

            # Convert tool name string to Action enum
            logger.info(f"Converting tool name '{tool_name}' to Action enum...")
            action = getattr(Action, tool_name)
            logger.info(f"Action enum resolved: {action}")

            logger.info("Calling self.client.actions.execute with validated arguments...")
            result = self.client.actions.execute(
                action,
                params=formatted_arguments,  # Use schema-validated arguments
                connected_account=connection_id,
                session_id="None",
            )
            logger.info(f"Composio API returned result: {result}")
            logger.info("@" * 80)

            return result

        except Exception as e:
            logger.error(f"Exception in ComposioCoreService.execute_tool: {str(e)}")
            logger.error(f"Exception type: {type(e)}")
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

    def execute_tool(self, tool_name: str, arguments: Dict[str, Any], connection_id: str) -> Any:
        """Execute a tool using composio-core

        Args:
            tool_name: The name of the tool to execute (e.g., "HACKERNEWS_GET_USER")
            arguments: Dictionary of arguments to pass to the tool
            connection_id: The connection ID for the authenticated account

        Returns:
            The result of the tool execution
        """
        return self.core.execute_tool(tool_name, arguments, connection_id)

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
