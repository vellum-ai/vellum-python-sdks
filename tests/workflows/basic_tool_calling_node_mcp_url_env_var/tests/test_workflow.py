from unittest import mock

from vellum.workflows.integrations.mcp_service import MCPService
from vellum.workflows.references import EnvironmentVariableReference
from vellum.workflows.types.definition import MCPServer


def test_mcp_server_url_env_var__mcp_service_receives_url(monkeypatch):
    """
    Tests that when the MCP service is called with an MCPServer using an EnvironmentVariableReference
    for the URL, the URL is correctly passed to the MCP HTTP client.
    """

    # GIVEN an MCP server configured with an EnvironmentVariableReference for the URL
    env_var_ref = EnvironmentVariableReference(name="MCP_SERVER_URL")
    mcp_server = MCPServer(
        name="my-mcp-server",
        url=env_var_ref,
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

        # AND the URL passed to MCPHttpClient should be the EnvironmentVariableReference
        # (the system handles resolution of descriptors before runtime services execute)
        call_args = mock_mcp_client_class.call_args
        assert call_args.args[0] == env_var_ref
