from unittest import mock
from uuid import uuid4
from typing import Any, Iterator, List

from vellum import (
    ExecutePromptEvent,
    FulfilledExecutePromptEvent,
    InitiatedExecutePromptEvent,
    PromptOutput,
    PromptParameters,
    RejectedExecutePromptEvent,
    StringVellumValue,
    VellumError,
)
from vellum.workflows.errors import WorkflowError as SdkVellumError
from vellum.workflows.errors.types import WorkflowErrorCode
from vellum.workflows.inputs import BaseInputs
from vellum.workflows.nodes import InlinePromptNode
from vellum.workflows.nodes.core.try_node.node import TryNode
from vellum.workflows.outputs.base import BaseOutput
from vellum.workflows.state import BaseState
from vellum.workflows.state.base import StateMeta


def test_inline_text_prompt_node__basic(vellum_adhoc_prompt_client):
    """Confirm that InlineTextPromptNodes output the expected text and results when run."""

    # GIVEN a node that subclasses InlineTextPromptNode
    class Inputs(BaseInputs):
        input: str

    class State(BaseState):
        pass

    class MyInlinePromptNode(InlinePromptNode):
        ml_model = "gpt-4o"
        blocks = []

    # AND a known response from invoking an inline prompt
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

    vellum_adhoc_prompt_client.adhoc_execute_prompt_stream.side_effect = generate_prompt_events

    # WHEN the node is run
    node = MyInlinePromptNode(
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

    # AND we should have made the expected call to Vellum search
    vellum_adhoc_prompt_client.adhoc_execute_prompt_stream.assert_called_once_with(
        blocks=[],
        expand_meta=Ellipsis,
        functions=None,
        input_values=[],
        input_variables=[],
        ml_model="gpt-4o",
        parameters=PromptParameters(
            stop=[],
            temperature=0.0,
            max_tokens=4096,
            top_p=1.0,
            top_k=0,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            logit_bias=None,
            custom_parameters=None,
        ),
        request_options=mock.ANY,
        settings=None,
    )


def test_inline_text_prompt_node__catch_provider_error(vellum_adhoc_prompt_client):
    """Confirm that InlineTextPromptNodes output the caught error upon Provider Error."""

    # GIVEN a node that subclasses InlineTextPromptNode
    class Inputs(BaseInputs):
        input: str

    class State(BaseState):
        pass

    @TryNode.wrap(on_error_code=WorkflowErrorCode.PROVIDER_ERROR)
    class MyInlinePromptNode(InlinePromptNode):
        ml_model = "gpt-4o"
        blocks = []

    # AND a known response from invoking an inline prompt that fails
    expected_error = VellumError(
        message="OpenAI failed",
        code="PROVIDER_ERROR",
    )

    def generate_prompt_events(*args: Any, **kwargs: Any) -> Iterator[ExecutePromptEvent]:
        execution_id = str(uuid4())
        events: List[ExecutePromptEvent] = [
            InitiatedExecutePromptEvent(execution_id=execution_id),
            RejectedExecutePromptEvent(
                execution_id=execution_id,
                error=expected_error,
            ),
        ]
        yield from events

    vellum_adhoc_prompt_client.adhoc_execute_prompt_stream.side_effect = generate_prompt_events

    # WHEN the node is run
    node = MyInlinePromptNode(
        state=State(
            meta=StateMeta(workflow_inputs=Inputs(input="Say something.")),
        )
    )
    outputs = list(node.run())

    # THEN the node should have produced the outputs we expect
    assert (
        BaseOutput(
            name="error",
            value=SdkVellumError(
                message="OpenAI failed",
                code=WorkflowErrorCode.PROVIDER_ERROR,
            ),
        )
        in outputs
    )
