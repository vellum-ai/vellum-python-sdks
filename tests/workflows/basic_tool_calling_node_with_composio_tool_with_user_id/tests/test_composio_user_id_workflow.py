from unittest import mock
from uuid import uuid4
from typing import Iterator, List

from vellum.client.types import (
    ExecutePromptEvent,
    FulfilledExecutePromptEvent,
    FunctionCall,
    FunctionCallVellumValue,
    InitiatedExecutePromptEvent,
)

from tests.workflows.basic_tool_calling_node_with_composio_tool_with_user_id.workflow import (
    BasicToolCallingNodeWithComposioToolWithUserIdWorkflow,
    Inputs,
    github_create_issue_tool_with_user_id,
)


def test_run_workflow__with_user_id(vellum_adhoc_prompt_client, monkeypatch):
    """Test that user_id from ComposioToolDefinition is passed to ComposioService.execute_tool"""

    monkeypatch.setenv("COMPOSIO_API_KEY", "test_api_key")

    mock_composio_result = {"success": True, "data": "test_result"}
    mock_tool_details = {
        "slug": "GITHUB_CREATE_AN_ISSUE",
        "name": "Create GitHub Issue",
        "description": "Create a new issue in a GitHub repository",
        "toolkit": {"slug": "github"},
        "input_parameters": {},
        "version": "1.0.0",
        "tags": [],
    }

    with mock.patch("vellum.workflows.integrations.composio_service.ComposioService") as mock_service_class, mock.patch(
        "vellum.workflows.nodes.displayable.tool_calling_node.utils.ComposioService"
    ) as mock_service_class_utils:
        mock_service_instance = mock.Mock()
        mock_service_instance.execute_tool.return_value = mock_composio_result
        mock_service_instance.get_tool_by_slug.return_value = mock_tool_details
        mock_service_class.return_value = mock_service_instance
        mock_service_class_utils.return_value = mock_service_instance

        def generate_prompt_events(*_args, **_kwargs) -> Iterator[ExecutePromptEvent]:
            execution_id = str(uuid4())
            expected_outputs = [
                FunctionCallVellumValue(
                    value=FunctionCall(
                        arguments={"owner": "test-owner", "repo": "test-repo", "title": "Test Issue"},
                        id="call_composio_user_test",
                        name="github_create_an_issue",
                        state="FULFILLED",
                    ),
                ),
            ]

            events: List[ExecutePromptEvent] = [
                InitiatedExecutePromptEvent(execution_id=execution_id),
                FulfilledExecutePromptEvent(
                    execution_id=execution_id,
                    outputs=expected_outputs,
                ),
            ]
            yield from events

        vellum_adhoc_prompt_client.adhoc_execute_prompt_stream.side_effect = generate_prompt_events

        workflow = BasicToolCallingNodeWithComposioToolWithUserIdWorkflow()

        # WHEN the workflow runs
        workflow.run(Inputs(query="Create a test issue"))

        mock_service_instance.execute_tool.assert_called_with(
            tool_name="GITHUB_CREATE_AN_ISSUE",
            arguments={"owner": "test-owner", "repo": "test-repo", "title": "Test Issue"},
            user_id="test_user_123",
        )
        assert mock_service_instance.execute_tool.call_count >= 1


def test_composio_tool_definition_has_user_id():
    """Test that the ComposioToolDefinition includes the expected user_id"""
    tool = github_create_issue_tool_with_user_id

    user_id = tool.user_id

    assert user_id == "test_user_123"
