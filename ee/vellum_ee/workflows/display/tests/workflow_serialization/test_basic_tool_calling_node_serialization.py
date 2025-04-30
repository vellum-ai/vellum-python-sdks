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
    assert len(input_variables) == 0

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

    assert len(workflow_raw_data["edges"]) == 3
    assert len(workflow_raw_data["nodes"]) == 4

    # AND each node should be serialized correctly
    entrypoint_node = workflow_raw_data["nodes"][0]
    assert entrypoint_node == {
        "id": "5c4fd706-1b4b-4cf6-9237-038421f232d2",
        "type": "ENTRYPOINT",
        "inputs": [],
        "data": {"label": "Entrypoint Node", "source_handle_id": "26072df9-40ce-4aac-920e-e0682ad24721"},
        "display_data": {"position": {"x": 0.0, "y": 0.0}},
        "base": None,
        "definition": None,
    }

    tool_calling_node = workflow_raw_data["nodes"][1]
    assert tool_calling_node == {
        "id": "21f29cac-da87-495f-bba1-093d423f4e46",
        "label": "GetCurrentWeatherNode",
        "type": "GENERIC",
        "display_data": {
            "position": {"x": 0.0, "y": 0.0},
            "comment": {"value": "\n    A tool calling node that calls the get_current_weather function.\n    "},
        },
        "base": {
            "name": "ToolCallingNode",
            "module": ["vellum", "workflows", "nodes", "experimental", "tool_calling_node", "node"],
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
                        "items": [
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
                        "items": [
                            {
                                "state": None,
                                "cache_config": None,
                                "name": "get_current_weather",
                                "description": None,
                                "parameters": {
                                    "type": "object",
                                    "properties": {"location": {"type": "string"}, "unit": {"type": "string"}},
                                    "required": ["location", "unit"],
                                },
                                "forced": None,
                                "strict": None,
                            }
                        ],
                    },
                },
            },
            {
                "id": "0f6dc102-3460-4963-91fa-7ba85d65ef7a",
                "name": "prompt_inputs",
                "value": {
                    "type": "CONSTANT_VALUE",
                    "value": {"type": "JSON", "value": {"question": "What's the weather like in San Francisco?"}},
                },
            },
            {
                "id": "5c041b7d-732c-4773-a93a-32211f2af0b3",
                "name": "max_tool_calls",
                "value": {"type": "CONSTANT_VALUE", "value": {"type": "NUMBER", "value": 1.0}},
            },
        ],
        "outputs": [
            {
                "id": "e62bc785-a914-4066-b79e-8c89a5d0ec6c",
                "name": "text",
                "type": "STRING",
                "value": {"type": "CONSTANT_VALUE", "value": {"type": "STRING", "value": ""}},
            },
            {
                "id": "4674f1d9-e3af-411f-8a55-40a3a3ab5394",
                "name": "chat_history",
                "type": "CHAT_HISTORY",
                "value": {"type": "CONSTANT_VALUE", "value": {"type": "JSON", "items": []}},
            },
        ],
    }

    final_output_node = workflow_raw_data["nodes"][2]
    assert not DeepDiff(
        {
            "id": "676dbf0d-a896-4b18-9d3e-2108278b4811",
            "type": "TERMINAL",
            "data": {
                "label": "Final Output",
                "name": "text",
                "target_handle_id": "2f7c78a1-a5fe-4df8-9299-926ddcb31f84",
                "output_id": "8e7c0147-930d-4b7f-b6b1-6d79641cd3eb",
                "output_type": "STRING",
                "node_input_id": "5dc6e7a0-7fdd-47e1-9fbe-703f809c1761",
            },
            "inputs": [
                {
                    "id": "5dc6e7a0-7fdd-47e1-9fbe-703f809c1761",
                    "key": "node_input",
                    "value": {
                        "rules": [
                            {
                                "type": "NODE_OUTPUT",
                                "data": {
                                    "node_id": "21f29cac-da87-495f-bba1-093d423f4e46",
                                    "output_id": "e62bc785-a914-4066-b79e-8c89a5d0ec6c",
                                },
                            }
                        ],
                        "combinator": "OR",
                    },
                }
            ],
            "display_data": {"position": {"x": 0.0, "y": 0.0}},
            "base": {
                "name": "FinalOutputNode",
                "module": ["vellum", "workflows", "nodes", "displayable", "final_output_node", "node"],
            },
            "definition": None,
        },
        final_output_node,
        ignore_order=True,
    )

    # AND each edge should be serialized correctly
    serialized_edges = workflow_raw_data["edges"]
    assert not DeepDiff(
        [
            {
                "id": "daef9bcb-a3c1-4e82-9b02-35631c6adebd",
                "source_node_id": "5c4fd706-1b4b-4cf6-9237-038421f232d2",
                "source_handle_id": "26072df9-40ce-4aac-920e-e0682ad24721",
                "target_node_id": "21f29cac-da87-495f-bba1-093d423f4e46",
                "target_handle_id": "2414743b-b1dd-4552-8abf-9b7481df9762",
                "type": "DEFAULT",
            },
            {
                "id": "0e8d361a-2c8c-488b-90a6-95f0d5b11ffc",
                "source_node_id": "21f29cac-da87-495f-bba1-093d423f4e46",
                "source_handle_id": "3cd6d78c-9dad-42aa-ad38-31f67057c379",
                "target_node_id": "676dbf0d-a896-4b18-9d3e-2108278b4811",
                "target_handle_id": "2f7c78a1-a5fe-4df8-9299-926ddcb31f84",
                "type": "DEFAULT",
            },
            {
                "id": "9746263a-b783-4ba8-80eb-ace6e005827a",
                "source_node_id": "21f29cac-da87-495f-bba1-093d423f4e46",
                "source_handle_id": "3cd6d78c-9dad-42aa-ad38-31f67057c379",
                "target_node_id": "5e43697c-da2d-442a-a500-af5a883dbff0",
                "target_handle_id": "0f6c0b7a-3060-40d6-b66b-93c418f045d1",
                "type": "DEFAULT",
            },
        ],
        serialized_edges,
        ignore_order=True,
    )

    # AND the display data should be what we expect
    display_data = workflow_raw_data["display_data"]
    assert display_data == {
        "viewport": {
            "x": 0.0,
            "y": 0.0,
            "zoom": 1.0,
        }
    }

    # AND the definition should be what we expect
    definition = workflow_raw_data["definition"]
    assert definition == {
        "name": "BasicToolCallingNodeWorkflow",
        "module": ["tests", "workflows", "basic_tool_calling_node", "workflow"],
    }
