from unittest import mock
from uuid import uuid4
from typing import Any, Iterator, List

from vellum import (
    ExecutePromptEvent,
    FulfilledExecutePromptEvent,
    InitiatedExecutePromptEvent,
    PromptOutput,
    StringVellumValue,
)
from vellum.workflows.constants import OMIT
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
    vellum_client.execute_prompt_stream.assert_called_once_with(
        expand_meta=OMIT,
        expand_raw=OMIT,
        external_id=OMIT,
        inputs=[],
        metadata=OMIT,
        prompt_deployment_id=None,
        prompt_deployment_name="my-deployment",
        raw_overrides=OMIT,
        release_tag="LATEST",
        request_options={
            "additional_body_parameters": {"execution_context": {"parent_context": None, "trace_id": mock.ANY}}
        },
    )
