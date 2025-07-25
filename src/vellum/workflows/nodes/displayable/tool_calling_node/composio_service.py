from dataclasses import dataclass
import logging
from typing import Any, Dict, List, Optional

import requests

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

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://backend.composio.dev/api/v3"

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

    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Execute a tool using direct API request

        Args:
            tool_name: The name of the tool to execute (e.g., "HACKERNEWS_GET_USER")
            arguments: Dictionary of arguments to pass to the tool

        Returns:
            The result of the tool execution
        """
        endpoint = f"/tools/execute/{tool_name}"
        response = self._make_request(endpoint, method="POST", json_data=arguments)
        return response.get("data", response)
