import asyncio
import json
from unittest import mock

from vellum.workflows.integrations.mcp_service import MCPHttpClient


def test_mcp_http_client_sse_response():
    """Test that SSE responses are correctly parsed to JSON"""
    # GIVEN an SSE response from the server
    sample_sse_response = (
        "event: message\n"
        'data: {"result":{"protocolVersion":"2025-06-18",'
        '"capabilities":{"tools":{"listChanged":true}},'
        '"serverInfo":{"name":"TestServer","version":"1.0.0"},'
        '"instructions":"Test server for unit tests."},'
        '"jsonrpc":"2.0","id":1}\n\n'
    )
    expected_json = {
        "result": {
            "protocolVersion": "2025-06-18",
            "capabilities": {"tools": {"listChanged": True}},
            "serverInfo": {"name": "TestServer", "version": "1.0.0"},
            "instructions": "Test server for unit tests.",
        },
        "jsonrpc": "2.0",
        "id": 1,
    }

    with mock.patch("vellum.workflows.integrations.mcp_service.httpx.AsyncClient") as mock_client_class:
        mock_client = mock.AsyncMock()
        mock_client_class.return_value = mock_client

        mock_response = mock.Mock()
        mock_response.headers = {"content-type": "text/event-stream"}
        mock_response.text = sample_sse_response
        mock_client.post.return_value = mock_response

        # WHEN we send a request through the MCP client
        async def test_request():
            async with MCPHttpClient("https://test.server.com", {}) as client:
                result = await client._send_request("initialize", {"test": "params"})
                return result

        result = asyncio.run(test_request())

        # THEN the SSE response should be parsed correctly to JSON
        assert result == expected_json

        # AND the request should have been made with correct headers
        mock_client.post.assert_called_once()
        call_args = mock_client.post.call_args
        assert call_args[1]["headers"]["Accept"] == "application/json, text/event-stream"
        assert call_args[1]["headers"]["Content-Type"] == "application/json"


def test_mcp_http_client_json_response():
    """Test that regular JSON responses still work"""
    # GIVEN a regular JSON response from the server
    sample_json_response = {"result": {"test": "data"}, "jsonrpc": "2.0", "id": 1}

    with mock.patch("vellum.workflows.integrations.mcp_service.httpx.AsyncClient") as mock_client_class:
        mock_client = mock.AsyncMock()
        mock_client_class.return_value = mock_client

        mock_response = mock.Mock()
        mock_response.headers = {"content-type": "application/json"}
        mock_response.text = json.dumps(sample_json_response)
        mock_response.json.return_value = sample_json_response
        mock_client.post.return_value = mock_response

        # WHEN we send a request through the MCP client
        async def test_request():
            async with MCPHttpClient("https://test.server.com", {}) as client:
                result = await client._send_request("initialize", {"test": "params"})
                return result

        result = asyncio.run(test_request())

        # THEN the JSON response should be returned as expected
        assert result == sample_json_response
