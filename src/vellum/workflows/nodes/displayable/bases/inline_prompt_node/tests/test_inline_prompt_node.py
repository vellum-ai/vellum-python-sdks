import pytest
from typing import List

from vellum import (
    ChatMessagePromptBlock,
    JinjaPromptBlock,
    PlainTextPromptBlock,
    PromptBlock,
    RichTextPromptBlock,
    VariablePromptBlock,
)
from vellum.workflows.errors import WorkflowErrorCode
from vellum.workflows.exceptions import NodeException
from vellum.workflows.nodes.displayable.bases.inline_prompt_node import BaseInlinePromptNode


def test_extract_required_input_variables_with_various_block_types():
    """Test that _extract_required_input_variables correctly identifies variables from different block types."""
    test_blocks: List[PromptBlock] = [
        VariablePromptBlock(input_variable="var1"),
        ChatMessagePromptBlock(
            chat_role="SYSTEM",
            blocks=[
                VariablePromptBlock(input_variable="var2"),
            ],
        ),
        RichTextPromptBlock(
            blocks=[
                PlainTextPromptBlock(text="Some text"),
                VariablePromptBlock(input_variable="var3"),
            ],
        ),
        JinjaPromptBlock(template="Template without variables"),
        ChatMessagePromptBlock(
            chat_role="USER",
            blocks=[
                RichTextPromptBlock(
                    blocks=[
                        PlainTextPromptBlock(text="Nested text"),
                        VariablePromptBlock(input_variable="var4"),
                    ],
                ),
            ],
        ),
    ]

    # GIVEN a BaseInlinePromptNode
    class TestNode(BaseInlinePromptNode):
        ml_model = "test-model"
        blocks = test_blocks
        prompt_inputs = {}

    # WHEN the _extract_required_input_variables method is called
    node = TestNode()
    required_vars = node._extract_required_input_variables(test_blocks)

    # THEN all variables were found
    assert required_vars == {"var1", "var2", "var3", "var4"}


def test_validation_with_missing_variables():
    """Test that validation correctly identifies missing variables."""
    test_blocks: List[PromptBlock] = [
        VariablePromptBlock(input_variable="required_var1"),
        VariablePromptBlock(input_variable="required_var2"),
        VariablePromptBlock(input_variable="required_var3"),
    ]

    # GIVEN a BaseInlinePromptNode
    class TestNode(BaseInlinePromptNode):
        ml_model = "test-model"
        blocks = test_blocks
        prompt_inputs = {
            "required_var1": "value1",
            # required_var2 is missing
            # required_var3 is missing
        }

    # WHEN the _validate method is called
    node = TestNode()

    # THEN it should raise an exception
    with pytest.raises(NodeException) as excinfo:
        node._validate()

    # THEN the exception details should be as expected
    assert excinfo.value.code == WorkflowErrorCode.INVALID_INPUTS
    assert "required_var2" in str(excinfo.value)
    assert "required_var3" in str(excinfo.value)


def test_validation_with_all_variables_provided():
    """Test that validation passes when all variables are provided."""
    test_blocks: List[PromptBlock] = [
        VariablePromptBlock(input_variable="required_var1"),
        VariablePromptBlock(input_variable="required_var2"),
    ]

    # GIVEN a BaseInlinePromptNode
    class TestNode(BaseInlinePromptNode):
        ml_model = "test-model"
        blocks = test_blocks
        prompt_inputs = {
            "required_var1": "value1",
            "required_var2": "value2",
        }

    # WHEN the _validate method is called
    node = TestNode()

    # THEN it should not raise an exception
    node._validate()  # This should not raise


def test_validation_with_extra_variables():
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

    # WHEN the _validate method is called
    node = TestNode()

    # THEN it should not raise an exception
    node._validate()


def test_validation_with_empty_blocks():
    """Test that validation handles empty blocks list."""

    # GIVEN a BaseInlinePromptNode
    class TestNode(BaseInlinePromptNode):
        ml_model = "test-model"
        blocks = []  # Empty blocks
        prompt_inputs = {}

    node = TestNode()

    # WHEN the _extract_required_input_variables method is called
    required_vars = node._extract_required_input_variables([])

    # THEN no variables should be found
    assert required_vars == set()
