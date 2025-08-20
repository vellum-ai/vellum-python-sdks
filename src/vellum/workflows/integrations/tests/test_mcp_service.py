import asyncio
import json
from unittest import mock

from vellum.workflows.constants import AuthorizationType
from vellum.workflows.integrations.mcp_service import MCPHttpClient, MCPService
from vellum.workflows.types.definition import MCPServer


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


def test_mcp_service_bearer_token_auth():
    """Test that bearer token auth headers are set correctly"""
    # GIVEN an MCP server with bearer token auth
    server = MCPServer(
        name="test-server",
        url="https://test.server.com",
        authorization_type=AuthorizationType.BEARER_TOKEN,
        bearer_token_value="test-token-123",
    )

    # WHEN we get auth headers
    service = MCPService()
    headers = service._get_auth_headers(server)

    # THEN the Authorization header should be set correctly
    assert headers == {"Authorization": "Bearer test-token-123"}


def test_mcp_service_api_key_auth():
    """Test that API key auth headers are set correctly"""
    # GIVEN an MCP server with API key auth
    server = MCPServer(
        name="test-server",
        url="https://test.server.com",
        authorization_type=AuthorizationType.API_KEY,
        api_key_header_key="X-API-Key",
        api_key_header_value="api-key-123",
    )

    # WHEN we get auth headers
    service = MCPService()
    headers = service._get_auth_headers(server)

    # THEN the custom API key header should be set correctly
    assert headers == {"X-API-Key": "api-key-123"}
