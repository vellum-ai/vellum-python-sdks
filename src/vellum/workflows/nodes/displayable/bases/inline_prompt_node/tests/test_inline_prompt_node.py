import pytest
from uuid import uuid4
from typing import Any, Iterator, List

from vellum import (
    ChatMessagePromptBlock,
    JinjaPromptBlock,
    PlainTextPromptBlock,
    PromptBlock,
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
from vellum.workflows.nodes.displayable.bases.inline_prompt_node import BaseInlinePromptNode


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
