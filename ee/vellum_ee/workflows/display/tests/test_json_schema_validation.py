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


def test_inline_prompt_node_validation__array_with_empty_items__succeeds():
    """
    Tests that array schemas with empty items object are valid (unconstrained elements).
    """

    # GIVEN an InlinePromptNode with an array schema where items is an empty object
    class MyPromptNode(InlinePromptNode):
        ml_model = "gpt-4"
        blocks = []
        parameters = PromptParameters(
            custom_parameters={
                "json_schema": {
                    "type": "array",
                    "items": {},  # Empty schema means unconstrained elements
                }
            }
        )

    # WHEN we call __validate__() on the node
    # THEN it should not raise any errors
    try:
        MyPromptNode.__validate__()
    except ValueError:
        pytest.fail("Validation should not raise an error for array with empty items object")


def test_inline_prompt_node_validation__array_with_empty_prefix_items__succeeds():
    """
    Tests that array schemas with empty prefixItems array are valid.
    """

    # GIVEN an InlinePromptNode with an array schema where prefixItems is an empty array
    class MyPromptNode(InlinePromptNode):
        ml_model = "gpt-4"
        blocks = []
        parameters = PromptParameters(
            custom_parameters={
                "json_schema": {
                    "type": "array",
                    "prefixItems": [],  # Empty array is valid
                }
            }
        )

    # WHEN we call __validate__() on the node
    # THEN it should not raise any errors
    try:
        MyPromptNode.__validate__()
    except ValueError:
        pytest.fail("Validation should not raise an error for array with empty prefixItems array")


def test_inline_prompt_node_validation__array_with_both_items_and_prefix_items__succeeds():
    """
    Tests that array schemas with both items and prefixItems are valid.
    """

    # GIVEN an InlinePromptNode with an array schema that has both items and prefixItems
    class MyPromptNode(InlinePromptNode):
        ml_model = "gpt-4"
        blocks = []
        parameters = PromptParameters(
            custom_parameters={
                "json_schema": {
                    "type": "array",
                    "prefixItems": [{"type": "string"}],
                    "items": {"type": "number"},  # Additional items after prefix
                }
            }
        )

    # WHEN we call __validate__() on the node
    # THEN it should not raise any errors
    try:
        MyPromptNode.__validate__()
    except ValueError:
        pytest.fail("Validation should not raise an error for array with both items and prefixItems")


def test_inline_prompt_node_validation__nested_array_in_prefix_items__raises_error():
    """
    Tests that nested arrays in prefixItems without items/prefixItems are caught.
    """

    # GIVEN an InlinePromptNode with a nested array in prefixItems missing items
    class MyPromptNode(InlinePromptNode):
        ml_model = "gpt-4"
        blocks = []
        parameters = PromptParameters(
            custom_parameters={
                "json_schema": {
                    "type": "array",
                    "prefixItems": [{"type": "array"}],  # Missing items/prefixItems
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
    assert "prefixItems[0]" in error_message


def test_inline_prompt_node_validation__nested_array_in_list_items__raises_error():
    """
    Tests that nested arrays in list-valued items without items/prefixItems are caught.
    """

    # GIVEN an InlinePromptNode with a nested array in list-valued items
    class MyPromptNode(InlinePromptNode):
        ml_model = "gpt-4"
        blocks = []
        parameters = PromptParameters(
            custom_parameters={
                "json_schema": {
                    "type": "array",
                    "items": [
                        {"type": "string"},
                        {"type": "array"},  # Missing items/prefixItems
                    ],
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
    assert "items[1]" in error_message


def test_inline_prompt_node_validation__valid_nested_array_in_prefix_items__succeeds():
    """
    Tests that valid nested arrays in prefixItems with proper items pass validation.
    """

    # GIVEN an InlinePromptNode with a valid nested array in prefixItems
    class MyPromptNode(InlinePromptNode):
        ml_model = "gpt-4"
        blocks = []
        parameters = PromptParameters(
            custom_parameters={
                "json_schema": {
                    "type": "array",
                    "prefixItems": [{"type": "array", "items": {"type": "string"}}],  # Valid nested array
                }
            }
        )

    # WHEN we call __validate__() on the node
    # THEN it should not raise any errors
    try:
        MyPromptNode.__validate__()
    except ValueError:
        pytest.fail("Validation should not raise an error for valid nested array in prefixItems")


def test_inline_prompt_node_validation__valid_nested_array_in_list_items__succeeds():
    """
    Tests that valid nested arrays in list-valued items with proper items pass validation.
    """

    # GIVEN an InlinePromptNode with a valid nested array in list-valued items
    class MyPromptNode(InlinePromptNode):
        ml_model = "gpt-4"
        blocks = []
        parameters = PromptParameters(
            custom_parameters={
                "json_schema": {
                    "type": "array",
                    "items": [
                        {"type": "string"},
                        {"type": "array", "items": {"type": "number"}},  # Valid nested array
                    ],
                }
            }
        )

    # WHEN we call __validate__() on the node
    # THEN it should not raise any errors
    try:
        MyPromptNode.__validate__()
    except ValueError:
        pytest.fail("Validation should not raise an error for valid nested array in list items")


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


def test_inline_prompt_node_validation__wrapper_with_invalid_inner_schema__raises_error():
    """
    Tests that validation drills into the nested schema field for standard structured-output format.
    """

    # GIVEN an InlinePromptNode with a json_schema wrapper containing an invalid inner schema
    class MyPromptNode(InlinePromptNode):
        ml_model = "gpt-4"
        blocks = []
        parameters = PromptParameters(
            custom_parameters={
                "json_schema": {
                    "name": "my_schema",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "items": {
                                "type": "array",
                                # Missing 'items' field - this should trigger validation error
                            }
                        },
                    },
                }
            }
        )

    # WHEN we call __validate__() on the node
    # THEN it should raise a ValueError with a clear message
    with pytest.raises(ValueError) as exc_info:
        MyPromptNode.__validate__()

    # AND the error message should indicate the nested path including .schema
    error_message = str(exc_info.value)
    assert "array" in error_message.lower()
    assert "items" in error_message.lower()
    assert "json_schema.schema" in error_message


def test_inline_prompt_node_validation__wrapper_with_valid_inner_schema__succeeds():
    """
    Tests that validation passes for valid schemas in the standard structured-output wrapper format.
    """

    # GIVEN an InlinePromptNode with a json_schema wrapper containing a valid inner schema
    class MyPromptNode(InlinePromptNode):
        ml_model = "gpt-4"
        blocks = []
        parameters = PromptParameters(
            custom_parameters={
                "json_schema": {
                    "name": "match_scorer_schema",
                    "schema": {
                        "type": "object",
                        "title": "MatchScorerSchema",
                        "required": ["recommendation", "score", "remarks"],
                        "properties": {
                            "score": {
                                "type": "integer",
                                "title": "Match Score",
                                "description": "Match score out of 10",
                            },
                            "remarks": {
                                "type": "string",
                                "title": "Remarks",
                            },
                            "recommendation": {
                                "enum": ["Advance", "Defer", "Reject"],
                                "type": "string",
                                "title": "Status",
                            },
                        },
                    },
                }
            }
        )

    # WHEN we call __validate__() on the node
    # THEN it should not raise any errors
    try:
        MyPromptNode.__validate__()
    except ValueError:
        pytest.fail("Validation should not raise an error for valid wrapper schema")
