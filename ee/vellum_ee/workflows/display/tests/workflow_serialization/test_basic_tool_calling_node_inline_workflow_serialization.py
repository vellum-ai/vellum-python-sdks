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
    function_attributes = next(
        attribute for attribute in tool_calling_node["attributes"] if attribute["name"] == "functions"
    )
    assert function_attributes == {
        "id": "102d8447-5232-4e96-8192-9b1ca0f02650",
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
                                        "id": "07a83d1a-7948-4a23-9f46-9a60382d3a48",
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
                                            "id": "8a7854a7-a595-44ce-8197-1f9cd2c78f10",
                                            "merge_behavior": "AWAIT_ATTRIBUTES",
                                        },
                                        "ports": [
                                            {
                                                "id": "ee444f1a-b126-4480-8eb2-d22506640763",
                                                "name": "default",
                                                "type": "DEFAULT",
                                            }
                                        ],
                                        "adornments": None,
                                        "attributes": [
                                            {
                                                "id": "b5e2d415-4368-43c1-826c-ff6511bf6942",
                                                "name": "city",
                                                "value": {
                                                    "type": "WORKFLOW_INPUT",
                                                    "input_variable_id": "fa73da37-34c3-47a9-be58-69cc6cdbfca5",
                                                },
                                            },
                                            {
                                                "id": "5b3ed6d0-8cd6-41b6-ad55-d380b41f943b",
                                                "name": "date",
                                                "value": {
                                                    "type": "WORKFLOW_INPUT",
                                                    "input_variable_id": "aba1e6e0-dfa7-4c15-a4e6-aec6feebfaca",
                                                },
                                            },
                                        ],
                                        "outputs": [
                                            {
                                                "id": "272eccdb-6903-4f32-8159-8bfb87c65c2e",
                                                "name": "temperature",
                                                "type": "NUMBER",
                                                "value": None,
                                            },
                                            {
                                                "id": "8616509d-fecb-4bbf-afdc-bd4c5de35ce7",
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
                                                                "node_id": "07a83d1a-7948-4a23-9f46-9a60382d3a48",  # noqa: E501
                                                                "output_id": "272eccdb-6903-4f32-8159-8bfb87c65c2e",  # noqa: E501
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
                                                                "node_id": "07a83d1a-7948-4a23-9f46-9a60382d3a48",  # noqa: E501
                                                                "output_id": "8616509d-fecb-4bbf-afdc-bd4c5de35ce7",  # noqa: E501
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
                                        "id": "1c333b1c-a1b7-437e-9dfc-bdca8db2cff5",
                                        "source_node_id": "6358dcfe-b162-4e19-99ca-401d1ada9bdc",
                                        "source_handle_id": "c344fdee-282b-40c9-8c97-6dd08830948c",
                                        "target_node_id": "07a83d1a-7948-4a23-9f46-9a60382d3a48",
                                        "target_handle_id": "8a7854a7-a595-44ce-8197-1f9cd2c78f10",
                                        "type": "DEFAULT",
                                    },
                                    {
                                        "id": "3c5d8990-48f5-42e1-893e-bc8308d2110a",
                                        "source_node_id": "07a83d1a-7948-4a23-9f46-9a60382d3a48",
                                        "source_handle_id": "ee444f1a-b126-4480-8eb2-d22506640763",
                                        "target_node_id": "0779b232-82ab-4dbe-a340-6a85e6ab3368",
                                        "target_handle_id": "9e077063-c394-4c7b-b0c6-e6686df67984",
                                        "type": "DEFAULT",
                                    },
                                    {
                                        "id": "de0b8090-a26e-4e09-9173-9f7400a5be4c",
                                        "source_node_id": "07a83d1a-7948-4a23-9f46-9a60382d3a48",
                                        "source_handle_id": "ee444f1a-b126-4480-8eb2-d22506640763",
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
                                            "node_id": "07a83d1a-7948-4a23-9f46-9a60382d3a48",
                                            "node_output_id": "272eccdb-6903-4f32-8159-8bfb87c65c2e",
                                        },
                                    },
                                    {
                                        "output_variable_id": "7444a019-081a-4e10-a528-3249299159f7",
                                        "value": {
                                            "type": "NODE_OUTPUT",
                                            "node_id": "07a83d1a-7948-4a23-9f46-9a60382d3a48",
                                            "node_output_id": "8616509d-fecb-4bbf-afdc-bd4c5de35ce7",
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
    }
