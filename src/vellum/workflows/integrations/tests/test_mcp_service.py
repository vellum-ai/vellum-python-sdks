import pytest
import asyncio
import json
from unittest import mock

from vellum.workflows.constants import AuthorizationType
from vellum.workflows.errors.types import WorkflowErrorCode
from vellum.workflows.exceptions import NodeException
from vellum.workflows.integrations.mcp_service import MCPHttpClient, MCPService
from vellum.workflows.types.definition import MCPServer, MCPToolDefinition


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


@pytest.mark.asyncio
async def test_mcp_http_client_empty_response():
    """Test that empty responses are handled gracefully"""
    # GIVEN a mock response that returns empty content
    mock_response = mock.Mock()
    mock_response.headers = {"content-type": "application/json"}
    mock_response.text = ""

    # AND a mock httpx client that returns this response
    with mock.patch("vellum.workflows.integrations.mcp_service.httpx.AsyncClient") as mock_client_class:
        mock_client = mock.AsyncMock()
        mock_client.post.return_value = mock_response
        mock_client_class.return_value = mock_client

        # WHEN we call initialize with an empty response
        # THEN it should raise an exception about empty response
        async with MCPHttpClient("https://test.server.com", {}) as client:
            with pytest.raises(Exception, match="Empty response received from server"):
                await client.initialize()


@pytest.mark.asyncio
async def test_mcp_http_client_invalid_sse_json():
    """Test that invalid JSON in SSE data is handled"""
    # GIVEN an SSE response with invalid JSON
    invalid_sse = """event: message
data: {invalid json}

"""

    mock_response = mock.Mock()
    mock_response.headers = {"content-type": "text/event-stream"}
    mock_response.text = invalid_sse

    with mock.patch("vellum.workflows.integrations.mcp_service.httpx.AsyncClient") as mock_client_class:
        mock_client = mock.AsyncMock()
        mock_client.post.return_value = mock_response
        mock_client_class.return_value = mock_client

        # WHEN we call initialize with invalid SSE data
        # THEN it should raise an exception about no valid JSON
        async with MCPHttpClient("https://test.server.com", {}) as client:
            with pytest.raises(Exception, match="No valid JSON data found in SSE response"):
                await client.initialize()


def test_mcp_service_hydrate_tool_definitions():
    """Test tool definition hydration with SSE responses"""
    # GIVEN an MCP server configuration
    sample_mcp_server = MCPServer(
        name="test-server",
        url="https://test.mcp.server.com/mcp",
        authorization_type=AuthorizationType.BEARER_TOKEN,
        bearer_token_value="test-token-123",
    )

    # AND a mock MCP service that returns tools via SSE
    with mock.patch("vellum.workflows.integrations.mcp_service.asyncio.run") as mock_run:
        mock_run.return_value = [
            {
                "name": "resolve-library-id",
                "description": "Resolves library names to IDs",
                "inputSchema": {
                    "type": "object",
                    "properties": {"libraryName": {"type": "string"}},
                    "required": ["libraryName"],
                },
            }
        ]

        # WHEN we hydrate tool definitions
        service = MCPService()
        tool_definitions = service.hydrate_tool_definitions(sample_mcp_server)

        # THEN we should get properly formatted MCPToolDefinition objects
        assert len(tool_definitions) == 1
        assert isinstance(tool_definitions[0], MCPToolDefinition)
        assert tool_definitions[0].name == "resolve-library-id"
        assert tool_definitions[0].description == "Resolves library names to IDs"
        assert tool_definitions[0].server == sample_mcp_server
        assert tool_definitions[0].parameters == {
            "type": "object",
            "properties": {"libraryName": {"type": "string"}},
            "required": ["libraryName"],
        }


def test_mcp_service_list_tools_handles_errors():
    """Test that SSE parsing errors are handled gracefully"""
    # GIVEN an MCP server configuration
    sample_mcp_server = MCPServer(name="test-server", url="https://test.mcp.server.com/mcp")

    # AND a mock that raises an exception during SSE parsing
    with mock.patch("vellum.workflows.integrations.mcp_service.asyncio.run") as mock_run:
        mock_run.side_effect = Exception("SSE parsing failed")

        # WHEN we try to list tools
        service = MCPService()
        tools = service.list_tools(sample_mcp_server)

        # THEN we should get an empty list instead of crashing
        assert tools == []


def test_mcp_service_call_tool_includes_stacktrace_and_raw_data_on_error():
    """
    Tests that NodeException contains stacktrace and raw_data when call_tool errors.
    """
    # GIVEN an MCP server configuration
    sample_mcp_server = MCPServer(
        name="test-server",
        url="https://test.mcp.server.com/mcp",
        authorization_type=AuthorizationType.BEARER_TOKEN,
        bearer_token_value="test-token",
    )

    tool_def = MCPToolDefinition(
        name="test-tool",
        server=sample_mcp_server,
        description="A test tool",
        parameters={},
    )

    # AND a mock httpx client that raises an exception during tool execution
    with mock.patch("vellum.workflows.integrations.mcp_service.httpx.AsyncClient") as mock_client_class:
        mock_client = mock.AsyncMock()
        mock_client_class.return_value = mock_client
        mock_client.post.side_effect = RuntimeError("Tool execution failed")

        # WHEN we try to execute the tool
        service = MCPService()

        with pytest.raises(NodeException) as exc_info:
            service.execute_tool(tool_def, {"arg": "value"})

        # THEN the exception should have the correct error code
        assert exc_info.value.code == WorkflowErrorCode.NODE_EXECUTION

        # AND the exception should have a stacktrace
        assert exc_info.value.stacktrace is not None
        assert len(exc_info.value.stacktrace) > 0
        assert "RuntimeError: Tool execution failed" in exc_info.value.stacktrace

        # AND the exception should have raw_data with operation details
        assert exc_info.value.raw_data is not None
        assert exc_info.value.raw_data["operation"] == "call_tool"
        assert exc_info.value.raw_data["error_type"] == "RuntimeError"
        assert exc_info.value.raw_data["error_message"] == "Tool execution failed"
