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
        "id": "21f29cac-da87-495f-bba1-093d423f4e46",
        "label": "Get Current Weather Node",
        "type": "GENERIC",
        "display_data": {
            "position": {"x": 200.0, "y": -50.0},
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
        "trigger": {"id": "2414743b-b1dd-4552-8abf-9b7481df9762", "merge_behavior": "AWAIT_ATTRIBUTES"},
        "ports": [{"id": "3cd6d78c-9dad-42aa-ad38-31f67057c379", "name": "default", "type": "DEFAULT"}],
        "adornments": None,
        "attributes": [
            {
                "id": "44420e39-966f-4c59-bdf8-6365a61c5d2a",
                "name": "ml_model",
                "value": {"type": "CONSTANT_VALUE", "value": {"type": "STRING", "value": "gpt-4o-mini"}},
            },
            {
                "id": "669cfb4b-8c25-460e-8952-b63d91302cbc",
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
                                                "input_variable": "question",
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
                "id": "78324739-ff89-47a5-902b-10da0cb95c6d",
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
                "id": "0f6dc102-3460-4963-91fa-7ba85d65ef7a",
                "name": "prompt_inputs",
                "value": {
                    "type": "DICTIONARY_REFERENCE",
                    "entries": [
                        {
                            "id": "b6d4427d-16dd-478a-9780-f88d60d2263d",
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
                "id": "229cd1ca-dc2f-4586-b933-c4d4966f7bd1",
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
                            "custom_parameters": None,
                        },
                    },
                },
            },
            {
                "id": "1668419e-a193-43a5-8a97-3394e89bf278",
                "name": "max_prompt_iterations",
                "value": {"type": "CONSTANT_VALUE", "value": {"type": "NUMBER", "value": 5.0}},
            },
        ],
        "outputs": [
            {"id": "e62bc785-a914-4066-b79e-8c89a5d0ec6c", "name": "text", "type": "STRING", "value": None},
            {
                "id": "4674f1d9-e3af-411f-8a55-40a3a3ab5394",
                "name": "chat_history",
                "type": "CHAT_HISTORY",
                "value": None,
            },
        ],
    }
