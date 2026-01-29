import asyncio
import json
import logging
import traceback
from typing import Any, Dict, List, Optional

import httpx

from vellum.workflows.constants import AuthorizationType
from vellum.workflows.errors.types import WorkflowErrorCode
from vellum.workflows.exceptions import NodeException
from vellum.workflows.types.core import VellumSecret
from vellum.workflows.types.definition import MCPServer, MCPToolDefinition

logger = logging.getLogger(__name__)


class MCPHttpClient:
    """
    Direct HTTP implementation for MCP (Model Context Protocol) client
    without using the official Python SDK.

    Supports Streamable HTTP transport using httpx.
    """

    def __init__(self, server_url: str, headers: Dict[str, str], session_timeout: int = 30):
        """
        Initialize MCP HTTP client.

        Args:
            server_url: The MCP server endpoint URL (e.g., "https://example.com/mcp")
            headers: Authentication headers
            session_timeout: Timeout for HTTP requests in seconds
        """
        self.server_url = server_url.rstrip("/")
        self.headers = headers
        self.session_timeout = session_timeout
        self.session_id: Optional[str] = None
        self.request_id = 0
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self):
        """Async context manager entry."""
        self._client = httpx.AsyncClient(timeout=httpx.Timeout(self.session_timeout), headers=self.headers)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self._client:
            await self._client.aclose()

    def _next_request_id(self) -> int:
        """Generate next request ID."""
        self.request_id += 1
        return self.request_id

    async def _send_request(self, method: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Send a JSON-RPC request to the MCP server.

        Args:
            method: The JSON-RPC method name
            params: Optional parameters for the method

        Returns:
            The JSON-RPC response
        """
        if not self._client:
            raise RuntimeError("Client session not initialized. Use 'async with' context manager.")

        # Prepare JSON-RPC request
        request_data = {"jsonrpc": "2.0", "id": self._next_request_id(), "method": method, "params": params or {}}

        # Prepare headers
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        }

        # Include session ID if we have one
        if self.session_id:
            headers["Mcp-Session-Id"] = self.session_id

        logger.debug(f"Sending request: {json.dumps(request_data, indent=2)}")

        # Send POST request
        response = await self._client.post(self.server_url, json=request_data, headers=headers)

        # Check for session ID in response headers
        if "Mcp-Session-Id" in response.headers:
            self.session_id = response.headers["Mcp-Session-Id"]

        # Handle response based on content type
        content_type = response.headers.get("content-type", "").lower()

        if "text/event-stream" in content_type:
            # Handle SSE response
            response_text = response.text

            # Parse SSE format to extract JSON data
            lines = response_text.strip().split("\n")
            json_data = None

            for line in lines:
                if line.startswith("data: "):
                    data_content = line[6:]  # Remove 'data: ' prefix
                    if data_content.strip() and data_content != "[DONE]":
                        try:
                            json_data = json.loads(data_content)
                            break
                        except json.JSONDecodeError:
                            continue

            if json_data is None:
                raise Exception("No valid JSON data found in SSE response")

            response_data = json_data
        else:
            # Handle regular JSON response
            if not response.text.strip():
                raise Exception("Empty response received from server")

            try:
                response_data = response.json()
            except json.JSONDecodeError as e:
                raise Exception(f"Invalid JSON response: {str(e)}")

        if "error" in response_data:
            raise Exception(f"MCP Error: {response_data['error']}")

        return response_data

    async def initialize(self, client_info: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Initialize the MCP connection.

        Args:
            client_info: Optional client information

        Returns:
            Server capabilities and information
        """
        params = {
            "protocolVersion": "2025-06-18",
            "capabilities": {},
            "clientInfo": client_info or {"name": "vellum-mcp-client", "version": "1.0.0"},
        }

        response = await self._send_request("initialize", params)
        return response.get("result", {})

    async def list_tools(self) -> List[Dict[str, Any]]:
        """
        Get list of available tools from the server.

        Returns:
            List of tool definitions
        """
        response = await self._send_request("tools/list")
        return response.get("result", {}).get("tools", [])

    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call a tool on the server.

        Args:
            name: Tool name
            arguments: Tool arguments

        Returns:
            Tool execution result
        """
        params = {"name": name, "arguments": arguments}

        response = await self._send_request("tools/call", params)
        return response.get("result", {})


class MCPService:
    def _get_auth_headers(self, server: MCPServer) -> Dict[str, str]:
        headers = {}
        if server.authorization_type == AuthorizationType.BEARER_TOKEN:
            token = server.bearer_token_value
            if not token:
                raise NodeException(
                    "Bearer token is required for BEARER_TOKEN authorization type",
                    code=WorkflowErrorCode.INVALID_INPUTS,
                )

            headers["Authorization"] = f"Bearer {token}"

        elif server.authorization_type == AuthorizationType.API_KEY:
            key = server.api_key_header_key
            value = server.api_key_header_value
            if not key or not value:
                raise NodeException(
                    "API key header key and value are required for API_KEY authorization type",
                    code=WorkflowErrorCode.INVALID_INPUTS,
                )
            if isinstance(value, VellumSecret):
                headers[key] = value.name
            elif isinstance(value, str):
                headers[key] = value

        return headers

    async def _execute_mcp_call(self, server: MCPServer, operation: str, **kwargs) -> Any:
        """Execute an MCP operation using direct HTTP calls."""
        headers = self._get_auth_headers(server)

        try:
            async with MCPHttpClient(server.url, headers) as client:
                await client.initialize()

                if operation == "list_tools":
                    return await client.list_tools()
                elif operation == "call_tool":
                    return await client.call_tool(
                        name=kwargs["name"],
                        arguments=kwargs["arguments"],
                    )
                else:
                    raise ValueError(f"Unknown MCP operation: {operation}")

        except Exception as e:
            logger.error(f"Error executing MCP operation {operation}: {e}")
            raise NodeException(
                message=f"Error executing MCP operation '{operation}': {str(e)}",
                code=WorkflowErrorCode.NODE_EXECUTION,
                stacktrace=traceback.format_exc(),
                raw_data={"operation": operation, "error_type": type(e).__name__, "error_message": str(e)},
            )

    def list_tools(self, server: MCPServer) -> List[Dict[str, Any]]:
        """List available tools from an MCP server."""
        try:
            tools = asyncio.run(self._execute_mcp_call(server, "list_tools"))
            return tools
        except Exception as e:
            logger.warning(f"Failed to list tools from MCP server '{server.name}': {e}")
            return []

    def execute_tool(self, tool_def: MCPToolDefinition, arguments: Dict[str, Any]) -> Any:
        """Execute a tool on an MCP server."""
        try:
            result = asyncio.run(
                self._execute_mcp_call(
                    tool_def.server,
                    "call_tool",
                    name=tool_def.name,
                    arguments=arguments,
                )
            )
            return result
        except NodeException:
            raise
        except Exception as e:
            logger.error(f"Error executing MCP tool '{tool_def.name}': {e}")
            raise NodeException(
                message=f"Error executing MCP tool '{tool_def.name}': {str(e)}",
                code=WorkflowErrorCode.NODE_EXECUTION,
                stacktrace=traceback.format_exc(),
                raw_data={"tool_name": tool_def.name, "error_type": type(e).__name__, "error_message": str(e)},
            )

    def hydrate_tool_definitions(self, server_def: MCPServer) -> List[MCPToolDefinition]:
        """Hydrate an MCPToolDefinition with detailed information from the MCP server."""
        try:
            tools = self.list_tools(server_def)

            return [
                MCPToolDefinition(
                    name=tool["name"],
                    server=server_def,
                    description=tool["description"],
                    parameters=tool["inputSchema"],
                )
                for tool in tools
            ]
        except Exception as e:
            logger.warning(f"Failed to hydrate MCP server '{server_def.name}': {e}")
            return []
