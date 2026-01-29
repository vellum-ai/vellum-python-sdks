from uuid import uuid4
from typing import Iterator, List

from vellum.client.types.chat_message import ChatMessage
from vellum.client.types.execute_prompt_event import ExecutePromptEvent
from vellum.client.types.fulfilled_execute_prompt_event import FulfilledExecutePromptEvent
from vellum.client.types.function_call import FunctionCall
from vellum.client.types.function_call_chat_message_content import FunctionCallChatMessageContent
from vellum.client.types.function_call_chat_message_content_value import FunctionCallChatMessageContentValue
from vellum.client.types.function_call_vellum_value import FunctionCallVellumValue
from vellum.client.types.initiated_execute_prompt_event import InitiatedExecutePromptEvent
from vellum.client.types.prompt_output import PromptOutput
from vellum.client.types.string_chat_message_content import StringChatMessageContent
from vellum.client.types.string_vellum_value import StringVellumValue
from vellum.client.types.workflow_deployment_release import WorkflowDeploymentRelease
from vellum.client.types.workflow_execution_workflow_result_event import WorkflowExecutionWorkflowResultEvent
from vellum.client.types.workflow_output_string import WorkflowOutputString
from vellum.client.types.workflow_result_event import WorkflowResultEvent
from vellum.workflows.events.workflow import WorkflowExecutionFulfilledEvent

from tests.workflows.basic_tool_calling_node_workflow_deployment_tool_wrapper.workflow import (
    BasicToolCallingNodeWorkflowDeploymentToolWrapperWorkflow,
    WorkflowInputs,
)


def test_workflow_deployment_tool_wrapper__merges_inputs_from_parent(vellum_adhoc_prompt_client, vellum_client):
    """
    Tests that a workflow deployment with tool wrapper correctly merges inputs from the parent workflow.
    """

    # GIVEN a mock that returns function call events followed by a final response
    def generate_prompt_events(*args, **kwargs) -> Iterator[ExecutePromptEvent]:  # noqa: U100
        execution_id = str(uuid4())

        call_count = vellum_adhoc_prompt_client.adhoc_execute_prompt_stream.call_count
        expected_outputs: List[PromptOutput]
        if call_count == 1:
            expected_outputs = [
                FunctionCallVellumValue(
                    value=FunctionCall(
                        arguments={"city": "San Francisco", "date": "2025-01-01"},
                        id="call_workflow_deployment",
                        name="weatherworkflowdeployment",
                        state="FULFILLED",
                    ),
                ),
            ]
        else:
            expected_outputs = [
                StringVellumValue(
                    value="Based on the function call, the current temperature in San Francisco is 70 degrees."
                )
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

    # AND a mock for the workflow deployment release info
    mock_workflow_deployment_release = WorkflowDeploymentRelease(
        id="mock-deployment-id",
        created="2024-01-01T00:00:00Z",
        environment={"id": "mock-env-id", "name": "mock-env-name", "label": "mock-env-label"},
        created_by={"id": "mock-user-id", "email": "mock@example.com"},
        workflow_version={
            "id": "mock-version-id",
            "input_variables": [
                {"id": "city-input-id", "key": "city", "type": "STRING", "required": True, "default": None},
                {"id": "date-input-id", "key": "date", "type": "STRING", "required": True, "default": None},
                {"id": "context-input-id", "key": "context", "type": "STRING", "required": False, "default": None},
            ],
            "output_variables": [],
        },
        deployment={"id": "mock-deployment-id", "name": "weather-workflow-deployment"},
        description="A workflow that gets the weather for a given city and date.",
        release_tags=[],
        reviews=[],
    )
    vellum_client.workflow_deployments.retrieve_workflow_deployment_release.return_value = (
        mock_workflow_deployment_release
    )

    # AND a mock for the workflow deployment execution that includes the context
    def mock_workflow_execution(*args, **kwargs):  # noqa: U100
        # Check that the context was passed to the workflow deployment
        inputs = kwargs.get("inputs", [])
        context_input = next((i for i in inputs if i.name == "context"), None)
        context_value = context_input.value if context_input else ""

        yield WorkflowExecutionWorkflowResultEvent(
            execution_id="mock-execution-id",
            type="WORKFLOW",
            data=WorkflowResultEvent(id="mock-event-id", state="INITIATED", ts="2024-01-01T00:00:00Z"),
        )
        yield WorkflowExecutionWorkflowResultEvent(
            execution_id="mock-execution-id",
            type="WORKFLOW",
            data=WorkflowResultEvent(id="mock-event-id", state="STREAMING", ts="2024-01-01T00:00:00Z"),
        )
        yield WorkflowExecutionWorkflowResultEvent(
            execution_id="mock-execution-id",
            type="WORKFLOW",
            data=WorkflowResultEvent(
                id="mock-event-id",
                state="FULFILLED",
                ts="2024-01-01T00:00:00Z",
                outputs=[
                    WorkflowOutputString(
                        id="mock-output-id",
                        name="result",
                        type="STRING",
                        value=f"The weather in San Francisco on 2025-01-01 was hot. Context: {context_value}",
                    )
                ],
            ),
        )

    vellum_client.execute_workflow_stream.side_effect = mock_workflow_execution

    # AND a workflow that uses a workflow deployment with tool wrapper
    workflow = BasicToolCallingNodeWorkflowDeploymentToolWrapperWorkflow()

    # WHEN the workflow is executed
    terminal_event = workflow.run(
        inputs=WorkflowInputs(
            query="What's the weather like in San Francisco?",
            context="This is additional context from parent workflow",
        )
    )

    # THEN the workflow should complete successfully
    assert terminal_event.name == "workflow.execution.fulfilled"
    assert isinstance(terminal_event, WorkflowExecutionFulfilledEvent)

    # AND the output should contain the expected text
    assert terminal_event.outputs.text == (
        "Based on the function call, the current temperature in San Francisco is 70 degrees."
    )

    # AND the chat history should include the function call with merged context
    chat_history = terminal_event.outputs.chat_history
    assert len(chat_history) == 3

    # AND the function result should include the context from the parent workflow
    function_result_message = chat_history[1]
    assert function_result_message.role == "FUNCTION"
    assert isinstance(function_result_message.content, StringChatMessageContent)
    assert "This is additional context from parent workflow" in function_result_message.content.value

    # AND the chat history should have the expected structure
    assert chat_history == [
        ChatMessage(
            text=None,
            role="ASSISTANT",
            content=FunctionCallChatMessageContent(
                type="FUNCTION_CALL",
                value=FunctionCallChatMessageContentValue(
                    name="weatherworkflowdeployment",
                    arguments={"city": "San Francisco", "date": "2025-01-01"},
                    id="call_workflow_deployment",
                ),
            ),
            source=None,
        ),
        ChatMessage(
            text=None,
            role="FUNCTION",
            content=StringChatMessageContent(
                type="STRING",
                value='{"result": "The weather in San Francisco on 2025-01-01 was hot. Context: This is additional context from parent workflow"}',  # noqa: E501
            ),
            source="call_workflow_deployment",
        ),
        ChatMessage(
            text="Based on the function call, the current temperature in San Francisco is 70 degrees.",
            role="ASSISTANT",
            content=None,
            source=None,
        ),
    ]
