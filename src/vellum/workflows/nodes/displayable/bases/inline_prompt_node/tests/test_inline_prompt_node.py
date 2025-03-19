import pytest
import json
from unittest import mock
from uuid import uuid4
from typing import Any, Iterator, List

from vellum import (
    ChatMessagePromptBlock,
    JinjaPromptBlock,
    PlainTextPromptBlock,
    PromptBlock,
    PromptParameters,
    RichTextPromptBlock,
    VariablePromptBlock,
)
from vellum.client.types.execute_prompt_event import ExecutePromptEvent
from vellum.client.types.fulfilled_execute_prompt_event import FulfilledExecutePromptEvent
from vellum.client.types.initiated_execute_prompt_event import InitiatedExecutePromptEvent
from vellum.client.types.prompt_output import PromptOutput
from vellum.client.types.prompt_request_string_input import PromptRequestStringInput
from vellum.client.types.string_vellum_value import StringVellumValue
from vellum.workflows.errors import WorkflowErrorCode
from vellum.workflows.exceptions import NodeException
from vellum.workflows.inputs import BaseInputs
from vellum.workflows.nodes import InlinePromptNode
from vellum.workflows.nodes.displayable.bases.inline_prompt_node import BaseInlinePromptNode
from vellum.workflows.state import BaseState
from vellum.workflows.state.base import StateMeta


def test_validation_with_missing_variables():
    """Test that validation correctly identifies missing variables."""
    test_blocks: List[PromptBlock] = [
        VariablePromptBlock(input_variable="required_var1"),
        VariablePromptBlock(input_variable="required_var2"),
        RichTextPromptBlock(
            blocks=[
                PlainTextPromptBlock(text="Some text"),
                VariablePromptBlock(input_variable="required_var3"),
            ],
        ),
        JinjaPromptBlock(template="Template without variables"),
        ChatMessagePromptBlock(
            chat_role="USER",
            blocks=[
                RichTextPromptBlock(
                    blocks=[
                        PlainTextPromptBlock(text="Nested text"),
                        VariablePromptBlock(input_variable="required_var4"),
                    ],
                ),
            ],
        ),
    ]

    # GIVEN a BaseInlinePromptNode
    class TestNode(BaseInlinePromptNode):
        ml_model = "test-model"
        blocks = test_blocks
        prompt_inputs = {
            "required_var1": "value1",
            # required_var2 is missing
            # required_var3 is missing
            # required_var4 is missing
        }

    # WHEN the node is run
    node = TestNode()
    with pytest.raises(NodeException) as excinfo:
        list(node.run())

    # THEN the node raises the correct NodeException
    assert excinfo.value.code == WorkflowErrorCode.INVALID_INPUTS
    assert "required_var2" in str(excinfo.value)
    assert "required_var3" in str(excinfo.value)
    assert "required_var4" in str(excinfo.value)


def test_validation_with_all_variables_provided(vellum_adhoc_prompt_client):
    """Test that validation passes when all variables are provided."""
    test_blocks: List[PromptBlock] = [
        VariablePromptBlock(input_variable="required_var1"),
        VariablePromptBlock(input_variable="required_var2"),
        RichTextPromptBlock(
            blocks=[
                PlainTextPromptBlock(text="Some text"),
                VariablePromptBlock(input_variable="required_var3"),
            ],
        ),
        JinjaPromptBlock(template="Template without variables"),
        ChatMessagePromptBlock(
            chat_role="USER",
            blocks=[
                RichTextPromptBlock(
                    blocks=[
                        PlainTextPromptBlock(text="Nested text"),
                        VariablePromptBlock(input_variable="required_var4"),
                    ],
                ),
            ],
        ),
    ]

    # GIVEN a BaseInlinePromptNode
    class TestNode(BaseInlinePromptNode):
        ml_model = "test-model"
        blocks = test_blocks
        prompt_inputs = {
            "required_var1": "value1",
            "required_var2": "value2",
            "required_var3": "value3",
            "required_var4": "value4",
        }

    expected_outputs: List[PromptOutput] = [
        StringVellumValue(value="Test response"),
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
    node = TestNode()
    list(node.run())

    # THEN the prompt is executed with the correct inputs
    mock_api = vellum_adhoc_prompt_client.adhoc_execute_prompt_stream
    assert mock_api.call_count == 1
    assert mock_api.call_args.kwargs["input_values"] == [
        PromptRequestStringInput(key="required_var1", type="STRING", value="value1"),
        PromptRequestStringInput(key="required_var2", type="STRING", value="value2"),
        PromptRequestStringInput(key="required_var3", type="STRING", value="value3"),
        PromptRequestStringInput(key="required_var4", type="STRING", value="value4"),
    ]


def test_validation_with_extra_variables(vellum_adhoc_prompt_client):
    """Test that validation passes when extra variables are provided."""
    test_blocks: List[PromptBlock] = [
        VariablePromptBlock(input_variable="required_var"),
    ]

    # GIVEN a BaseInlinePromptNode
    class TestNode(BaseInlinePromptNode):
        ml_model = "test-model"
        blocks = test_blocks
        prompt_inputs = {
            "required_var": "value",
            "extra_var": "extra_value",  # This is not required
        }

    expected_outputs: List[PromptOutput] = [
        StringVellumValue(value="Test response"),
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
    node = TestNode()
    list(node.run())

    # THEN the prompt is executed with the correct inputs
    mock_api = vellum_adhoc_prompt_client.adhoc_execute_prompt_stream
    assert mock_api.call_count == 1
    assert mock_api.call_args.kwargs["input_values"] == [
        PromptRequestStringInput(key="required_var", type="STRING", value="value"),
        PromptRequestStringInput(key="extra_var", type="STRING", value="extra_value"),
    ]


def test_inline_prompt_node__json_output(vellum_adhoc_prompt_client):
    """Confirm that InlinePromptNodes output the expected JSON when run."""

    # GIVEN a node that subclasses InlinePromptNode
    class Inputs(BaseInputs):
        input: str

    class State(BaseState):
        pass

    class MyInlinePromptNode(InlinePromptNode):
        ml_model = "gpt-4o"
        blocks = []
        parameters = PromptParameters(
            stop=[],
            temperature=0.0,
            max_tokens=4096,
            top_p=1.0,
            top_k=0,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            logit_bias=None,
            custom_parameters={
                "json_mode": False,
                "json_schema": {
                    "name": "get_result",
                    "schema": {
                        "type": "object",
                        "required": ["result"],
                        "properties": {"result": {"type": "string", "description": ""}},
                    },
                },
            },
        )

    # AND a known JSON response from invoking an inline prompt
    expected_json = {"result": "Hello, world!"}
    expected_outputs: List[PromptOutput] = [
        StringVellumValue(value=json.dumps(expected_json)),
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
            meta=StateMeta(workflow_inputs=Inputs(input="Generate JSON.")),
        )
    )
    outputs = [o for o in node.run()]

    # THEN the node should have produced the outputs we expect
    results_output = outputs[0]
    assert results_output.name == "results"
    assert results_output.value == expected_outputs

    text_output = outputs[1]
    assert text_output.name == "text"
    assert text_output.value == '{"result": "Hello, world!"}'

    json_output = outputs[2]
    assert json_output.name == "json"
    assert json_output.value == expected_json

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
            custom_parameters={
                "json_mode": False,
                "json_schema": {
                    "name": "get_result",
                    "schema": {
                        "type": "object",
                        "required": ["result"],
                        "properties": {"result": {"type": "string", "description": ""}},
                    },
                },
            },
        ),
        request_options=mock.ANY,
        settings=None,
    )
