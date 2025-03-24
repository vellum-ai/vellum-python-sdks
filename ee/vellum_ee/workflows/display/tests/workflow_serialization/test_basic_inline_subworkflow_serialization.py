from deepdiff import DeepDiff

from vellum_ee.workflows.display.workflows import VellumWorkflowDisplay
from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display

from tests.workflows.basic_inline_subworkflow.workflow import BasicInlineSubworkflowWorkflow


def test_serialize_workflow():
    # GIVEN a Workflow
    # WHEN we serialize it
    workflow_display = get_workflow_display(
        base_display_class=VellumWorkflowDisplay, workflow_class=BasicInlineSubworkflowWorkflow
    )
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
    assert workflow_raw_data.keys() == {"edges", "nodes", "display_data", "definition"}
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
            "position": {"x": 0.0, "y": 0.0},
        },
    }

    subworkflow_node = workflow_raw_data["nodes"][1]
    assert not DeepDiff(
        {
            "id": "080e4343-c7ce-4f82-b9dd-e94c8cc92239",
            "type": "SUBWORKFLOW",
            "inputs": [
                {
                    "id": "704c4640-bfda-44f0-8da3-e9cfc4f21cf2",
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
                "source_handle_id": "cfd831bc-ee7f-44d0-8d76-0ba0cd0277dc",
                "target_handle_id": "859a75a6-1bd2-4350-9509-4af66245e8e4",
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
                            "display_data": {"position": {"x": 0.0, "y": 0.0}},
                            "base": None,
                            "definition": None,
                        },
                        {
                            "id": "1381c078-efa2-4255-89a1-7b4cb742c7fc",
                            "label": "StartNode",
                            "type": "GENERIC",
                            "display_data": {"position": {"x": 0.0, "y": 0.0}},
                            "base": {"name": "BaseNode", "module": ["vellum", "workflows", "nodes", "bases", "base"]},
                            "definition": {
                                "name": "StartNode",
                                "module": ["tests", "workflows", "basic_inline_subworkflow", "workflow"],
                            },
                            "trigger": {
                                "id": "6492efcf-4437-4af1-9ad7-269795ccb27a",
                                "merge_behavior": "AWAIT_ATTRIBUTES",
                            },
                            "ports": [
                                {"id": "1e739e86-a285-4438-9725-a152c15a63e3", "name": "default", "type": "DEFAULT"}
                            ],
                            "adornments": None,
                            "attributes": [
                                {
                                    "id": "b0ac6b50-22a8-42ba-a707-1aa09a653205",
                                    "name": "metro",
                                    "value": {
                                        "type": "WORKFLOW_INPUT",
                                        "input_variable_id": "f2f5da15-026d-4905-bfe7-7d16bda20eed",
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
                                                    "node_id": "1381c078-efa2-4255-89a1-7b4cb742c7fc",
                                                    "output_id": "3f4c753e-f057-47bb-9748-7968283cc8aa",
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
                                                    "node_id": "1381c078-efa2-4255-89a1-7b4cb742c7fc",
                                                    "output_id": "2a4a62b3-cd26-4d2c-b3f1-eaa5f9dd22dd",
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
                    ],
                    "edges": [
                        {
                            "id": "fb2f58f0-9d49-4658-af78-afa9b94091a6",
                            "source_node_id": "afa49a0f-db35-4552-9217-5b8f237e84bc",
                            "source_handle_id": "9914a6a0-9a99-430d-8ddd-f7c13847fe1a",
                            "target_node_id": "1381c078-efa2-4255-89a1-7b4cb742c7fc",
                            "target_handle_id": "6492efcf-4437-4af1-9ad7-269795ccb27a",
                            "type": "DEFAULT",
                        },
                        {
                            "id": "6f16dfb8-d794-4be8-8860-6ea34f0b9e7c",
                            "source_node_id": "1381c078-efa2-4255-89a1-7b4cb742c7fc",
                            "source_handle_id": "1e739e86-a285-4438-9725-a152c15a63e3",
                            "target_node_id": "a773c3a5-78cb-4250-8d29-7282e8a579d3",
                            "target_handle_id": "804bb543-9cf4-457f-acf1-fb4b8b7d9259",
                            "type": "DEFAULT",
                        },
                        {
                            "id": "63b77ff0-5282-46ce-8da9-37ced05ac61c",
                            "source_node_id": "1381c078-efa2-4255-89a1-7b4cb742c7fc",
                            "source_handle_id": "1e739e86-a285-4438-9725-a152c15a63e3",
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
                },
                "input_variables": [{"id": "704c4640-bfda-44f0-8da3-e9cfc4f21cf2", "key": "metro", "type": "STRING"}],
                "output_variables": [
                    {"id": "2fc57139-7420-49e5-96a6-dcbb3ff5d622", "key": "temperature", "type": "NUMBER"},
                    {"id": "fad5dd9f-3328-4e70-ad55-65a5325a4a82", "key": "reasoning", "type": "STRING"},
                ],
            },
            "display_data": {"position": {"x": 0.0, "y": 0.0}},
            "base": {
                "name": "InlineSubworkflowNode",
                "module": ["vellum", "workflows", "nodes", "core", "inline_subworkflow_node", "node"],
            },
            "definition": {
                "name": "ExampleInlineSubworkflowNode",
                "module": ["tests", "workflows", "basic_inline_subworkflow", "workflow"],
            },
        },
        subworkflow_node,
        ignore_order=True,
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
                                    "node_id": "080e4343-c7ce-4f82-b9dd-e94c8cc92239",
                                    "output_id": "0a7192da-5576-4933-bba4-de8adf5d7996",
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
                                    "node_id": "080e4343-c7ce-4f82-b9dd-e94c8cc92239",
                                    "output_id": "86dd0202-c141-48a3-8382-2da60372e77c",
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
                "id": "71dd3569-ccf8-4352-ad42-3594be3a6c16",
                "source_node_id": "6358dcfe-b162-4e19-99ca-401d1ada9bdc",
                "source_handle_id": "c344fdee-282b-40c9-8c97-6dd08830948c",
                "target_node_id": "080e4343-c7ce-4f82-b9dd-e94c8cc92239",
                "target_handle_id": "859a75a6-1bd2-4350-9509-4af66245e8e4",
                "type": "DEFAULT",
            },
            {
                "id": "3c5d8990-48f5-42e1-893e-bc8308d2110a",
                "source_node_id": "080e4343-c7ce-4f82-b9dd-e94c8cc92239",
                "source_handle_id": "cfd831bc-ee7f-44d0-8d76-0ba0cd0277dc",
                "target_node_id": "0779b232-82ab-4dbe-a340-6a85e6ab3368",
                "target_handle_id": "9e077063-c394-4c7b-b0c6-e6686df67984",
                "type": "DEFAULT",
            },
            {
                "id": "de0b8090-a26e-4e09-9173-9f7400a5be4c",
                "source_node_id": "080e4343-c7ce-4f82-b9dd-e94c8cc92239",
                "source_handle_id": "cfd831bc-ee7f-44d0-8d76-0ba0cd0277dc",
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
