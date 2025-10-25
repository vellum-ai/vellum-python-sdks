from deepdiff import DeepDiff

from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display

from tests.workflows.basic_inline_subworkflow.workflow import BasicInlineSubworkflowWorkflow


def test_serialize_workflow():
    # GIVEN a Workflow
    # WHEN we serialize it
    workflow_display = get_workflow_display(workflow_class=BasicInlineSubworkflowWorkflow)
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
    assert len(input_variables) == 2
    assert not DeepDiff(
        [
            {
                "id": "fa73da37-34c3-47a9-be58-69cc6cdbfca5",
                "key": "city",
                "type": "STRING",
                "required": True,
                "default": None,
                "extensions": {"color": None},
            },
            {
                "id": "aba1e6e0-dfa7-4c15-a4e6-aec6feebfaca",
                "key": "date",
                "type": "STRING",
                "required": True,
                "default": None,
                "extensions": {"color": None},
            },
        ],
        input_variables,
        ignore_order=True,
    )

    # AND its output variables should be what we expect
    output_variables = serialized_workflow["output_variables"]
    assert len(output_variables) == 2
    assert not DeepDiff(
        [
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
        "id": "6358dcfe-b162-4e19-99ca-401d1ada9bdc",
        "type": "ENTRYPOINT",
        "base": None,
        "definition": None,
        "inputs": [],
        "data": {
            "label": "Entrypoint Node",
            "source_handle_id": "c344fdee-282b-40c9-8c97-6dd08830948c",
        },
        "display_data": {
            "position": {"x": 0.0, "y": -50.0},
        },
    }

    subworkflow_node = workflow_raw_data["nodes"][1]
    assert not DeepDiff(
        {
            "id": "cc246984-82bb-4da3-b447-ea66aa1cffe4",
            "type": "SUBWORKFLOW",
            "inputs": [
                {
                    "id": "9ae1bf55-2024-48e4-b7fa-29c189545dc8",
                    "key": "metro",
                    "value": {
                        "rules": [
                            {
                                "type": "INPUT_VARIABLE",
                                "data": {"input_variable_id": "fa73da37-34c3-47a9-be58-69cc6cdbfca5"},
                            }
                        ],
                        "combinator": "OR",
                    },
                }
            ],
            "data": {
                "label": "Example Inline Subworkflow Node",
                "error_output_id": None,
                "source_handle_id": "4e6146c9-05f1-4494-b48c-7ff02224cf5a",
                "target_handle_id": "955e83a5-6a19-4dfa-ab19-9a6fd63d017d",
                "variant": "INLINE",
                "workflow_raw_data": {
                    "nodes": [
                        {
                            "id": "afa49a0f-db35-4552-9217-5b8f237e84bc",
                            "type": "ENTRYPOINT",
                            "inputs": [],
                            "data": {
                                "label": "Entrypoint Node",
                                "source_handle_id": "9914a6a0-9a99-430d-8ddd-f7c13847fe1a",
                            },
                            "display_data": {"position": {"x": 0.0, "y": -50.0}},
                            "base": None,
                            "definition": None,
                        },
                        {
                            "id": "45ba1e29-611f-4a6f-9f51-7cf6fe47141e",
                            "label": "Start Node",
                            "type": "GENERIC",
                            "should_file_merge": True,
                            "display_data": {"position": {"x": 200.0, "y": -50.0}},
                            "base": {"name": "BaseNode", "module": ["vellum", "workflows", "nodes", "bases", "base"]},
                            "definition": {
                                "name": "StartNode",
                                "module": ["tests", "workflows", "basic_inline_subworkflow", "workflow"],
                            },
                            "trigger": {
                                "id": "ab273dfa-6719-427c-9054-dd2c03d90d5d",
                                "merge_behavior": "AWAIT_ATTRIBUTES",
                            },
                            "ports": [
                                {"id": "37a41308-2f6c-443d-a832-5859cef231e8", "name": "default", "type": "DEFAULT"}
                            ],
                            "adornments": None,
                            "attributes": [
                                {
                                    "id": "47970f44-eafc-4526-bd81-b1419b0a787a",
                                    "name": "metro",
                                    "value": {
                                        "type": "WORKFLOW_INPUT",
                                        "input_variable_id": "f2f5da15-026d-4905-bfe7-7d16bda20eed",
                                    },
                                },
                                {
                                    "id": "6d933d5e-84a2-434a-baf8-25315c9469af",
                                    "name": "date",
                                    "value": {
                                        "type": "WORKFLOW_INPUT",
                                        "input_variable_id": "aba1e6e0-dfa7-4c15-a4e6-aec6feebfaca",
                                    },
                                },
                            ],
                            "outputs": [
                                {
                                    "id": "1162f98c-fc51-49c3-a634-120ccbf2ddc2",
                                    "name": "temperature",
                                    "type": "NUMBER",
                                    "value": None,
                                },
                                {
                                    "id": "4d13651c-3c74-4bf4-8595-2339de83c59a",
                                    "name": "reasoning",
                                    "type": "STRING",
                                    "value": None,
                                },
                            ],
                        },
                        {
                            "id": "a773c3a5-78cb-4250-8d29-7282e8a579d3",
                            "type": "TERMINAL",
                            "data": {
                                "label": "Final Output",
                                "name": "temperature",
                                "target_handle_id": "804bb543-9cf4-457f-acf1-fb4b8b7d9259",
                                "output_id": "2fc57139-7420-49e5-96a6-dcbb3ff5d622",
                                "output_type": "NUMBER",
                                "node_input_id": "712eaeec-9e1e-41bd-9217-9caec8b6ade7",
                            },
                            "inputs": [
                                {
                                    "id": "712eaeec-9e1e-41bd-9217-9caec8b6ade7",
                                    "key": "node_input",
                                    "value": {
                                        "rules": [
                                            {
                                                "type": "NODE_OUTPUT",
                                                "data": {
                                                    "node_id": "45ba1e29-611f-4a6f-9f51-7cf6fe47141e",
                                                    "output_id": "1162f98c-fc51-49c3-a634-120ccbf2ddc2",
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
                                "module": ["vellum", "workflows", "nodes", "displayable", "final_output_node", "node"],
                            },
                            "definition": None,
                        },
                        {
                            "id": "570f4d12-69ff-49f1-ba98-ade6283dd7c2",
                            "type": "TERMINAL",
                            "data": {
                                "label": "Final Output",
                                "name": "reasoning",
                                "target_handle_id": "6d4c4a14-c388-4c7a-b223-eb39baf5c080",
                                "output_id": "fad5dd9f-3328-4e70-ad55-65a5325a4a82",
                                "output_type": "STRING",
                                "node_input_id": "8fd4279a-4f13-4257-9577-1b55e964cdf1",
                            },
                            "inputs": [
                                {
                                    "id": "8fd4279a-4f13-4257-9577-1b55e964cdf1",
                                    "key": "node_input",
                                    "value": {
                                        "rules": [
                                            {
                                                "type": "NODE_OUTPUT",
                                                "data": {
                                                    "node_id": "45ba1e29-611f-4a6f-9f51-7cf6fe47141e",
                                                    "output_id": "4d13651c-3c74-4bf4-8595-2339de83c59a",
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
                                "module": ["vellum", "workflows", "nodes", "displayable", "final_output_node", "node"],
                            },
                            "definition": None,
                        },
                    ],
                    "edges": [
                        {
                            "id": "85ac167b-dc92-4197-b364-64e630cab237",
                            "source_node_id": "afa49a0f-db35-4552-9217-5b8f237e84bc",
                            "source_handle_id": "9914a6a0-9a99-430d-8ddd-f7c13847fe1a",
                            "target_node_id": "45ba1e29-611f-4a6f-9f51-7cf6fe47141e",
                            "target_handle_id": "ab273dfa-6719-427c-9054-dd2c03d90d5d",
                            "type": "DEFAULT",
                        },
                        {
                            "id": "6f16dfb8-d794-4be8-8860-6ea34f0b9e7c",
                            "source_node_id": "45ba1e29-611f-4a6f-9f51-7cf6fe47141e",
                            "source_handle_id": "37a41308-2f6c-443d-a832-5859cef231e8",
                            "target_node_id": "a773c3a5-78cb-4250-8d29-7282e8a579d3",
                            "target_handle_id": "804bb543-9cf4-457f-acf1-fb4b8b7d9259",
                            "type": "DEFAULT",
                        },
                        {
                            "id": "63b77ff0-5282-46ce-8da9-37ced05ac61c",
                            "source_node_id": "45ba1e29-611f-4a6f-9f51-7cf6fe47141e",
                            "source_handle_id": "37a41308-2f6c-443d-a832-5859cef231e8",
                            "target_node_id": "570f4d12-69ff-49f1-ba98-ade6283dd7c2",
                            "target_handle_id": "6d4c4a14-c388-4c7a-b223-eb39baf5c080",
                            "type": "DEFAULT",
                        },
                    ],
                    "display_data": {"viewport": {"x": 0.0, "y": 0.0, "zoom": 1.0}},
                    "definition": {
                        "name": "NestedWorkflow",
                        "module": ["tests", "workflows", "basic_inline_subworkflow", "workflow"],
                    },
                    "output_values": [
                        {
                            "output_variable_id": "2fc57139-7420-49e5-96a6-dcbb3ff5d622",
                            "value": {
                                "type": "NODE_OUTPUT",
                                "node_id": "45ba1e29-611f-4a6f-9f51-7cf6fe47141e",
                                "node_output_id": "1162f98c-fc51-49c3-a634-120ccbf2ddc2",
                            },
                        },
                        {
                            "output_variable_id": "fad5dd9f-3328-4e70-ad55-65a5325a4a82",
                            "value": {
                                "type": "NODE_OUTPUT",
                                "node_id": "45ba1e29-611f-4a6f-9f51-7cf6fe47141e",
                                "node_output_id": "4d13651c-3c74-4bf4-8595-2339de83c59a",
                            },
                        },
                    ],
                },
                "input_variables": [
                    {
                        "id": "9ae1bf55-2024-48e4-b7fa-29c189545dc8",
                        "key": "metro",
                        "type": "STRING",
                        "required": True,
                        "default": None,
                    }
                ],
                "output_variables": [
                    {"id": "2fc57139-7420-49e5-96a6-dcbb3ff5d622", "key": "temperature", "type": "NUMBER"},
                    {"id": "fad5dd9f-3328-4e70-ad55-65a5325a4a82", "key": "reasoning", "type": "STRING"},
                ],
            },
            "display_data": {"position": {"x": 200.0, "y": -50.0}},
            "base": {
                "name": "InlineSubworkflowNode",
                "module": ["vellum", "workflows", "nodes", "core", "inline_subworkflow_node", "node"],
            },
            "definition": {
                "name": "ExampleInlineSubworkflowNode",
                "module": ["tests", "workflows", "basic_inline_subworkflow", "workflow"],
            },
            "trigger": {
                "id": "955e83a5-6a19-4dfa-ab19-9a6fd63d017d",
                "merge_behavior": "AWAIT_ATTRIBUTES",
            },
            "ports": [{"id": "4e6146c9-05f1-4494-b48c-7ff02224cf5a", "name": "default", "type": "DEFAULT"}],
        },
        subworkflow_node,
    )

    temperature_terminal_node = next(
        node for node in workflow_raw_data["nodes"][2:] if node["data"]["name"] == "temperature"
    )
    reasoning_terminal_node = next(
        node for node in workflow_raw_data["nodes"][2:] if node["data"]["name"] == "reasoning"
    )

    assert not DeepDiff(
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
                                    "node_id": "cc246984-82bb-4da3-b447-ea66aa1cffe4",
                                    "output_id": "0a7192da-5576-4933-bba4-de8adf5d7996",
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
                "module": ["vellum", "workflows", "nodes", "displayable", "final_output_node", "node"],
            },
            "definition": None,
        },
        reasoning_terminal_node,
        ignore_order=True,
        # TODO: Make sure this output ID matches the workflow output ID of the subworkflow node's workflow
        # https://app.shortcut.com/vellum/story/5660/fix-output-id-in-subworkflow-nodes
        exclude_regex_paths=r"root\['inputs'\]\[0\]\['value'\]\['rules'\]\[0\]\['data'\]\['output_id'\]",
    )

    assert not DeepDiff(
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
                                    "node_id": "cc246984-82bb-4da3-b447-ea66aa1cffe4",
                                    "output_id": "86dd0202-c141-48a3-8382-2da60372e77c",
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
                "module": ["vellum", "workflows", "nodes", "displayable", "final_output_node", "node"],
            },
            "definition": None,
        },
        temperature_terminal_node,
        ignore_order=True,
        # TODO: Make sure this output ID matches the workflow output ID of the subworkflow node's workflow
        # https://app.shortcut.com/vellum/story/5660/fix-output-id-in-subworkflow-nodes
        exclude_regex_paths=r"root\['inputs'\]\[0\]\['value'\]\['rules'\]\[0\]\['data'\]\['output_id'\]",
    )

    # AND each edge should be serialized correctly
    serialized_edges = workflow_raw_data["edges"]
    assert not DeepDiff(
        [
            {
                "id": "4bfa5508-f7bc-4b8c-b468-f6f830caa660",
                "source_node_id": "6358dcfe-b162-4e19-99ca-401d1ada9bdc",
                "source_handle_id": "c344fdee-282b-40c9-8c97-6dd08830948c",
                "target_node_id": "cc246984-82bb-4da3-b447-ea66aa1cffe4",
                "target_handle_id": "955e83a5-6a19-4dfa-ab19-9a6fd63d017d",
                "type": "DEFAULT",
            },
            {
                "id": "3c5d8990-48f5-42e1-893e-bc8308d2110a",
                "source_node_id": "cc246984-82bb-4da3-b447-ea66aa1cffe4",
                "source_handle_id": "4e6146c9-05f1-4494-b48c-7ff02224cf5a",
                "target_node_id": "0779b232-82ab-4dbe-a340-6a85e6ab3368",
                "target_handle_id": "9e077063-c394-4c7b-b0c6-e6686df67984",
                "type": "DEFAULT",
            },
            {
                "id": "de0b8090-a26e-4e09-9173-9f7400a5be4c",
                "source_node_id": "cc246984-82bb-4da3-b447-ea66aa1cffe4",
                "source_handle_id": "4e6146c9-05f1-4494-b48c-7ff02224cf5a",
                "target_node_id": "31b74695-3f1c-47cf-8be8-a4d86cc589e8",
                "target_handle_id": "8b525943-6c27-414b-a329-e29c0b217f72",
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
        "name": "BasicInlineSubworkflowWorkflow",
        "module": [
            "tests",
            "workflows",
            "basic_inline_subworkflow",
            "workflow",
        ],
    }
