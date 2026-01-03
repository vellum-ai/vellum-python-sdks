import pytest
from uuid import uuid4
from typing import Any, Iterator, List

from vellum import (
    ExecutePromptEvent,
    FulfilledExecutePromptEvent,
    InitiatedExecutePromptEvent,
    PromptOutput,
    RejectedExecutePromptEvent,
    StringVellumValue,
    VellumError,
)
from vellum.workflows.errors import WorkflowErrorCode
from vellum.workflows.exceptions import NodeException
from vellum.workflows.inputs import BaseInputs
from vellum.workflows.nodes import PromptDeploymentNode
from vellum.workflows.state import BaseState
from vellum.workflows.state.base import StateMeta


def test_text_prompt_deployment_node__basic(vellum_client):
    """Confirm that TextPromptDeploymentNodes output the expected text and results when run."""

    # GIVEN a node that subclasses TextPromptDeploymentNode
    class Inputs(BaseInputs):
        input: str

    class State(BaseState):
        pass

    class MyPromptDeploymentNode(PromptDeploymentNode):
        deployment = "my-deployment"

    # AND a known response from invoking a deployed prompt
    expected_outputs: List[PromptOutput] = [
        StringVellumValue(value="Hello, world!"),
    ]

    def generate_prompt_events(*args: Any, **kwargs: Any) -> Iterator[ExecutePromptEvent]:
        execution_id = str(uuid4())
        events: List[ExecutePromptEvent] = [
            InitiatedExecutePromptEvent(execution_id=execution_id),
            FulfilledExecutePromptEvent(
                execution_id=execution_id,
                outputs=expected_outputs,
            ),
        ]
        yield from events

    vellum_client.execute_prompt_stream.side_effect = generate_prompt_events

    # WHEN the node is run
    node = MyPromptDeploymentNode(
        state=State(
            meta=StateMeta(workflow_inputs=Inputs(input="Say something.")),
        )
    )
    outputs = [o for o in node.run()]

    # THEN the node should have produced the outputs we expect
    results_output = outputs[0]
    assert results_output.name == "results"
    assert results_output.value == expected_outputs

    text_output = outputs[1]
    assert text_output.name == "text"
    assert text_output.value == "Hello, world!"

    # AND we should have made the expected call to stream the prompt execution
    vellum_client.execute_prompt_stream.assert_called_once()
    _, call_kwargs = vellum_client.execute_prompt_stream.call_args
    exec_ctx = call_kwargs["request_options"]["additional_body_parameters"]["execution_context"]
    assert exec_ctx["parent_context"] is not None
    assert exec_ctx["parent_context"]["type"] == "EXTERNAL"

    # AND expand_meta should include finish_reason=True by default
    expand_meta = call_kwargs.get("expand_meta")
    assert expand_meta is not None
    assert expand_meta.finish_reason is True


def test_prompt_deployment_node__provider_error_from_first_event(vellum_client):
    """
    Tests that PromptDeploymentNode raises NodeException with the actual provider error message
    when the first event is REJECTED, rather than a generic "Expected to receive outputs" error.
    """

    # GIVEN a PromptDeploymentNode with basic configuration
    class MyPromptDeploymentNode(PromptDeploymentNode):
        deployment = "my-deployment"

    # AND the API returns a REJECTED event as the first event with a provider quota error
    provider_error = VellumError(
        code="PROVIDER_QUOTA_EXCEEDED",
        message="Google: You exceeded your current quota, please check your plan and billing details.",
    )

    def generate_prompt_events(*args: Any, **kwargs: Any) -> Iterator[ExecutePromptEvent]:
        execution_id = str(uuid4())
        events: List[ExecutePromptEvent] = [
            RejectedExecutePromptEvent(
                execution_id=execution_id,
                error=provider_error,
            ),
        ]
        yield from events

    vellum_client.execute_prompt_stream.side_effect = generate_prompt_events

    # WHEN the node is run
    node = MyPromptDeploymentNode()

    # THEN it should raise a NodeException with the actual provider error
    with pytest.raises(NodeException) as excinfo:
        list(node.run())

    # AND the exception should have the correct error code
    assert excinfo.value.code == WorkflowErrorCode.PROVIDER_QUOTA_EXCEEDED

    # AND the exception message should contain the actual provider error message
    assert "Google: You exceeded your current quota" in excinfo.value.message
