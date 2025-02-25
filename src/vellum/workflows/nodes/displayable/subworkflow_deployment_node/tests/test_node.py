import pytest
from datetime import datetime
from uuid import uuid4
from typing import Any, Iterator, List

from vellum.client.core.api_error import ApiError
from vellum.client.types.chat_message import ChatMessage
from vellum.client.types.chat_message_request import ChatMessageRequest
from vellum.client.types.workflow_execution_workflow_result_event import WorkflowExecutionWorkflowResultEvent
from vellum.client.types.workflow_output_string import WorkflowOutputString
from vellum.client.types.workflow_request_chat_history_input_request import WorkflowRequestChatHistoryInputRequest
from vellum.client.types.workflow_request_json_input_request import WorkflowRequestJsonInputRequest
from vellum.client.types.workflow_result_event import WorkflowResultEvent
from vellum.client.types.workflow_stream_event import WorkflowStreamEvent
from vellum.workflows.errors import WorkflowErrorCode
from vellum.workflows.exceptions import NodeException
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


def test_run_workflow__no_deployment():
    """Confirm that we raise error when running a subworkflow deployment node with no deployment attribute set"""

    # GIVEN a Subworkflow Deployment Node
    class ExampleSubworkflowDeploymentNode(SubworkflowDeploymentNode):
        subworkflow_inputs = {
            "fruits": ["apple", "banana", "cherry"],
        }

    # WHEN/THEN running the node should raise a NodeException
    node = ExampleSubworkflowDeploymentNode()
    with pytest.raises(NodeException) as exc_info:
        list(node.run())

    # AND the error message should be correct
    assert exc_info.value.code == WorkflowErrorCode.NODE_EXECUTION
    assert "Expected subworkflow deployment attribute to be either a UUID or STR, got None instead" in str(
        exc_info.value
    )


def test_run_workflow__hyphenated_output(vellum_client):
    """Confirm that we can successfully handle subworkflow outputs with hyphenated names"""

    # GIVEN a Subworkflow Deployment Node
    class ExampleSubworkflowDeploymentNode(SubworkflowDeploymentNode):
        deployment = "example_subworkflow_deployment"
        subworkflow_inputs = {
            "test_input": "test_value",
        }

        class Outputs(SubworkflowDeploymentNode.Outputs):
            final_output_copy: str

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
                            name="final-output_copy",  # Note the hyphen here
                            value="test success",
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
    assert events[-1].name == "final_output_copy"  # Note the underscore here
    assert events[-1].value == "test success"


@pytest.mark.parametrize(
    ["exception", "expected_code", "expected_message"],
    [
        (
            ApiError(status_code=400, body={"detail": "Missing required input variable: 'foo'"}),
            WorkflowErrorCode.INVALID_INPUTS,
            "Missing required input variable: 'foo'",
        ),
        (
            ApiError(status_code=400, body={"message": "Missing required input variable: 'foo'"}),
            WorkflowErrorCode.INVALID_INPUTS,
            "Failed to execute Subworkflow Deployment",
        ),
        (
            ApiError(status_code=400, body="Missing required input variable: 'foo'"),
            WorkflowErrorCode.INTERNAL_ERROR,
            "Failed to execute Subworkflow Deployment",
        ),
        (
            ApiError(status_code=None, body={"detail": "Missing required input variable: 'foo'"}),
            WorkflowErrorCode.INTERNAL_ERROR,
            "Failed to execute Subworkflow Deployment",
        ),
        (
            ApiError(status_code=500, body={"detail": "Missing required input variable: 'foo'"}),
            WorkflowErrorCode.INTERNAL_ERROR,
            "Failed to execute Subworkflow Deployment",
        ),
    ],
    ids=["400", "invalid_dict", "invalid_body", "no_status_code", "500"],
)
def test_subworkflow_deployment_node__api_error__invalid_inputs_node_exception(
    vellum_client, exception, expected_code, expected_message
):
    # GIVEN a prompt node with an invalid model name
    class MyNode(SubworkflowDeploymentNode):
        deployment = "example_subworkflow_deployment"
        subworkflow_inputs = {
            "not_foo": "bar",
        }

    # AND the Subworkflow Deployment API call fails
    def _side_effect(*args: Any, **kwargs: Any) -> Iterator[WorkflowStreamEvent]:
        if kwargs.get("_mock_condition_to_induce_an_error"):
            yield WorkflowExecutionWorkflowResultEvent(
                execution_id=str(uuid4()),
                data=WorkflowResultEvent(
                    id=str(uuid4()),
                    state="INITIATED",
                    ts=datetime.now(),
                ),
            )
        else:
            raise exception

    # AND the vellum client execute workflow stream raises a 4xx error
    vellum_client.execute_workflow_stream.side_effect = _side_effect

    # WHEN the node is run
    with pytest.raises(NodeException) as e:
        list(MyNode().run())

    # THEN the node raises the correct NodeException
    assert e.value.code == expected_code
    assert e.value.message == expected_message


def test_subworkflow_deployment_node__immediate_api_error__node_exception(vellum_client):
    # GIVEN a prompt node with an invalid model name
    class MyNode(SubworkflowDeploymentNode):
        deployment = "example_subworkflow_deployment"
        subworkflow_inputs = {
            "not_foo": "bar",
        }

    # AND the vellum client execute workflow stream raises a 4xx error
    vellum_client.execute_workflow_stream.side_effect = ApiError(status_code=404, body={"detail": "Not found"})

    # WHEN the node is run
    with pytest.raises(NodeException) as e:
        list(MyNode().run())

    # THEN the node raises the correct NodeException
    assert e.value.code == WorkflowErrorCode.INVALID_INPUTS
    assert e.value.message == "Not found"
