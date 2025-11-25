"""
Tests for JSON schema validation in InlinePromptNode during serialization.
"""

import pytest
from unittest import mock

from pydantic import BaseModel

from vellum import PromptParameters
from vellum.workflows.nodes import InlinePromptNode
from vellum.workflows.nodes.displayable.bases.inline_prompt_node import node as ipn


@pytest.mark.parametrize(
    "description,json_schema,expected_message",
    [
        (
            "array without items or prefixItems",
            {"type": "array"},
            "JSON Schema of type 'array' at 'parameters.custom_parameters.json_schema' must define either an 'items' "
            "field or a 'prefixItems' field to specify the type of elements in the array.",
        ),
        (
            "nested array without items",
            {
                "type": "object",
                "properties": {
                    "items": {"type": "array"},
                },
            },
            "JSON Schema of type 'array' at 'parameters.custom_parameters.json_schema.properties.items' must define "
            "either an 'items' field or a 'prefixItems' field to specify the type of elements in the array.",
        ),
        (
            "object with non-dict properties",
            {"type": "object", "properties": "invalid"},
            "JSON Schema of type 'object' at 'parameters.custom_parameters.json_schema' must have 'properties' "
            "defined as a dictionary, not str",
        ),
        (
            "anyOf not list",
            {"anyOf": {"type": "string"}},
            "JSON Schema's 'anyOf' field at 'parameters.custom_parameters.json_schema' must be a list of schemas, "
            "not dict",
        ),
        (
            "nested array in prefixItems without items",
            {
                "type": "array",
                "prefixItems": [{"type": "array"}],
            },
            "JSON Schema of type 'array' at 'parameters.custom_parameters.json_schema.prefixItems[0]' must define "
            "either an 'items' field or a 'prefixItems' field to specify the type of elements in the array.",
        ),
        (
            "nested array in list-valued items without items",
            {
                "type": "array",
                "items": [
                    {"type": "string"},
                    {"type": "array"},
                ],
            },
            "JSON Schema of type 'array' at 'parameters.custom_parameters.json_schema.items[1]' must define "
            "either an 'items' field or a 'prefixItems' field to specify the type of elements in the array.",
        ),
        (
            "wrapper with invalid inner schema",
            {
                "name": "my_schema",
                "schema": {
                    "type": "object",
                    "properties": {
                        "items": {"type": "array"},
                    },
                },
            },
            "JSON Schema of type 'array' at 'parameters.custom_parameters.json_schema.schema.properties.items' "
            "must define either an 'items' field or a 'prefixItems' field to specify the type of elements in the "
            "array.",
        ),
        (
            "real schema with schema field validates outer schema",
            {
                "type": "array",
                "schema": {"type": "string"},
            },
            "JSON Schema of type 'array' at 'parameters.custom_parameters.json_schema' must define either an 'items' "
            "field or a 'prefixItems' field to specify the type of elements in the array.",
        ),
        (
            "array with None items",
            {"type": "array", "items": None},
            "JSON Schema 'items' field at 'parameters.custom_parameters.json_schema.items' must be a schema object "
            "or a list of schema objects, not NoneType",
        ),
        (
            "array with string items",
            {"type": "array", "items": "string"},
            "JSON Schema 'items' field at 'parameters.custom_parameters.json_schema.items' must be a schema object "
            "or a list of schema objects, not str",
        ),
        (
            "array with non-list prefixItems",
            {"type": "array", "prefixItems": {"type": "string"}},
            "JSON Schema 'prefixItems' field at 'parameters.custom_parameters.json_schema.prefixItems' must be a list "
            "of schema objects, not dict",
        ),
        (
            "prefixItems with non-dict element",
            {"type": "array", "prefixItems": ["string"]},
            "JSON Schema 'prefixItems[0]' at 'parameters.custom_parameters.json_schema.prefixItems[0]' must be a "
            "schema object, not str",
        ),
        (
            "list items with non-dict element",
            {"type": "array", "items": ["string", {"type": "number"}]},
            "JSON Schema 'items[0]' at 'parameters.custom_parameters.json_schema.items[0]' must be a "
            "schema object, not str",
        ),
        (
            "anyOf with non-schema element",
            {"anyOf": ["string"]},
            "JSON Schema 'anyOf[0]' at 'parameters.custom_parameters.json_schema.anyOf[0]' must be a schema object, "
            "not str",
        ),
    ],
    ids=lambda p: p if isinstance(p, str) else None,
)
def test_inline_prompt_node_validation__invalid_schemas_raise_error(
    description: str,
    json_schema: dict,
    expected_message: str,
) -> None:
    """
    Tests that InlinePromptNode validation rejects structurally invalid JSON Schemas with clear error messages.
    """

    # GIVEN an InlinePromptNode configured with a specific invalid JSON Schema scenario
    class MyPromptNode(InlinePromptNode):
        ml_model = "gpt-4"
        blocks = []
        parameters = PromptParameters(custom_parameters={"json_schema": json_schema})

    # WHEN we call __validate__ on the node
    with pytest.raises(ValueError) as exc_info:
        MyPromptNode.__validate__()

    # THEN the error message should match the expected validation error
    assert str(exc_info.value) == expected_message


@pytest.mark.parametrize(
    "description,json_schema",
    [
        (
            "array with prefixItems only",
            {
                "type": "array",
                "prefixItems": [{"type": "string"}, {"type": "number"}],
            },
        ),
        (
            "valid array with items",
            {"type": "array", "items": {"type": "string"}},
        ),
        (
            "array with empty items object",
            {"type": "array", "items": {}},
        ),
        (
            "array with empty prefixItems",
            {"type": "array", "prefixItems": []},
        ),
        (
            "array with both items and prefixItems",
            {
                "type": "array",
                "prefixItems": [{"type": "string"}],
                "items": {"type": "number"},
            },
        ),
        (
            "valid nested array in prefixItems",
            {
                "type": "array",
                "prefixItems": [{"type": "array", "items": {"type": "string"}}],
            },
        ),
        (
            "valid nested array in list-valued items",
            {
                "type": "array",
                "items": [
                    {"type": "string"},
                    {"type": "array", "items": {"type": "number"}},
                ],
            },
        ),
        (
            "valid complex object schema with anyOf",
            {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "age": {"type": "number"},
                    "tags": {"type": "array", "items": {"type": "string"}},
                    "address": {
                        "type": "object",
                        "properties": {
                            "street": {"type": "string"},
                            "city": {"type": "string"},
                        },
                    },
                },
                "anyOf": [{"required": ["name"]}, {"required": ["age"]}],
            },
        ),
        (
            "wrapper with valid inner schema",
            {
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
            },
        ),
    ],
    ids=lambda p: p if isinstance(p, str) else None,
)
def test_inline_prompt_node_validation__valid_schemas_succeed(
    description: str,
    json_schema: dict,
) -> None:
    """
    Tests that InlinePromptNode validation accepts structurally valid JSON Schemas.
    """

    # GIVEN an InlinePromptNode configured with a specific valid JSON Schema scenario
    class MyPromptNode(InlinePromptNode):
        ml_model = "gpt-4"
        blocks = []
        parameters = PromptParameters(custom_parameters={"json_schema": json_schema})

    # WHEN we call __validate__ on the node
    try:
        MyPromptNode.__validate__()
    # THEN it should not raise an error for valid schemas
    except ValueError as e:
        pytest.fail(f"Validation should not raise an error for valid schema ({description}): {e}")


def test_inline_prompt_node_validation__no_json_schema__succeeds():
    """
    Tests that InlinePromptNode without json_schema passes validation.
    """

    # GIVEN an InlinePromptNode that has no json_schema
    class MyPromptNode(InlinePromptNode):
        ml_model = "gpt-4"
        blocks = []

    # WHEN we call __validate__() on the node
    try:
        MyPromptNode.__validate__()
    # THEN it should not raise any errors
    except ValueError as e:
        pytest.fail(f"Validation should not raise an error when no json_schema is present: {e}")


def test_inline_prompt_node_validation__pydantic_model_schema_is_validated():
    """
    Tests that Pydantic model-based json_schema values are normalized and validated.
    """

    # GIVEN a Pydantic model for the schema
    class TestPydanticModel(BaseModel):
        result: str

    # AND an InlinePromptNode with a Pydantic model as the schema
    class MyPromptNode(InlinePromptNode):
        ml_model = "gpt-4"
        blocks = []
        parameters = PromptParameters(
            custom_parameters={
                "json_schema": {
                    "name": "get_result_pydantic",
                    "schema": TestPydanticModel,
                }
            }
        )

    # AND we mock normalize_json to return an invalid array schema (missing items/prefixItems)
    original_normalize_json = ipn.normalize_json

    def fake_normalize_json(value: object) -> object:
        if isinstance(value, dict):
            normalized = {k: fake_normalize_json(v) for k, v in value.items()}
            return normalized
        if value is TestPydanticModel:
            return {"type": "array"}
        return original_normalize_json(value)

    # WHEN we call __validate__() on the node with the mocked normalize_json
    # THEN it should raise a ValueError because the normalized schema is invalid
    with mock.patch.object(ipn, "normalize_json", side_effect=fake_normalize_json):
        with pytest.raises(ValueError) as exc_info:
            MyPromptNode.__validate__()

    # AND the error message should indicate the array is missing items/prefixItems
    assert "must define either an 'items' field or a 'prefixItems' field" in str(exc_info.value)
