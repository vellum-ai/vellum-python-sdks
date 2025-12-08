"""
Tests for JSON schema validation in InlinePromptNode during serialization.

This uses the jsonschema library to validate schemas against the JSON Schema meta-schema.
The validation is spec-compliant, meaning some schemas that might seem incomplete
(like arrays without items) are valid according to the JSON Schema specification.
"""

import pytest

import jsonschema

from vellum import PromptParameters
from vellum.workflows.nodes import InlinePromptNode


@pytest.mark.parametrize(
    "json_schema",
    [
        pytest.param(
            {"type": "object", "properties": "invalid"},
            id="object with non-dict properties",
        ),
        pytest.param(
            {"anyOf": {"type": "string"}},
            id="anyOf not list",
        ),
        pytest.param(
            {"type": "object", "properties": {"name": "string"}},
            id="object with non-schema property value",
        ),
    ],
)
def test_inline_prompt_node_validation__invalid_schemas_raise_error(
    json_schema: dict,
) -> None:
    """
    Tests that InlinePromptNode validation rejects structurally invalid JSON Schemas.
    """

    # GIVEN an InlinePromptNode configured with an invalid JSON Schema
    class MyPromptNode(InlinePromptNode):
        ml_model = "gpt-4"
        blocks = []
        parameters = PromptParameters(custom_parameters={"json_schema": json_schema})

    # WHEN we call __validate__ on the node
    # THEN it should raise a SchemaError
    with pytest.raises(jsonschema.exceptions.SchemaError):
        MyPromptNode.__validate__()


@pytest.mark.parametrize(
    "json_schema",
    [
        pytest.param(
            {"type": "array"},
            id="array without items (valid per JSON Schema spec)",
        ),
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
        pytest.param(
            {"type": "array", "items": True},
            id="array with boolean items (valid per JSON Schema spec)",
        ),
        pytest.param(
            {"anyOf": [True, {"type": "string"}]},
            id="anyOf with boolean element (valid per JSON Schema spec)",
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
