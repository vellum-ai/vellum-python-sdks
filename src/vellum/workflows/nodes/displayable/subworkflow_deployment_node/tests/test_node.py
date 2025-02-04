import pytest
from datetime import datetime
from uuid import uuid4
from typing import Any, Iterator, List

from vellum.client.types.chat_message import ChatMessage
from vellum.client.types.chat_message_request import ChatMessageRequest
from vellum.client.types.workflow_execution_workflow_result_event import WorkflowExecutionWorkflowResultEvent
from vellum.client.types.workflow_output_string import WorkflowOutputString
from vellum.client.types.workflow_request_chat_history_input_request import WorkflowRequestChatHistoryInputRequest
from vellum.client.types.workflow_request_json_input_request import WorkflowRequestJsonInputRequest
from vellum.client.types.workflow_result_event import WorkflowResultEvent
from vellum.client.types.workflow_stream_event import WorkflowStreamEvent
from vellum.workflows.nodes.displayable.subworkflow_deployment_node.node import SubworkflowDeploymentNode


@pytest.mark.parametrize("ChatMessageClass", [ChatMessageRequest, ChatMessage])
def test_run_workflow__chat_history_input(vellum_client, ChatMessageClass):
    """Confirm that we can successfully invoke a Subworkflow Deployment Node that uses Chat History Inputs"""

    # GIVEN a Subworkflow Deployment Node
    class ExampleSubworkflowDeploymentNode(SubworkflowDeploymentNode):
        deployment = "example_subworkflow_deployment"
        subworkflow_inputs = {
            "chat_history": [ChatMessageClass(role="USER", text="Hello, how are you?")],
        }

    # AND we know what the Subworkflow Deployment will respond with
    def generate_subworkflow_events(*args: Any, **kwargs: Any) -> Iterator[WorkflowStreamEvent]:
        execution_id = str(uuid4())
        expected_events: List[WorkflowStreamEvent] = [
            WorkflowExecutionWorkflowResultEvent(
                execution_id=execution_id,
                data=WorkflowResultEvent(
                    id=str(uuid4()),
                    state="INITIATED",
                    ts=datetime.now(),
                ),
            ),
            WorkflowExecutionWorkflowResultEvent(
                execution_id=execution_id,
                data=WorkflowResultEvent(
                    id=str(uuid4()),
                    state="FULFILLED",
                    ts=datetime.now(),
                    outputs=[
                        WorkflowOutputString(
                            id=str(uuid4()),
                            name="greeting",
                            value="Great!",
                        )
                    ],
                ),
            ),
        ]
        yield from expected_events

    vellum_client.execute_workflow_stream.side_effect = generate_subworkflow_events

    # WHEN we run the node
    node = ExampleSubworkflowDeploymentNode()
    events = list(node.run())

    # THEN the node should have completed successfully
    assert events[-1].name == "greeting"
    assert events[-1].value == "Great!"

    # AND we should have invoked the Subworkflow Deployment with the expected inputs
    call_kwargs = vellum_client.execute_workflow_stream.call_args.kwargs
    assert call_kwargs["inputs"] == [
        WorkflowRequestChatHistoryInputRequest(
            name="chat_history", value=[ChatMessageRequest(role="USER", text="Hello, how are you?")]
        ),
    ]


def test_run_workflow__any_array(vellum_client):
    """Confirm that we can successfully invoke a Subworkflow Deployment Node that uses any array input"""

    # GIVEN a Subworkflow Deployment Node
    class ExampleSubworkflowDeploymentNode(SubworkflowDeploymentNode):
        deployment = "example_subworkflow_deployment"
        subworkflow_inputs = {
            "fruits": ["apple", "banana", "cherry"],
        }

    # AND we know what the Subworkflow Deployment will respond with
    def generate_subworkflow_events(*args: Any, **kwargs: Any) -> Iterator[WorkflowStreamEvent]:
        execution_id = str(uuid4())
        expected_events: List[WorkflowStreamEvent] = [
            WorkflowExecutionWorkflowResultEvent(
                execution_id=execution_id,
                data=WorkflowResultEvent(
                    id=str(uuid4()),
                    state="INITIATED",
                    ts=datetime.now(),
                ),
            ),
            WorkflowExecutionWorkflowResultEvent(
                execution_id=execution_id,
                data=WorkflowResultEvent(
                    id=str(uuid4()),
                    state="FULFILLED",
                    ts=datetime.now(),
                    outputs=[
                        WorkflowOutputString(
                            id=str(uuid4()),
                            name="greeting",
                            value="Great!",
                        )
                    ],
                ),
            ),
        ]
        yield from expected_events

    vellum_client.execute_workflow_stream.side_effect = generate_subworkflow_events

    # WHEN we run the node
    node = ExampleSubworkflowDeploymentNode()
    events = list(node.run())

    # THEN the node should have completed successfully
    assert events[-1].name == "greeting"
    assert events[-1].value == "Great!"

    # AND we should have invoked the Subworkflow Deployment with the expected inputs
    call_kwargs = vellum_client.execute_workflow_stream.call_args.kwargs
    assert call_kwargs["inputs"] == [
        WorkflowRequestJsonInputRequest(name="fruits", value=["apple", "banana", "cherry"]),
    ]
