import os
from unittest import mock

from vellum.workflows.integrations.mcp_service import MCPService
from vellum.workflows.types.definition import MCPServer


def test_mcp_server_url_env_var__mcp_service_receives_resolved_url(monkeypatch):
    """
    Tests that when the MCP service is called with an MCPServer that has a URL resolved
    from an environment variable, the resolved URL string is passed to the MCP HTTP client.

    Note: The EnvironmentVariableReference resolution happens at the workflow/node level
    before MCPService is called. This test verifies the MCPService correctly passes
    the resolved URL to the MCP HTTP client.
    """

    # GIVEN an environment variable set to a URL
    expected_url = "https://example.com/mcp"
    monkeypatch.setenv("MCP_SERVER_URL", expected_url)

    # AND an MCP server configured with the URL resolved from the environment variable
    # (simulating what happens after EnvironmentVariableReference resolution)
    mcp_server = MCPServer(
        name="my-mcp-server",
        url=os.environ["MCP_SERVER_URL"],
    )

    # AND a mock MCP HTTP client
    with mock.patch("vellum.workflows.integrations.mcp_service.MCPHttpClient") as mock_mcp_client_class:
        mock_client_instance = mock.Mock()
        mock_client_instance.__aenter__ = mock.AsyncMock(return_value=mock_client_instance)
        mock_client_instance.__aexit__ = mock.AsyncMock(return_value=None)
        mock_client_instance.initialize = mock.AsyncMock(return_value=None)
        mock_client_instance.list_tools = mock.AsyncMock(return_value=[])
        mock_mcp_client_class.return_value = mock_client_instance

        # WHEN the MCP service lists tools from the server
        service = MCPService()
        service.list_tools(mcp_server)

        # THEN the MCP client should be instantiated
        assert mock_mcp_client_class.call_count == 1

        # AND the resolved URL string should be passed to MCPHttpClient
        call_args = mock_mcp_client_class.call_args
        assert call_args.args[0] == expected_url
