from deepdiff import DeepDiff

from vellum_ee.workflows.display.workflows import VellumWorkflowDisplay
from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display

from tests.workflows.basic_map_node.workflow import SimpleMapExample


def test_serialize_workflow():
    # GIVEN a Workflow that uses a MapNode
    # WHEN we serialize it
    workflow_display = get_workflow_display(base_display_class=VellumWorkflowDisplay, workflow_class=SimpleMapExample)
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
    assert not DeepDiff(
        [
            {
                "id": "db2eb237-38e4-417a-8bfc-5bda0f3165ca",
                "key": "fruits",
                "type": "JSON",
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
    assert len(output_variables) == 1
    assert not DeepDiff(
        [
            {
                "id": "145b0b68-224b-4f83-90e6-eea3457e6c3e",
                "key": "final_value",
                "type": "JSON",
            },
        ],
        output_variables,
        ignore_order=True,
    )

    # AND its raw data should be what we expect
    workflow_raw_data = serialized_workflow["workflow_raw_data"]
    assert workflow_raw_data.keys() == {"edges", "nodes", "display_data", "definition"}
    assert len(workflow_raw_data["edges"]) == 2
    assert len(workflow_raw_data["nodes"]) == 3

    # AND each node should be serialized correctly
    entrypoint_node = workflow_raw_data["nodes"][0]
    assert entrypoint_node == {
        "id": "c0aa464d-1685-4f15-a051-31b426fec92e",
        "type": "ENTRYPOINT",
        "inputs": [],
        "data": {
            "label": "Entrypoint Node",
            "source_handle_id": "844d992e-60ab-4af2-a8ff-52cd858386f7",
        },
        "base": None,
        "base": None,
        "definition": None,
        "display_data": {
            "position": {"x": 0.0, "y": 0.0},
        },
    }

    map_node = workflow_raw_data["nodes"][1]
    assert not DeepDiff(
        {
            "id": "bf83099a-40df-4445-b90d-1f6f1067ebe3",
            "type": "MAP",
            "inputs": [
                {
                    "id": "4c0a109f-599e-4d04-a396-a51474fc2996",
                    "key": "items",
                    "value": {
                        "rules": [
                            {
                                "type": "INPUT_VARIABLE",
                                "data": {"input_variable_id": "db2eb237-38e4-417a-8bfc-5bda0f3165ca"},
                            }
                        ],
                        "combinator": "OR",
                    },
                }
            ],
            "data": {
                "label": "Map Fruits Node",
                "error_output_id": None,
                "source_handle_id": "a2171a61-0657-43ad-b6d9-cf93ce3270d0",
                "target_handle_id": "b5e8182e-20c5-482b-b4c5-4dde48c01472",
                "variant": "INLINE",
                "workflow_raw_data": {
                    "nodes": [
                        {
                            "id": "ff9bfe6e-839d-4d40-b8fc-313b3bbd0ab0",
                            "type": "ENTRYPOINT",
                            "inputs": [],
                            "data": {
                                "label": "Entrypoint Node",
                                "source_handle_id": "520d3616-8369-4e79-9da5-3febae299c2a",
                            },
                            "display_data": {"position": {"x": 0.0, "y": 0.0}},
                            "base": None,
                            "definition": None,
                        },
                        {
                            "id": "baf6d316-dc75-41e8-96c0-015aede96309",
                            "label": "Iteration",
                            "type": "GENERIC",
                            "display_data": {"position": {"x": 0.0, "y": 0.0}},
                            "base": {
                                "name": "BaseNode",
                                "module": ["vellum", "workflows", "nodes", "bases", "base"],
                            },
                            "definition": {
                                "name": "Iteration",
                                "module": ["tests", "workflows", "basic_map_node", "workflow"],
                            },
                            "trigger": {
                                "id": "551d5528-f4e1-42ea-bde0-9de4b4968253",
                                "merge_behavior": "AWAIT_ATTRIBUTES",
                            },
                            "ports": [
                                {"id": "71ada606-d791-4a59-a252-0795c5faeeaf", "type": "DEFAULT", "name": "default"}
                            ],
                            "adornments": None,
                            "attributes": [
                                {
                                    "id": "4306b0ce-f31c-4c8f-8122-659d40e60ffe",
                                    "name": "item",
                                    "value": {
                                        "type": "WORKFLOW_INPUT",
                                        "input_variable_id": "b29bb546-9bc8-4136-857d-8c7a464ba9d4",
                                    },
                                },
                                {
                                    "id": "bca02056-0fd9-44c6-8aa9-743dd1180d48",
                                    "name": "index",
                                    "value": {
                                        "type": "WORKFLOW_INPUT",
                                        "input_variable_id": "17e7ca49-668f-450d-a792-e1f97d13db67",
                                    },
                                },
                            ],
                            "outputs": [
                                {
                                    "id": "a7bcb362-a2b8-4476-b0de-a361efeec204",
                                    "name": "count",
                                    "type": "NUMBER",
                                    "value": None,
                                }
                            ],
                        },
                        {
                            "id": "6f4883b2-70b1-4e1c-ae15-7d0f5aec810b",
                            "type": "TERMINAL",
                            "data": {
                                "label": "Final Output",
                                "name": "count",
                                "target_handle_id": "9d74571f-b7f5-4c1d-8b7c-b9c648738a4d",
                                "output_id": "2a957315-fae0-4366-8a35-f0b315c5eade",
                                "output_type": "NUMBER",
                                "node_input_id": "05f2e4cc-0e36-4c6b-a535-be38281e5280",
                            },
                            "inputs": [
                                {
                                    "id": "05f2e4cc-0e36-4c6b-a535-be38281e5280",
                                    "key": "node_input",
                                    "value": {
                                        "rules": [
                                            {
                                                "type": "NODE_OUTPUT",
                                                "data": {
                                                    "node_id": "baf6d316-dc75-41e8-96c0-015aede96309",
                                                    "output_id": "a7bcb362-a2b8-4476-b0de-a361efeec204",
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
                            "id": "b59c050b-0f6a-4153-ab58-fa051222fa05",
                            "source_node_id": "ff9bfe6e-839d-4d40-b8fc-313b3bbd0ab0",
                            "source_handle_id": "520d3616-8369-4e79-9da5-3febae299c2a",
                            "target_node_id": "baf6d316-dc75-41e8-96c0-015aede96309",
                            "target_handle_id": "551d5528-f4e1-42ea-bde0-9de4b4968253",
                            "type": "DEFAULT",
                        },
                        {
                            "id": "14152688-6996-4d64-9231-a6e66a4827eb",
                            "source_node_id": "baf6d316-dc75-41e8-96c0-015aede96309",
                            "source_handle_id": "71ada606-d791-4a59-a252-0795c5faeeaf",
                            "target_node_id": "6f4883b2-70b1-4e1c-ae15-7d0f5aec810b",
                            "target_handle_id": "9d74571f-b7f5-4c1d-8b7c-b9c648738a4d",
                            "type": "DEFAULT",
                        },
                    ],
                    "display_data": {"viewport": {"x": 0.0, "y": 0.0, "zoom": 1.0}},
                    "definition": {
                        "name": "IterationSubworkflow",
                        "module": [
                            "tests",
                            "workflows",
                            "basic_map_node",
                            "workflow",
                        ],
                    },
                },
                "input_variables": [
                    {
                        "id": "b29bb546-9bc8-4136-857d-8c7a464ba9d4",
                        "key": "item",
                        "type": "JSON",
                        "required": True,
                        "default": None,
                        "extensions": {"color": None},
                    },
                    {
                        "id": "17e7ca49-668f-450d-a792-e1f97d13db67",
                        "key": "index",
                        "type": "NUMBER",
                        "required": True,
                        "default": None,
                        "extensions": {"color": None},
                    },
                    {
                        "id": "d6fc6c7a-235f-4b98-86f3-e258d1198f93",
                        "key": "items",
                        "type": "JSON",
                        "required": True,
                        "default": None,
                        "extensions": {"color": None},
                    },
                ],
                "output_variables": [{"id": "2a957315-fae0-4366-8a35-f0b315c5eade", "key": "count", "type": "NUMBER"}],
                "concurrency": None,
                "items_input_id": "d6fc6c7a-235f-4b98-86f3-e258d1198f93",
                "item_input_id": "b29bb546-9bc8-4136-857d-8c7a464ba9d4",
                "index_input_id": "17e7ca49-668f-450d-a792-e1f97d13db67",
            },
            "display_data": {"position": {"x": 0.0, "y": 0.0}},
            "base": {
                "name": "MapNode",
                "module": ["vellum", "workflows", "nodes", "core", "map_node", "node"],
            },
            "definition": {
                "name": "MapFruitsNode",
                "module": ["tests", "workflows", "basic_map_node", "workflow"],
            },
        },
        map_node,
        ignore_order=True,
    )

    assert not DeepDiff(
        {
            "id": "bacc5d55-07d4-4a0a-a69e-831524480de5",
            "type": "TERMINAL",
            "data": {
                "label": "Final Output",
                "name": "final_value",
                "target_handle_id": "720dd872-2f3d-47b9-8245-89387f04f300",
                "output_id": "145b0b68-224b-4f83-90e6-eea3457e6c3e",
                "output_type": "JSON",
                "node_input_id": "57fe72e9-cc9f-48f2-b5ea-25ac52637a33",
            },
            "inputs": [
                {
                    "id": "57fe72e9-cc9f-48f2-b5ea-25ac52637a33",
                    "key": "node_input",
                    "value": {
                        "rules": [
                            {
                                "type": "NODE_OUTPUT",
                                "data": {
                                    "node_id": "bf83099a-40df-4445-b90d-1f6f1067ebe3",
                                    "output_id": "2a957315-fae0-4366-8a35-f0b315c5eade",
                                },
                            }
                        ],
                        "combinator": "OR",
                    },
                }
            ],
            "display_data": {"position": {"x": 0.0, "y": 0.0}},
            "base": {
                "module": [
                    "vellum",
                    "workflows",
                    "nodes",
                    "displayable",
                    "final_output_node",
                    "node",
                ],
                "name": "FinalOutputNode",
            },
            "definition": None,
        },
        workflow_raw_data["nodes"][2],
        # TODO: Fix output ID not referencing map node workflow output
        # https://app.shortcut.com/vellum/story/5667/fix-output-display-reference-on-map-nodes
        exclude_regex_paths=r"root\['inputs'\]\[0\]\['value'\]\['rules'\]\[0\]\['data'\]\['output_id'\]",
    )

    # AND each edge should be serialized correctly
    serialized_edges = workflow_raw_data["edges"]
    assert not DeepDiff(
        [
            {
                "id": "f39477f3-445a-412e-a8ab-371baa8ae990",
                "source_node_id": "c0aa464d-1685-4f15-a051-31b426fec92e",
                "source_handle_id": "844d992e-60ab-4af2-a8ff-52cd858386f7",
                "target_node_id": "bf83099a-40df-4445-b90d-1f6f1067ebe3",
                "target_handle_id": "b5e8182e-20c5-482b-b4c5-4dde48c01472",
                "type": "DEFAULT",
            },
            {
                "id": "47a34f6e-d139-4702-aa46-6212bb8a150f",
                "source_node_id": "bf83099a-40df-4445-b90d-1f6f1067ebe3",
                "source_handle_id": "a2171a61-0657-43ad-b6d9-cf93ce3270d0",
                "target_node_id": "bacc5d55-07d4-4a0a-a69e-831524480de5",
                "target_handle_id": "720dd872-2f3d-47b9-8245-89387f04f300",
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
        "name": "SimpleMapExample",
        "module": [
            "tests",
            "workflows",
            "basic_map_node",
            "workflow",
        ],
    }
