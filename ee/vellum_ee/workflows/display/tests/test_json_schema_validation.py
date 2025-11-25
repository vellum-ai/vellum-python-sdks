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
    "json_schema,expected_message",
    [
        pytest.param(
            {"type": "array"},
            "JSON Schema of type 'array' at 'parameters.custom_parameters.json_schema' must define either an 'items' "
            "field or a 'prefixItems' field to specify the type of elements in the array.",
            id="array without items or prefixItems",
        ),
        pytest.param(
            {
                "type": "object",
                "properties": {
                    "items": {"type": "array"},
                },
            },
            "JSON Schema of type 'array' at 'parameters.custom_parameters.json_schema.properties.items' must define "
            "either an 'items' field or a 'prefixItems' field to specify the type of elements in the array.",
            id="nested array without items",
        ),
        pytest.param(
            {"type": "object", "properties": "invalid"},
            "JSON Schema of type 'object' at 'parameters.custom_parameters.json_schema' must have 'properties' "
            "defined as a dictionary, not str",
            id="object with non-dict properties",
        ),
        pytest.param(
            {"anyOf": {"type": "string"}},
            "JSON Schema's 'anyOf' field at 'parameters.custom_parameters.json_schema' must be a list of schemas, "
            "not dict",
            id="anyOf not list",
        ),
        pytest.param(
            {
                "type": "array",
                "prefixItems": [{"type": "array"}],
            },
            "JSON Schema of type 'array' at 'parameters.custom_parameters.json_schema.prefixItems[0]' must define "
            "either an 'items' field or a 'prefixItems' field to specify the type of elements in the array.",
            id="nested array in prefixItems without items",
        ),
        pytest.param(
            {
                "type": "array",
                "items": [
                    {"type": "string"},
                    {"type": "array"},
                ],
            },
            "JSON Schema of type 'array' at 'parameters.custom_parameters.json_schema.items[1]' must define "
            "either an 'items' field or a 'prefixItems' field to specify the type of elements in the array.",
            id="nested array in list-valued items without items",
        ),
        pytest.param(
            {
                "type": "array",
                "schema": {"type": "string"},
            },
            "JSON Schema of type 'array' at 'parameters.custom_parameters.json_schema' must define either an 'items' "
            "field or a 'prefixItems' field to specify the type of elements in the array.",
            id="schema with schema field validates outer schema",
        ),
        pytest.param(
            {"type": "array", "items": None},
            "JSON Schema 'items' field at 'parameters.custom_parameters.json_schema.items' must be a schema object "
            "or a list of schema objects, not NoneType",
            id="array with None items",
        ),
        pytest.param(
            {"type": "array", "items": "string"},
            "JSON Schema 'items' field at 'parameters.custom_parameters.json_schema.items' must be a schema object "
            "or a list of schema objects, not str",
            id="array with string items",
        ),
        pytest.param(
            {"type": "array", "prefixItems": {"type": "string"}},
            "JSON Schema 'prefixItems' field at 'parameters.custom_parameters.json_schema.prefixItems' must be a list "
            "of schema objects, not dict",
            id="array with non-list prefixItems",
        ),
        pytest.param(
            {"type": "array", "prefixItems": ["string"]},
            "JSON Schema 'prefixItems[0]' at 'parameters.custom_parameters.json_schema.prefixItems[0]' must be a "
            "schema object, not str",
            id="prefixItems with non-dict element",
        ),
        pytest.param(
            {"type": "array", "items": ["string", {"type": "number"}]},
            "JSON Schema 'items[0]' at 'parameters.custom_parameters.json_schema.items[0]' must be a "
            "schema object, not str",
            id="list items with non-dict element",
        ),
        pytest.param(
            {"anyOf": ["string"]},
            "JSON Schema 'anyOf[0]' at 'parameters.custom_parameters.json_schema.anyOf[0]' must be a schema object, "
            "not str",
            id="anyOf with non-schema element",
        ),
        pytest.param(
            {"name": "test", "schema": {"type": "array"}},
            "JSON Schema of type 'array' at 'parameters.custom_parameters.json_schema.schema' must define either an "
            "'items' field or a 'prefixItems' field to specify the type of elements in the array.",
            id="wrapper with invalid nested array schema",
        ),
        pytest.param(
            {"name": "test", "schema": "string"},
            "JSON Schema 'schema' field at 'parameters.custom_parameters.json_schema.schema' must be a schema object, "
            "not str",
            id="wrapper with non-dict schema value",
        ),
        pytest.param(
            {"type": "object", "properties": {"name": "string"}},
            "JSON Schema property 'name' at 'parameters.custom_parameters.json_schema.properties.name' must be a "
            "schema object, not str",
            id="object with non-schema property value",
        ),
    ],
)
def test_inline_prompt_node_validation__invalid_schemas_raise_error(
    json_schema: dict,
    expected_message: str,
) -> None:
    """
    Tests that InlinePromptNode validation rejects structurally invalid JSON Schemas with clear error messages.
    """

    # GIVEN an InlinePromptNode configured with an invalid JSON Schema
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
    "json_schema",
    [
        pytest.param(
            {
                "type": "array",
                "prefixItems": [{"type": "string"}, {"type": "number"}],
            },
            id="array with prefixItems only",
        ),
        pytest.param(
            {"type": "array", "items": {"type": "string"}},
            id="valid array with items",
        ),
        pytest.param(
            {"type": "array", "items": {}},
            id="array with empty items object",
        ),
        pytest.param(
            {"type": "array", "prefixItems": []},
            id="array with empty prefixItems",
        ),
        pytest.param(
            {
                "type": "array",
                "prefixItems": [{"type": "string"}],
                "items": {"type": "number"},
            },
            id="array with both items and prefixItems",
        ),
        pytest.param(
            {
                "type": "array",
                "prefixItems": [{"type": "array", "items": {"type": "string"}}],
            },
            id="valid nested array in prefixItems",
        ),
        pytest.param(
            {
                "type": "array",
                "items": [
                    {"type": "string"},
                    {"type": "array", "items": {"type": "number"}},
                ],
            },
            id="valid nested array in list-valued items",
        ),
        pytest.param(
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
            id="valid complex object schema with anyOf",
        ),
        pytest.param(
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
            id="wrapper with valid nested schema",
        ),
    ],
)
def test_inline_prompt_node_validation__valid_schemas_succeed(
    json_schema: dict,
) -> None:
    """
    Tests that InlinePromptNode validation accepts structurally valid JSON Schemas.
    """

    # GIVEN an InlinePromptNode configured with a valid JSON Schema
    class MyPromptNode(InlinePromptNode):
        ml_model = "gpt-4"
        blocks = []
        parameters = PromptParameters(custom_parameters={"json_schema": json_schema})

    # WHEN we call __validate__ on the node
    # THEN it should not raise an error
    MyPromptNode.__validate__()


def test_inline_prompt_node_validation__no_json_schema__succeeds():
    """
    Tests that InlinePromptNode without json_schema passes validation.
    """

    # GIVEN an InlinePromptNode that has no json_schema
    class MyPromptNode(InlinePromptNode):
        ml_model = "gpt-4"
        blocks = []

    # WHEN we call __validate__() on the node
    # THEN it should not raise any errors
    MyPromptNode.__validate__()


def test_inline_prompt_node_validation__pydantic_model_schema_is_validated():
    """
    Tests that Pydantic model-based json_schema values are normalized and validated.
    """

    # GIVEN a Pydantic model for the schema
    class TestPydanticModel(BaseModel):
        result: str

    # AND an InlinePromptNode with a Pydantic model as the json_schema
    class MyPromptNode(InlinePromptNode):
        ml_model = "gpt-4"
        blocks = []
        parameters = PromptParameters(
            custom_parameters={
                "json_schema": TestPydanticModel,
            }
        )

    # AND we mock normalize_json to return an invalid array schema (missing items/prefixItems)
    original_normalize_json = ipn.normalize_json

    def fake_normalize_json(value: object) -> object:
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
