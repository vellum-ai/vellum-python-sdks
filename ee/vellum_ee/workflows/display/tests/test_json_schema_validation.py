"""
Tests for JSON schema validation in InlinePromptNode during serialization.
"""

import pytest

from vellum import PromptParameters
from vellum.workflows.nodes import InlinePromptNode


def test_inline_prompt_node_validation__array_without_items__raises_error():
    """
    Tests that InlinePromptNode validation catches array schemas missing 'items' field.
    """

    # GIVEN an InlinePromptNode that has an invalid array schema (missing 'items')
    class MyPromptNode(InlinePromptNode):
        ml_model = "gpt-4"
        blocks = []
        parameters = PromptParameters(
            custom_parameters={
                "json_schema": {
                    "type": "array",
                    # Missing 'items' field - this should trigger validation error
                }
            }
        )

    # WHEN we call __validate__() on the node
    # THEN it should raise a ValueError with a clear message
    with pytest.raises(ValueError) as exc_info:
        MyPromptNode.__validate__()

    # AND the error message should be clear and actionable
    error_message = str(exc_info.value)
    assert "array" in error_message.lower()
    assert "items" in error_message.lower()
    assert "parameters.custom_parameters.json_schema" in error_message


def test_inline_prompt_node_validation__nested_array_without_items__raises_error():
    """
    Tests that validation catches nested array schemas missing 'items' field.
    """

    # GIVEN an InlinePromptNode that has a nested invalid array schema
    class MyPromptNode(InlinePromptNode):
        ml_model = "gpt-4"
        blocks = []
        parameters = PromptParameters(
            custom_parameters={
                "json_schema": {
                    "type": "object",
                    "properties": {
                        "items": {
                            "type": "array",
                            # Missing 'items' field in nested array
                        }
                    },
                }
            }
        )

    # WHEN we call __validate__() on the node
    # THEN it should raise a ValueError with a clear message
    with pytest.raises(ValueError) as exc_info:
        MyPromptNode.__validate__()

    # AND the error message should indicate the nested path
    error_message = str(exc_info.value)
    assert "array" in error_message.lower()
    assert "items" in error_message.lower()
    assert "properties.items" in error_message


def test_inline_prompt_node_validation__array_with_prefix_items__succeeds():
    """
    Tests that array schemas with prefixItems (but no items) are valid.
    """

    # GIVEN an InlinePromptNode that has an array schema with prefixItems
    class MyPromptNode(InlinePromptNode):
        ml_model = "gpt-4"
        blocks = []
        parameters = PromptParameters(
            custom_parameters={
                "json_schema": {
                    "type": "array",
                    "prefixItems": [{"type": "string"}, {"type": "number"}],
                    # No 'items' field, but prefixItems is present - this is valid
                }
            }
        )

    # WHEN we call __validate__() on the node
    # THEN it should not raise any errors
    try:
        MyPromptNode.__validate__()
    except ValueError:
        pytest.fail("Validation should not raise an error for array with prefixItems")


def test_inline_prompt_node_validation__valid_array_with_items__succeeds():
    """
    Tests that valid array schemas with 'items' field pass validation.
    """

    # GIVEN an InlinePromptNode that has a valid array schema
    class MyPromptNode(InlinePromptNode):
        ml_model = "gpt-4"
        blocks = []
        parameters = PromptParameters(custom_parameters={"json_schema": {"type": "array", "items": {"type": "string"}}})

    # WHEN we call __validate__() on the node
    # THEN it should not raise any errors
    try:
        MyPromptNode.__validate__()
    except ValueError:
        pytest.fail("Validation should not raise an error for valid array schema")


def test_inline_prompt_node_validation__object_with_invalid_properties__raises_error():
    """
    Tests that object schemas with invalid 'properties' field are caught.
    """

    # GIVEN an InlinePromptNode that has an object schema with invalid properties
    class MyPromptNode(InlinePromptNode):
        ml_model = "gpt-4"
        blocks = []
        parameters = PromptParameters(
            custom_parameters={
                "json_schema": {"type": "object", "properties": "invalid"}  # Should be a dict, not a string
            }
        )

    # WHEN we call __validate__() on the node
    # THEN it should raise a ValueError with a clear message
    with pytest.raises(ValueError) as exc_info:
        MyPromptNode.__validate__()

    # AND the error message should mention properties
    error_message = str(exc_info.value)
    assert "object" in error_message.lower()
    assert "properties" in error_message.lower()


def test_inline_prompt_node_validation__anyof_not_list__raises_error():
    """
    Tests that composition keywords (anyOf, oneOf, allOf) must be lists.
    """

    # GIVEN an InlinePromptNode that has anyOf as non-list
    class MyPromptNode(InlinePromptNode):
        ml_model = "gpt-4"
        blocks = []
        parameters = PromptParameters(
            custom_parameters={"json_schema": {"anyOf": {"type": "string"}}}  # Should be a list, not a dict
        )

    # WHEN we call __validate__() on the node
    # THEN it should raise a ValueError with a clear message
    with pytest.raises(ValueError) as exc_info:
        MyPromptNode.__validate__()

    # AND the error message should mention anyOf
    error_message = str(exc_info.value)
    assert "anyof" in error_message.lower()
    assert "list" in error_message.lower()


def test_inline_prompt_node_validation__valid_complex_schema__succeeds():
    """
    Tests that a complex valid schema passes validation.
    """

    # GIVEN an InlinePromptNode that has a complex valid schema
    class MyPromptNode(InlinePromptNode):
        ml_model = "gpt-4"
        blocks = []
        parameters = PromptParameters(
            custom_parameters={
                "json_schema": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "age": {"type": "number"},
                        "tags": {"type": "array", "items": {"type": "string"}},
                        "address": {
                            "type": "object",
                            "properties": {"street": {"type": "string"}, "city": {"type": "string"}},
                        },
                    },
                    "anyOf": [{"required": ["name"]}, {"required": ["age"]}],
                }
            }
        )

    # WHEN we call __validate__() on the node
    # THEN it should not raise any errors
    try:
        MyPromptNode.__validate__()
    except ValueError:
        pytest.fail("Validation should not raise an error for valid complex schema")


def test_inline_prompt_node_validation__no_json_schema__succeeds():
    """
    Tests that InlinePromptNode without json_schema passes validation.
    """

    # GIVEN an InlinePromptNode that has no json_schema
    class MyPromptNode(InlinePromptNode):
        ml_model = "gpt-4"
        blocks = []
        # No custom_parameters with json_schema

    # WHEN we call __validate__() on the node
    # THEN it should not raise any errors
    try:
        MyPromptNode.__validate__()
    except ValueError:
        pytest.fail("Validation should not raise an error when no json_schema is present")
