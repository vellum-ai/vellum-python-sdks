from dataclasses import dataclass
import logging
import os
from typing import Any, Dict, List, Optional

import requests

from vellum.workflows.errors.types import WorkflowErrorCode
from vellum.workflows.exceptions import NodeException

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
    """Composio API client for managing connections and executing tools"""

    def __init__(self, api_key: Optional[str] = None):
        # If no API key provided, look it up from environment variables
        if api_key is None:
            api_key = self._get_api_key_from_env()

        if not api_key:
            common_env_var_names = ["COMPOSIO_API_KEY", "COMPOSIO_KEY"]
            raise NodeException(
                "No Composio API key found. "
                "Please provide an api_key parameter or set one of these environment variables: "
                + ", ".join(common_env_var_names)
            )

        self.api_key = api_key
        self.base_url = "https://backend.composio.dev/api/v3"

    @staticmethod
    def _get_api_key_from_env() -> Optional[str]:
        """Get Composio API key from environment variables"""
        common_env_var_names = ["COMPOSIO_API_KEY", "COMPOSIO_KEY"]

        for env_var_name in common_env_var_names:
            value = os.environ.get(env_var_name)
            if value:
                return value
        return None

    def _make_request(
        self, endpoint: str, method: str = "GET", params: Optional[dict] = None, json_data: Optional[dict] = None
    ) -> dict:
        """Make a request to the Composio API"""
        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
        }

        url = f"{self.base_url}{endpoint}"

        try:
            if method == "GET":
                response = requests.get(url, headers=headers, params=params or {}, timeout=30)
            elif method == "POST":
                response = requests.post(url, headers=headers, json=json_data or {}, timeout=30)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                raise NodeException(
                    message="Failed to authorize Composio request. Make sure to define a COMPOSIO_API_KEY",
                    code=WorkflowErrorCode.PROVIDER_CREDENTIALS_UNAVAILABLE,
                )
            else:
                response_text = e.response.text if e.response else "No response"
                raise NodeException(
                    f"Composio API request failed with status {e.response.status_code}: {response_text}"
                )
        except Exception as e:
            raise NodeException(f"Composio API request failed: {e}")

    def get_user_connections(self) -> List[ConnectionInfo]:
        """Get all authorized connections for the user"""
        response = self._make_request("/connected_accounts")

        return [
            ConnectionInfo(
                connection_id=item.get("id"),
                integration_name=item.get("toolkit", {}).get("slug", ""),
                status=item.get("status", "ACTIVE"),
                created_at=item.get("created_at", ""),
                updated_at=item.get("updated_at", ""),
            )
            for item in response.get("items", [])
        ]

    def get_tool_by_slug(self, tool_slug: str) -> Dict[str, Any]:
        """Get detailed information about a tool using its slug identifier

        Args:
            tool_slug: The unique slug identifier of the tool

        Returns:
            Dictionary containing detailed tool information including:
            - slug, name, description
            - toolkit info (slug, name, logo)
            - input_parameters, output_parameters
            - no_auth, available_versions, version
            - scopes, tags, deprecated info

        Raises:
            NodeException: If tool not found (404), unauthorized (401), or other API errors
        """
        endpoint = f"/tools/{tool_slug}"

        try:
            response = self._make_request(endpoint, method="GET")
            logger.info(f"Retrieved tool details for slug '{tool_slug}': {response}")
            return response
        except Exception as e:
            # Enhanced error handling for specific cases
            error_message = str(e)
            if "404" in error_message:
                raise NodeException(f"Tool with slug '{tool_slug}' not found in Composio")
            elif "401" in error_message:
                raise NodeException(f"Unauthorized access to tool '{tool_slug}'. Check your Composio API key.")
            else:
                raise NodeException(f"Failed to retrieve tool details for '{tool_slug}': {error_message}")

    def execute_tool(self, tool_name: str, arguments: Dict[str, Any], user_id: Optional[str] = None) -> Any:
        """Execute a tool using direct API request

        Args:
            tool_name: The name of the tool to execute (e.g., "HACKERNEWS_GET_USER")
            arguments: Dictionary of arguments to pass to the tool
            user_id: Optional user ID to identify which user's Composio connection to use

        Returns:
            The result of the tool execution
        """
        endpoint = f"/tools/execute/{tool_name}"
        json_data: Dict[str, Any] = {"arguments": arguments}
        if user_id is not None:
            json_data["user_id"] = user_id
        response = self._make_request(endpoint, method="POST", json_data=json_data)

        if not response.get("successful", True):
            return response.get("error", "Tool execution failed")

        return response.get("data", response)
