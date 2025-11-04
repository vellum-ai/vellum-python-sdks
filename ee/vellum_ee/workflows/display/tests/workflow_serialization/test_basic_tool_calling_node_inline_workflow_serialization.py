from deepdiff import DeepDiff

from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display

from tests.workflows.basic_tool_calling_node_inline_workflow.workflow import BasicToolCallingNodeInlineWorkflowWorkflow


def test_serialize_workflow():
    # GIVEN a Workflow that uses a generic node
    # WHEN we serialize it
    workflow_display = get_workflow_display(workflow_class=BasicToolCallingNodeInlineWorkflowWorkflow)

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
            {"id": "dbedc4ee-be3b-4135-8c26-3643c0b6a530", "key": "text", "type": "STRING"},
            {"id": "c5733df5-03bb-498e-a770-8ef9bff85df3", "key": "chat_history", "type": "CHAT_HISTORY"},
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
            "module": ["tests", "workflows", "basic_tool_calling_node_inline_workflow", "workflow"],
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
                                                "input_variable": "8eb8b551-9b48-43b3-861f-52adb5c585a8",
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
                                "type": "INLINE_WORKFLOW",
                                "name": "BasicInlineSubworkflowWorkflow",
                                "description": "\n    A workflow that gets the weather for a given city and date.\n    ",  # noqa: E501
                                "exec_config": {
                                    "workflow_raw_data": {
                                        "nodes": [
                                            {
                                                "id": "6358dcfe-b162-4e19-99ca-401d1ada9bdc",
                                                "type": "ENTRYPOINT",
                                                "inputs": [],
                                                "data": {
                                                    "label": "Entrypoint Node",
                                                    "source_handle_id": "c344fdee-282b-40c9-8c97-6dd08830948c",
                                                },
                                                "display_data": {"position": {"x": 0.0, "y": -50.0}},
                                                "base": None,
                                                "definition": None,
                                            },
                                            {
                                                "id": "1381c078-efa2-4255-89a1-7b4cb742c7fc",
                                                "label": "Start Node",
                                                "type": "GENERIC",
                                                "should_file_merge": True,
                                                "display_data": {"position": {"x": 200.0, "y": -50.0}},
                                                "base": {
                                                    "name": "BaseNode",
                                                    "module": ["vellum", "workflows", "nodes", "bases", "base"],
                                                },
                                                "definition": {
                                                    "name": "StartNode",
                                                    "module": [
                                                        "tests",
                                                        "workflows",
                                                        "basic_tool_calling_node_inline_workflow",
                                                        "workflow",
                                                    ],
                                                },
                                                "trigger": {
                                                    "id": "6492efcf-4437-4af1-9ad7-269795ccb27a",
                                                    "merge_behavior": "AWAIT_ATTRIBUTES",
                                                },
                                                "ports": [
                                                    {
                                                        "id": "1e739e86-a285-4438-9725-a152c15a63e3",
                                                        "name": "default",
                                                        "type": "DEFAULT",
                                                    }
                                                ],
                                                "adornments": None,
                                                "attributes": [
                                                    {
                                                        "id": "60ad78cd-fc78-4e08-926d-5a095b34d4f5",
                                                        "name": "city",
                                                        "value": {
                                                            "type": "WORKFLOW_INPUT",
                                                            "input_variable_id": "fa73da37-34c3-47a9-be58-69cc6cdbfca5",
                                                        },
                                                    },
                                                    {
                                                        "id": "c5f2d66c-5bb6-4d2a-8e4d-5356318cd3ba",
                                                        "name": "date",
                                                        "value": {
                                                            "type": "WORKFLOW_INPUT",
                                                            "input_variable_id": "aba1e6e0-dfa7-4c15-a4e6-aec6feebfaca",
                                                        },
                                                    },
                                                ],
                                                "outputs": [
                                                    {
                                                        "id": "3f4c753e-f057-47bb-9748-7968283cc8aa",
                                                        "name": "temperature",
                                                        "type": "NUMBER",
                                                        "value": None,
                                                    },
                                                    {
                                                        "id": "2a4a62b3-cd26-4d2c-b3f1-eaa5f9dd22dd",
                                                        "name": "reasoning",
                                                        "type": "STRING",
                                                        "value": None,
                                                    },
                                                ],
                                            },
                                            {
                                                "id": "0779b232-82ab-4dbe-a340-6a85e6ab3368",
                                                "type": "TERMINAL",
                                                "data": {
                                                    "label": "Final Output",
                                                    "name": "temperature",
                                                    "target_handle_id": "9e077063-c394-4c7b-b0c6-e6686df67984",
                                                    "output_id": "99afb757-2782-465d-ab55-80ccf50552b9",
                                                    "output_type": "NUMBER",
                                                    "node_input_id": "7761c5e1-cc2e-43ab-bfd2-f66c3d47b3b9",
                                                },
                                                "inputs": [
                                                    {
                                                        "id": "7761c5e1-cc2e-43ab-bfd2-f66c3d47b3b9",
                                                        "key": "node_input",
                                                        "value": {
                                                            "rules": [
                                                                {
                                                                    "type": "NODE_OUTPUT",
                                                                    "data": {
                                                                        "node_id": "1381c078-efa2-4255-89a1-7b4cb742c7fc",  # noqa: E501
                                                                        "output_id": "3f4c753e-f057-47bb-9748-7968283cc8aa",  # noqa: E501
                                                                    },
                                                                }
                                                            ],
                                                            "combinator": "OR",
                                                        },
                                                    }
                                                ],
                                                "display_data": {"position": {"x": 400.0, "y": -175.0}},
                                                "base": {
                                                    "name": "FinalOutputNode",
                                                    "module": [
                                                        "vellum",
                                                        "workflows",
                                                        "nodes",
                                                        "displayable",
                                                        "final_output_node",
                                                        "node",
                                                    ],
                                                },
                                                "definition": None,
                                            },
                                            {
                                                "id": "31b74695-3f1c-47cf-8be8-a4d86cc589e8",
                                                "type": "TERMINAL",
                                                "data": {
                                                    "label": "Final Output",
                                                    "name": "reasoning",
                                                    "target_handle_id": "8b525943-6c27-414b-a329-e29c0b217f72",
                                                    "output_id": "7444a019-081a-4e10-a528-3249299159f7",
                                                    "output_type": "STRING",
                                                    "node_input_id": "c1833b54-95b6-4365-8e57-51b09c8e2606",
                                                },
                                                "inputs": [
                                                    {
                                                        "id": "c1833b54-95b6-4365-8e57-51b09c8e2606",
                                                        "key": "node_input",
                                                        "value": {
                                                            "rules": [
                                                                {
                                                                    "type": "NODE_OUTPUT",
                                                                    "data": {
                                                                        "node_id": "1381c078-efa2-4255-89a1-7b4cb742c7fc",  # noqa: E501
                                                                        "output_id": "2a4a62b3-cd26-4d2c-b3f1-eaa5f9dd22dd",  # noqa: E501
                                                                    },
                                                                }
                                                            ],
                                                            "combinator": "OR",
                                                        },
                                                    }
                                                ],
                                                "display_data": {"position": {"x": 400.0, "y": 75.0}},
                                                "base": {
                                                    "name": "FinalOutputNode",
                                                    "module": [
                                                        "vellum",
                                                        "workflows",
                                                        "nodes",
                                                        "displayable",
                                                        "final_output_node",
                                                        "node",
                                                    ],
                                                },
                                                "definition": None,
                                            },
                                        ],
                                        "edges": [
                                            {
                                                "id": "a37781d1-f7a5-4386-a67d-0c3d5c929602",
                                                "source_node_id": "6358dcfe-b162-4e19-99ca-401d1ada9bdc",
                                                "source_handle_id": "c344fdee-282b-40c9-8c97-6dd08830948c",
                                                "target_node_id": "1381c078-efa2-4255-89a1-7b4cb742c7fc",
                                                "target_handle_id": "6492efcf-4437-4af1-9ad7-269795ccb27a",
                                                "type": "DEFAULT",
                                            },
                                            {
                                                "id": "3c5d8990-48f5-42e1-893e-bc8308d2110a",
                                                "source_node_id": "1381c078-efa2-4255-89a1-7b4cb742c7fc",
                                                "source_handle_id": "1e739e86-a285-4438-9725-a152c15a63e3",
                                                "target_node_id": "0779b232-82ab-4dbe-a340-6a85e6ab3368",
                                                "target_handle_id": "9e077063-c394-4c7b-b0c6-e6686df67984",
                                                "type": "DEFAULT",
                                            },
                                            {
                                                "id": "de0b8090-a26e-4e09-9173-9f7400a5be4c",
                                                "source_node_id": "1381c078-efa2-4255-89a1-7b4cb742c7fc",
                                                "source_handle_id": "1e739e86-a285-4438-9725-a152c15a63e3",
                                                "target_node_id": "31b74695-3f1c-47cf-8be8-a4d86cc589e8",
                                                "target_handle_id": "8b525943-6c27-414b-a329-e29c0b217f72",
                                                "type": "DEFAULT",
                                            },
                                        ],
                                        "display_data": {"viewport": {"x": 0.0, "y": 0.0, "zoom": 1.0}},
                                        "definition": {
                                            "name": "BasicInlineSubworkflowWorkflow",
                                            "module": [
                                                "tests",
                                                "workflows",
                                                "basic_tool_calling_node_inline_workflow",
                                                "workflow",
                                            ],
                                        },
                                        "output_values": [
                                            {
                                                "output_variable_id": "99afb757-2782-465d-ab55-80ccf50552b9",
                                                "value": {
                                                    "type": "NODE_OUTPUT",
                                                    "node_id": "1381c078-efa2-4255-89a1-7b4cb742c7fc",
                                                    "node_output_id": "3f4c753e-f057-47bb-9748-7968283cc8aa",
                                                },
                                            },
                                            {
                                                "output_variable_id": "7444a019-081a-4e10-a528-3249299159f7",
                                                "value": {
                                                    "type": "NODE_OUTPUT",
                                                    "node_id": "1381c078-efa2-4255-89a1-7b4cb742c7fc",
                                                    "node_output_id": "2a4a62b3-cd26-4d2c-b3f1-eaa5f9dd22dd",
                                                },
                                            },
                                        ],
                                    },
                                    "input_variables": [
                                        {
                                            "id": "fa73da37-34c3-47a9-be58-69cc6cdbfca5",
                                            "key": "city",
                                            "type": "STRING",
                                            "default": None,
                                            "required": True,
                                            "extensions": {"color": None},
                                        },
                                        {
                                            "id": "aba1e6e0-dfa7-4c15-a4e6-aec6feebfaca",
                                            "key": "date",
                                            "type": "STRING",
                                            "default": None,
                                            "required": True,
                                            "extensions": {"color": None},
                                        },
                                    ],
                                    "state_variables": [],
                                    "output_variables": [
                                        {
                                            "id": "99afb757-2782-465d-ab55-80ccf50552b9",
                                            "key": "temperature",
                                            "type": "NUMBER",
                                        },
                                        {
                                            "id": "7444a019-081a-4e10-a528-3249299159f7",
                                            "key": "reasoning",
                                            "type": "STRING",
                                        },
                                    ],
                                },
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
                            "id": "8eb8b551-9b48-43b3-861f-52adb5c585a8",
                            "key": "question",
                            "value": {
                                "type": "WORKFLOW_INPUT",
                                "input_variable_id": "045942b7-e5b9-482c-b4d4-943309a20e05",
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
                "value": {"type": "CONSTANT_VALUE", "value": {"type": "NUMBER", "value": 25.0}},
            },
            {
                "id": "f92dc3ec-a19a-4491-a98a-2b2df322e2e3",
                "name": "settings",
                "value": {"type": "CONSTANT_VALUE", "value": {"type": "JSON", "value": None}},
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
