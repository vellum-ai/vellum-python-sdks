from unittest.mock import ANY

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
                "schema": {"type": "string"},
            },
            {
                "id": "aba1e6e0-dfa7-4c15-a4e6-aec6feebfaca",
                "key": "date",
                "type": "STRING",
                "required": True,
                "default": None,
                "extensions": {"color": None},
                "schema": {"type": "string"},
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
                "workflow_raw_data": ANY,
                "input_variables": [
                    {
                        "id": "9ae1bf55-2024-48e4-b7fa-29c189545dc8",
                        "key": "metro",
                        "type": "STRING",
                        "required": True,
                        "default": None,
                        "schema": {"type": "string"},
                    }
                ],
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
            "trigger": {
                "id": "955e83a5-6a19-4dfa-ab19-9a6fd63d017d",
                "merge_behavior": "AWAIT_ATTRIBUTES",
            },
            "ports": [{"id": "4e6146c9-05f1-4494-b48c-7ff02224cf5a", "name": "default", "type": "DEFAULT"}],
        },
        subworkflow_node,
        exclude_regex_paths=r"root\['data'\]\['workflow_raw_data'\]",
    )

    nested_workflow_data = subworkflow_node["data"]["workflow_raw_data"]
    nested_start_node = next(
        node for node in nested_workflow_data["nodes"] if node["type"] == "GENERIC" and node["label"] == "Start Node"
    )
    assert nested_start_node == {
        "id": "45ba1e29-611f-4a6f-9f51-7cf6fe47141e",
        "label": "Start Node",
        "type": "GENERIC",
        "should_file_merge": True,
        "display_data": {"position": {"x": 0.0, "y": 0.0}},
        "base": {"name": "BaseNode", "module": ["vellum", "workflows", "nodes", "bases", "base"]},
        "definition": {
            "name": "StartNode",
            "module": ["tests", "workflows", "basic_inline_subworkflow", "workflow"],
        },
        "trigger": {
            "id": "ab273dfa-6719-427c-9054-dd2c03d90d5d",
            "merge_behavior": "AWAIT_ATTRIBUTES",
        },
        "ports": [{"id": "37a41308-2f6c-443d-a832-5859cef231e8", "name": "default", "type": "DEFAULT"}],
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
                "schema": {"type": "number"},
            },
            {
                "id": "4d13651c-3c74-4bf4-8595-2339de83c59a",
                "name": "reasoning",
                "type": "STRING",
                "value": None,
                "schema": {"type": "string"},
            },
        ],
    }

    assert nested_workflow_data["display_data"] == {"viewport": {"x": 0.0, "y": 0.0, "zoom": 1.0}}
    assert nested_workflow_data["definition"] == {
        "name": "NestedWorkflow",
        "module": ["tests", "workflows", "basic_inline_subworkflow", "workflow"],
    }
    assert nested_workflow_data["output_values"] == [
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
    ]

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
