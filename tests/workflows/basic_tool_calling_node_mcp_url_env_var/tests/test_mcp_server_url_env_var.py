from unittest import mock
from uuid import uuid4
from typing import Iterator, List

from vellum.client.types.execute_prompt_event import ExecutePromptEvent
from vellum.client.types.fulfilled_execute_prompt_event import FulfilledExecutePromptEvent
from vellum.client.types.initiated_execute_prompt_event import InitiatedExecutePromptEvent
from vellum.client.types.prompt_output import PromptOutput
from vellum.client.types.string_vellum_value import StringVellumValue

from tests.workflows.basic_tool_calling_node_mcp_url_env_var.inputs import Inputs
from tests.workflows.basic_tool_calling_node_mcp_url_env_var.workflow import BasicToolCallingNodeMCPUrlEnvVarWorkflow


def test_run_workflow__mcp_server_url_resolved_from_env_var(vellum_adhoc_prompt_client, monkeypatch):
    """
    Tests that when a workflow runs with an MCPServer using an EnvironmentVariableReference
    for the URL, the resolved URL string is passed to the MCP HTTP client.
    """

    # GIVEN an environment variable set to a URL
    expected_url = "https://example.com/mcp"
    monkeypatch.setenv("MCP_SERVER_URL", expected_url)

    # AND a mock MCP HTTP client
    with mock.patch("vellum.workflows.integrations.mcp_service.MCPHttpClient") as mock_mcp_client_class:
        mock_client_instance = mock.Mock()
        mock_client_instance.__aenter__ = mock.AsyncMock(return_value=mock_client_instance)
        mock_client_instance.__aexit__ = mock.AsyncMock(return_value=None)
        mock_client_instance.initialize = mock.AsyncMock(return_value=None)
        mock_client_instance.list_tools = mock.AsyncMock(return_value=[])
        mock_mcp_client_class.return_value = mock_client_instance

        # AND a mock prompt client that returns a simple response
        def generate_prompt_events(*_args, **_kwargs) -> Iterator[ExecutePromptEvent]:
            execution_id = str(uuid4())
            expected_outputs: List[PromptOutput] = [StringVellumValue(value="I can help you with various tasks.")]
            events: List[ExecutePromptEvent] = [
                InitiatedExecutePromptEvent(execution_id=execution_id),
                FulfilledExecutePromptEvent(
                    execution_id=execution_id,
                    outputs=expected_outputs,
                ),
            ]
            yield from events

        vellum_adhoc_prompt_client.adhoc_execute_prompt_stream.side_effect = generate_prompt_events

        # AND a workflow instance
        workflow = BasicToolCallingNodeMCPUrlEnvVarWorkflow()

        # WHEN the workflow is executed
        terminal_event = workflow.run(Inputs(query="What can you help me with?"))

        # THEN the workflow should complete successfully
        assert terminal_event.name == "workflow.execution.fulfilled"

        # AND the MCP client should have been instantiated with the resolved URL
        assert mock_mcp_client_class.call_count >= 1

        # AND the resolved URL string should be passed to MCPHttpClient
        first_call_args = mock_mcp_client_class.call_args_list[0]
        assert first_call_args.args[0] == expected_url
