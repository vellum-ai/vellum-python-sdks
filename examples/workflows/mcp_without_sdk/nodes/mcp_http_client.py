import json
from typing import Any, Dict, List, Optional

import aiohttp


class MCPHttpClient:
    def __init__(self, server_url: str, token: str):
        self.server_url = server_url
        self.token = token
        self.request_id = 0
        self.session_id: Optional[str] = None
        self.session_timeout = 30
        self._session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        """Async context manager entry."""
        self._session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.session_timeout))
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self._session:
            await self._session.close()

    def _next_request_id(self) -> int:
        """Generate next request ID."""
        self.request_id += 1
        return self.request_id

    async def initialize(self, client_info: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Initialize the MCP connection.

        Args:
            client_info: Optional client information

        Returns:
            Server capabilities and information
        """

        params = {
            "protocolVersion": "2025-03-26",
            "capabilities": {},
            "clientInfo": client_info or {"name": "custom-mcp-client", "version": "1.0.0"},
        }

        response = await self._send_request("initialize", params)
        print(f"Received initialize response: {json.dumps(response, indent=2)}")
        return response.get("result", {})

    async def _send_request(self, method: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Send a JSON-RPC request to the MCP server.

        Args:
            method: The JSON-RPC method name
            params: Optional parameters for the method

        Returns:
            The JSON-RPC response
        """
        if not self._session:
            raise RuntimeError("Client session not initialized. Use 'async with' context manager.")

        # Prepare JSON-RPC request
        request_data = {"jsonrpc": "2.0", "id": self._next_request_id(), "method": method, "params": params or {}}

        # Prepare headers
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {self.token}",
        }

        # Include session ID if we have one
        if self.session_id:
            headers["Mcp-Session-Id"] = self.session_id

        print(f"Sending request: {json.dumps(request_data, indent=2)}")

        # Send POST request
        async with self._session.post(self.server_url, json=request_data, headers=headers) as response:

            # Check for session ID in response headers
            if "Mcp-Session-Id" in response.headers:
                self.session_id = response.headers["Mcp-Session-Id"]
                print(f"Received session ID: {self.session_id}")

            response_data = await response.json()

            if "error" in response_data:
                print(f"Error: {response_data['error']}")
                raise Exception(response_data["error"])

            return response_data

    async def list_tools(self) -> List[Dict[str, Any]]:
        """
        Get list of available tools from the server.

        Returns:
            List of tool definitions
        """
        response = await self._send_request("tools/list")
        print(f"Received {len(response.get('result', {}).get('tools', []))} tools")
        return response

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
        print(f"Received tools/call response: {json.dumps(response, indent=2)}")
        return response
