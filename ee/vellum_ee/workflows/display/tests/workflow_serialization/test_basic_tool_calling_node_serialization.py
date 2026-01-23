from deepdiff import DeepDiff

from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display

from tests.workflows.basic_tool_calling_node.workflow import BasicToolCallingNodeWorkflow


def test_serialize_workflow():
    # GIVEN a Workflow that uses a generic node
    # WHEN we serialize it
    workflow_display = get_workflow_display(workflow_class=BasicToolCallingNodeWorkflow)

    serialized_workflow: dict = workflow_display.serialize()
    # THEN we should get a serialized representation of the Workflow
    assert serialized_workflow.keys() == {
        "workflow_raw_data",
        "input_variables",
        "state_variables",
        "output_variables",
    }

    # AND its input variables should be what we expect
    input_variables = serialized_workflow["input_variables"]
    assert len(input_variables) == 1

    # AND its output variables should be what we expect
    output_variables = serialized_workflow["output_variables"]
    assert len(output_variables) == 2
    assert not DeepDiff(
        [
            {"id": "8e7c0147-930d-4b7f-b6b1-6d79641cd3eb", "key": "text", "type": "STRING"},
            {"id": "01a07e6d-7269-4f45-8b44-ef0227a2e88d", "key": "chat_history", "type": "CHAT_HISTORY"},
        ],
        output_variables,
        ignore_order=True,
    )

    # AND its raw data should be what we expect
    workflow_raw_data = serialized_workflow["workflow_raw_data"]
    tool_calling_node = workflow_raw_data["nodes"][1]
    assert tool_calling_node == {
        "id": "649a81cf-ce93-47c1-aa0f-e7a58a0cba8c",
        "label": "Get Current Weather Node",
        "type": "GENERIC",
        "should_file_merge": True,
        "display_data": {
            "position": {"x": 0.0, "y": 0.0},
            "comment": {
                "expanded": True,
                "value": "\n    A tool calling node that calls the get_current_weather function.\n    ",
            },
        },
        "base": {
            "name": "ToolCallingNode",
            "module": ["vellum", "workflows", "nodes", "displayable", "tool_calling_node", "node"],
        },
        "definition": {
            "name": "GetCurrentWeatherNode",
            "module": ["tests", "workflows", "basic_tool_calling_node", "workflow"],
        },
        "trigger": {"id": "fa785565-2906-433c-914a-79c574bcced4", "merge_behavior": "AWAIT_ATTRIBUTES"},
        "ports": [{"id": "8ae76650-6658-441e-aab2-dbdc62dc6a48", "name": "default", "type": "DEFAULT"}],
        "adornments": None,
        "attributes": [
            {
                "id": "6991a1bf-6a1d-4b0a-8e67-39505b324216",
                "name": "ml_model",
                "value": {"type": "CONSTANT_VALUE", "value": {"type": "STRING", "value": "gpt-4o-mini"}},
            },
            {
                "id": "74ce80ae-4f12-48fd-a9b7-412532e383ec",
                "name": "blocks",
                "value": {
                    "type": "CONSTANT_VALUE",
                    "value": {
                        "type": "JSON",
                        "value": [
                            {
                                "block_type": "CHAT_MESSAGE",
                                "state": None,
                                "cache_config": None,
                                "chat_role": "SYSTEM",
                                "chat_source": None,
                                "chat_message_unterminated": None,
                                "blocks": [
                                    {
                                        "block_type": "RICH_TEXT",
                                        "state": None,
                                        "cache_config": None,
                                        "blocks": [
                                            {
                                                "block_type": "PLAIN_TEXT",
                                                "state": None,
                                                "cache_config": None,
                                                "text": "You are a weather expert",
                                            }
                                        ],
                                    }
                                ],
                            },
                            {
                                "block_type": "CHAT_MESSAGE",
                                "state": None,
                                "cache_config": None,
                                "chat_role": "USER",
                                "chat_source": None,
                                "chat_message_unterminated": None,
                                "blocks": [
                                    {
                                        "block_type": "RICH_TEXT",
                                        "state": None,
                                        "cache_config": None,
                                        "blocks": [
                                            {
                                                "block_type": "VARIABLE",
                                                "state": None,
                                                "cache_config": None,
                                                "input_variable": "aa87c0db-68c0-4c9b-9ad0-ddb48bb169eb",
                                            }
                                        ],
                                    }
                                ],
                            },
                        ],
                    },
                },
            },
            {
                "id": "1e3cd0b3-5657-42bd-8a71-48bdf9e9b835",
                "name": "functions",
                "value": {
                    "type": "CONSTANT_VALUE",
                    "value": {
                        "type": "JSON",
                        "value": [
                            {
                                "type": "CODE_EXECUTION",
                                "name": "get_current_weather",
                                "description": "\n    Get the current weather in a given location.\n    ",
                                "definition": {
                                    "state": None,
                                    "cache_config": None,
                                    "name": "get_current_weather",
                                    "description": "\n    Get the current weather in a given location.\n    ",
                                    "parameters": {
                                        "type": "object",
                                        "properties": {
                                            "location": {
                                                "type": "string",
                                                "description": "The location to get the weather for",
                                            },
                                            "unit": {"type": "string", "description": "The unit of temperature"},
                                        },
                                        "required": ["location", "unit"],
                                    },
                                    "inputs": None,
                                    "forced": None,
                                    "strict": None,
                                },
                                "src": 'import math\nfrom typing import Annotated\n\n\ndef get_current_weather(\n    location: Annotated[str, "The location to get the weather for"], unit: Annotated[str, "The unit of temperature"]\n) -> str:\n    """\n    Get the current weather in a given location.\n    """\n    return f"The current weather in {location} is sunny with a temperature of {get_temperature(70.1)} degrees {unit}."\n\n\ndef get_temperature(temperature: float) -> int:\n    """\n    Get the temperature in a given location.\n    """\n    return math.floor(temperature)\n',  # noqa: E501
                            }
                        ],
                    },
                },
            },
            {
                "id": "e554e8c1-a270-4fbf-951f-fd4aca4afe9b",
                "name": "prompt_inputs",
                "value": {
                    "type": "DICTIONARY_REFERENCE",
                    "entries": [
                        {
                            "id": "aa87c0db-68c0-4c9b-9ad0-ddb48bb169eb",
                            "key": "question",
                            "value": {
                                "type": "WORKFLOW_INPUT",
                                "input_variable_id": "a70e0597-0076-4a17-a8d2-c8d6b4a05bac",
                            },
                        }
                    ],
                },
            },
            {
                "id": "ef504b60-5b94-43d0-b31d-534309a52ff2",
                "name": "parameters",
                "value": {
                    "type": "CONSTANT_VALUE",
                    "value": {
                        "type": "JSON",
                        "value": {
                            "stop": [],
                            "temperature": 0.0,
                            "max_tokens": 4096.0,
                            "top_p": 1.0,
                            "top_k": 0.0,
                            "frequency_penalty": 0.0,
                            "presence_penalty": 0.0,
                            "logit_bias": None,
                            "custom_parameters": {"mode": "initial"},
                        },
                    },
                },
            },
            {
                "id": "83546f2d-f531-4773-b87b-aeb104b9218d",
                "name": "max_prompt_iterations",
                "value": {"type": "CONSTANT_VALUE", "value": {"type": "NUMBER", "value": 25.0}},
            },
            {
                "id": "bb8b8427-db2c-4115-b26b-c30dc705787a",
                "name": "settings",
                "value": {"type": "CONSTANT_VALUE", "value": {"type": "JSON", "value": None}},
            },
        ],
        "outputs": [
            {
                "id": "a7ed5e04-2ddd-45f3-bb08-462068f17ad8",
                "name": "json",
                "type": "JSON",
                "value": None,
                "schema": {"type": "object", "additionalProperties": {}},
            },
            {
                "id": "d0d0cd85-8546-4d90-bdc1-86c751ba04e5",
                "name": "text",
                "type": "STRING",
                "value": None,
                "schema": {"type": "string"},
            },
            {
                "id": "33a737c2-d347-48d4-bf62-e36c06aebf0c",
                "name": "chat_history",
                "type": "CHAT_HISTORY",
                "value": None,
                "schema": {"type": "array", "items": {"$ref": "#/$defs/vellum.client.types.chat_message.ChatMessage"}},
            },
        ],
    }
