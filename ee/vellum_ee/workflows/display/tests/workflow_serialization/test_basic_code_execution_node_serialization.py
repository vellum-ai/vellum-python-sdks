from deepdiff import DeepDiff

from vellum.workflows.nodes.utils import ADORNMENT_MODULE_NAME
from vellum_ee.workflows.display.workflows import VellumWorkflowDisplay
from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display

from tests.workflows.basic_code_execution_node.try_workflow import TrySimpleCodeExecutionWorkflow
from tests.workflows.basic_code_execution_node.workflow import SimpleCodeExecutionWorkflow


def test_serialize_workflow():
    # GIVEN a Workflow with a code execution node
    # WHEN we serialize it
    workflow_display = get_workflow_display(
        base_display_class=VellumWorkflowDisplay, workflow_class=SimpleCodeExecutionWorkflow
    )
    serialized_workflow: dict = workflow_display.serialize()

    # THEN we should get a serialized representation of the Workflow
    assert serialized_workflow.keys() == {
        "workflow_raw_data",
        "input_variables",
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
            {"id": "ecdb8bf3-f456-400a-94af-a8f8338096b8", "key": "log", "type": "STRING"},
            {"id": "461585c0-0f65-4d18-ba69-fdfb3874d2b3", "key": "result", "type": "NUMBER"},
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
        "id": "6d94a007-9b25-4b4f-a31d-74e7965b6696",
        "type": "ENTRYPOINT",
        "inputs": [],
        "data": {
            "label": "Entrypoint Node",
            "source_handle_id": "5474e6da-f14c-458f-a82b-7a05fdfe3e5b",
        },
        "definition": {
            "bases": [],
            "module": [
                "vellum",
                "workflows",
                "nodes",
                "bases",
                "base",
            ],
            "name": "BaseNode",
        },
        "display_data": {
            "position": {"x": 0.0, "y": 0.0},
        },
    }

    code_execution_node = workflow_raw_data["nodes"][1]
    assert code_execution_node == {
        "id": "c07155b3-7d99-4d2d-9b29-b5298013aa46",
        "type": "CODE_EXECUTION",
        "inputs": [
            {
                "id": "f2e8a4fa-b54e-41e9-b314-0e5443519ac7",
                "key": "code",
                "value": {
                    "rules": [
                        {
                            "type": "CONSTANT_VALUE",
                            "data": {"type": "STRING", "value": "# flake8: noqa\ndef main():\n    return 0\n"},
                        }
                    ],
                    "combinator": "OR",
                },
            },
            {
                "id": "19d64948-f22b-4103-a7f5-3add184b31cc",
                "key": "runtime",
                "value": {
                    "rules": [{"type": "CONSTANT_VALUE", "data": {"type": "STRING", "value": "PYTHON_3_11_6"}}],
                    "combinator": "OR",
                },
            },
        ],
        "data": {
            "label": "Simple Code Execution Node",
            "error_output_id": None,
            "source_handle_id": "832f81ec-427b-42a8-825c-e62c43c1f961",
            "target_handle_id": "e02a2701-22c0-4533-8b00-175998e7350a",
            "code_input_id": "f2e8a4fa-b54e-41e9-b314-0e5443519ac7",
            "runtime_input_id": "19d64948-f22b-4103-a7f5-3add184b31cc",
            "output_type": "NUMBER",
            "packages": [],
            "output_id": "0fde9607-353f-42c2-85c4-20f720ebc1ec",
            "log_output_id": "7cac05e3-b7c3-475e-8df8-422b496c3398",
        },
        "display_data": {"position": {"x": 0.0, "y": 0.0}},
        "definition": {
            "bases": [
                {
                    "module": [
                        "vellum",
                        "workflows",
                        "nodes",
                        "displayable",
                        "code_execution_node",
                        "node",
                    ],
                    "name": "CodeExecutionNode",
                }
            ],
            "module": [
                "tests",
                "workflows",
                "basic_code_execution_node",
                "workflow",
            ],
            "name": "SimpleCodeExecutionNode",
        },
    }

    assert not DeepDiff(
        [
            {
                "id": "e81b713c-b356-4654-9715-e8c54e3ca267",
                "type": "TERMINAL",
                "data": {
                    "label": "Final Output",
                    "name": "result",
                    "target_handle_id": "c0890e2a-8827-4f99-8e9a-144c7e937f33",
                    "output_id": "461585c0-0f65-4d18-ba69-fdfb3874d2b3",
                    "output_type": "NUMBER",
                    "node_input_id": "c28cc3c7-1285-4be3-ac51-c73456cee961",
                },
                "inputs": [
                    {
                        "id": "c28cc3c7-1285-4be3-ac51-c73456cee961",
                        "key": "node_input",
                        "value": {
                            "rules": [
                                {
                                    "type": "NODE_OUTPUT",
                                    "data": {
                                        "node_id": "c07155b3-7d99-4d2d-9b29-b5298013aa46",
                                        "output_id": "0fde9607-353f-42c2-85c4-20f720ebc1ec",
                                    },
                                }
                            ],
                            "combinator": "OR",
                        },
                    }
                ],
                "display_data": {"position": {"x": 0.0, "y": 0.0}},
                "definition": {
                    "bases": [
                        {
                            "bases": [],
                            "module": [
                                "vellum",
                                "workflows",
                                "nodes",
                                "bases",
                                "base",
                            ],
                            "name": "BaseNode",
                        },
                    ],
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
            },
            {
                "id": "59e52e86-8059-4f32-b1f0-54f500b167a9",
                "type": "TERMINAL",
                "data": {
                    "label": "Final Output",
                    "name": "log",
                    "target_handle_id": "bb56d2ed-f5e2-4c00-a2ef-445a2210d6d1",
                    "output_id": "ecdb8bf3-f456-400a-94af-a8f8338096b8",
                    "output_type": "STRING",
                    "node_input_id": "e34369ff-8795-4f4f-8f40-c535a1c368bf",
                },
                "inputs": [
                    {
                        "id": "e34369ff-8795-4f4f-8f40-c535a1c368bf",
                        "key": "node_input",
                        "value": {
                            "rules": [
                                {
                                    "type": "NODE_OUTPUT",
                                    "data": {
                                        "node_id": "c07155b3-7d99-4d2d-9b29-b5298013aa46",
                                        "output_id": "7cac05e3-b7c3-475e-8df8-422b496c3398",
                                    },
                                }
                            ],
                            "combinator": "OR",
                        },
                    }
                ],
                "display_data": {"position": {"x": 0.0, "y": 0.0}},
                "definition": {
                    "bases": [
                        {
                            "bases": [],
                            "module": [
                                "vellum",
                                "workflows",
                                "nodes",
                                "bases",
                                "base",
                            ],
                            "name": "BaseNode",
                        },
                    ],
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
            },
        ],
        workflow_raw_data["nodes"][2:],
        ignore_order=True,
    )

    # AND each edge should be serialized correctly
    serialized_edges = workflow_raw_data["edges"]
    assert not DeepDiff(
        [
            {
                "id": "7cb7522b-3d91-474c-a3ad-6170b8d0def1",
                "source_node_id": "6d94a007-9b25-4b4f-a31d-74e7965b6696",
                "source_handle_id": "5474e6da-f14c-458f-a82b-7a05fdfe3e5b",
                "target_node_id": "c07155b3-7d99-4d2d-9b29-b5298013aa46",
                "target_handle_id": "e02a2701-22c0-4533-8b00-175998e7350a",
                "type": "DEFAULT",
            },
            {
                "id": "1b2ef8d2-9220-4aa7-9f09-fced39002337",
                "source_node_id": "c07155b3-7d99-4d2d-9b29-b5298013aa46",
                "source_handle_id": "832f81ec-427b-42a8-825c-e62c43c1f961",
                "target_node_id": "59e52e86-8059-4f32-b1f0-54f500b167a9",
                "target_handle_id": "bb56d2ed-f5e2-4c00-a2ef-445a2210d6d1",
                "type": "DEFAULT",
            },
            {
                "id": "caa519a9-3c17-45f2-b67f-7dc656780300",
                "source_node_id": "c07155b3-7d99-4d2d-9b29-b5298013aa46",
                "source_handle_id": "832f81ec-427b-42a8-825c-e62c43c1f961",
                "target_node_id": "e81b713c-b356-4654-9715-e8c54e3ca267",
                "target_handle_id": "c0890e2a-8827-4f99-8e9a-144c7e937f33",
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
        "name": "SimpleCodeExecutionWorkflow",
        "module": [
            "tests",
            "workflows",
            "basic_code_execution_node",
            "workflow",
        ],
    }


def test_serialize_workflow__try_wrapped():
    # GIVEN a Workflow with a code execution node
    # WHEN we serialize it
    workflow_display = get_workflow_display(
        base_display_class=VellumWorkflowDisplay, workflow_class=TrySimpleCodeExecutionWorkflow
    )
    serialized_workflow: dict = workflow_display.serialize()

    # THEN we should get a serialized representation of the Workflow
    assert serialized_workflow.keys() == {
        "workflow_raw_data",
        "input_variables",
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
            {"id": "5fbd27a0-9831-49c7-93c8-9c2a28c78696", "key": "log", "type": "STRING"},
            {"id": "400f9ffe-e700-4204-a810-e06123565947", "key": "result", "type": "NUMBER"},
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
        "id": "1b300de0-cf41-493f-ab41-6fdadf406f6a",
        "type": "ENTRYPOINT",
        "inputs": [],
        "data": {
            "label": "Entrypoint Node",
            "source_handle_id": "8cd1e612-39aa-4471-88cf-f7999b713fa6",
        },
        "definition": {
            "bases": [],
            "module": [
                "vellum",
                "workflows",
                "nodes",
                "bases",
                "base",
            ],
            "name": "BaseNode",
        },
        "display_data": {
            "position": {"x": 0.0, "y": 0.0},
        },
    }

    code_execution_node = workflow_raw_data["nodes"][1]
    assert code_execution_node == {
        "id": "c07155b3-7d99-4d2d-9b29-b5298013aa46",
        "type": "CODE_EXECUTION",
        "inputs": [
            {
                "id": "f2e8a4fa-b54e-41e9-b314-0e5443519ac7",
                "key": "code",
                "value": {
                    "rules": [
                        {
                            "type": "CONSTANT_VALUE",
                            "data": {"type": "STRING", "value": "# flake8: noqa\ndef main():\n    return 0\n"},
                        }
                    ],
                    "combinator": "OR",
                },
            },
            {
                "id": "19d64948-f22b-4103-a7f5-3add184b31cc",
                "key": "runtime",
                "value": {
                    "rules": [{"type": "CONSTANT_VALUE", "data": {"type": "STRING", "value": "PYTHON_3_11_6"}}],
                    "combinator": "OR",
                },
            },
        ],
        "data": {
            "label": "Simple Code Execution Node",
            "error_output_id": "7236b0f4-b6bb-4103-a993-a8908d597dc3",
            "source_handle_id": "832f81ec-427b-42a8-825c-e62c43c1f961",
            "target_handle_id": "e02a2701-22c0-4533-8b00-175998e7350a",
            "code_input_id": "f2e8a4fa-b54e-41e9-b314-0e5443519ac7",
            "runtime_input_id": "19d64948-f22b-4103-a7f5-3add184b31cc",
            "output_type": "NUMBER",
            "packages": [],
            "output_id": "0fde9607-353f-42c2-85c4-20f720ebc1ec",
            "log_output_id": "7cac05e3-b7c3-475e-8df8-422b496c3398",
        },
        "display_data": {"position": {"x": 0.0, "y": 0.0}},
        "definition": {
            "bases": [
                {
                    "module": [
                        "vellum",
                        "workflows",
                        "nodes",
                        "displayable",
                        "code_execution_node",
                        "node",
                    ],
                    "name": "CodeExecutionNode",
                }
            ],
            "module": [
                "tests",
                "workflows",
                "basic_code_execution_node",
                "try_workflow",
                "SimpleCodeExecutionNode",
                ADORNMENT_MODULE_NAME,
            ],
            "name": "TryNode",
        },
    }

    final_output_nodes = workflow_raw_data["nodes"][2:]
    assert not DeepDiff(
        [
            {
                "id": "af4fc1ef-7701-43df-b5e7-4f354f707db2",
                "type": "TERMINAL",
                "definition": {
                    "bases": [
                        {
                            "bases": [],
                            "module": [
                                "vellum",
                                "workflows",
                                "nodes",
                                "bases",
                                "base",
                            ],
                            "name": "BaseNode",
                        },
                    ],
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
                "data": {
                    "label": "Final Output",
                    "name": "log",
                    "target_handle_id": "d243df8d-46f6-4928-ac31-7c775c5d73a9",
                    "output_id": "5fbd27a0-9831-49c7-93c8-9c2a28c78696",
                    "output_type": "STRING",
                    "node_input_id": "569e1c05-53fa-413b-abf0-0353eaa44208",
                },
                "inputs": [
                    {
                        "id": "569e1c05-53fa-413b-abf0-0353eaa44208",
                        "key": "node_input",
                        "value": {
                            "rules": [
                                {
                                    "type": "NODE_OUTPUT",
                                    "data": {
                                        "node_id": "c07155b3-7d99-4d2d-9b29-b5298013aa46",
                                        "output_id": "7cac05e3-b7c3-475e-8df8-422b496c3398",
                                    },
                                }
                            ],
                            "combinator": "OR",
                        },
                    }
                ],
                "display_data": {"position": {"x": 0.0, "y": 0.0}},
            },
            {
                "id": "4cbfa5f7-fc12-4ab2-81cb-168c5caef4f0",
                "type": "TERMINAL",
                "definition": {
                    "bases": [
                        {
                            "bases": [],
                            "module": [
                                "vellum",
                                "workflows",
                                "nodes",
                                "bases",
                                "base",
                            ],
                            "name": "BaseNode",
                        },
                    ],
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
                "data": {
                    "label": "Final Output",
                    "name": "result",
                    "target_handle_id": "9c43709e-25cb-4548-b840-3fcf6a1c9f3e",
                    "output_id": "400f9ffe-e700-4204-a810-e06123565947",
                    "output_type": "NUMBER",
                    "node_input_id": "3d6cb7ef-985f-48f1-ad23-de49be60666a",
                },
                "inputs": [
                    {
                        "id": "3d6cb7ef-985f-48f1-ad23-de49be60666a",
                        "key": "node_input",
                        "value": {
                            "rules": [
                                {
                                    "type": "NODE_OUTPUT",
                                    "data": {
                                        "node_id": "c07155b3-7d99-4d2d-9b29-b5298013aa46",
                                        "output_id": "0fde9607-353f-42c2-85c4-20f720ebc1ec",
                                    },
                                }
                            ],
                            "combinator": "OR",
                        },
                    }
                ],
                "display_data": {"position": {"x": 0.0, "y": 0.0}},
            },
        ],
        final_output_nodes,
        ignore_order=True,
    )

    # AND each edge should be serialized correctly
    serialized_edges = workflow_raw_data["edges"]
    assert not DeepDiff(
        [
            {
                "id": "a95418ec-d44e-48e1-bb5e-b5b3cb060c38",
                "source_node_id": "1b300de0-cf41-493f-ab41-6fdadf406f6a",
                "source_handle_id": "8cd1e612-39aa-4471-88cf-f7999b713fa6",
                "target_node_id": "c07155b3-7d99-4d2d-9b29-b5298013aa46",
                "target_handle_id": "e02a2701-22c0-4533-8b00-175998e7350a",
                "type": "DEFAULT",
            },
            {
                "id": "ac96ad63-d91f-465c-9c52-629877e56492",
                "source_node_id": "c07155b3-7d99-4d2d-9b29-b5298013aa46",
                "source_handle_id": "832f81ec-427b-42a8-825c-e62c43c1f961",
                "target_node_id": "af4fc1ef-7701-43df-b5e7-4f354f707db2",
                "target_handle_id": "d243df8d-46f6-4928-ac31-7c775c5d73a9",
                "type": "DEFAULT",
            },
            {
                "id": "636f4540-e0e3-4740-af72-45f78b700cf9",
                "source_node_id": "c07155b3-7d99-4d2d-9b29-b5298013aa46",
                "source_handle_id": "832f81ec-427b-42a8-825c-e62c43c1f961",
                "target_node_id": "4cbfa5f7-fc12-4ab2-81cb-168c5caef4f0",
                "target_handle_id": "9c43709e-25cb-4548-b840-3fcf6a1c9f3e",
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
        "name": "TrySimpleCodeExecutionWorkflow",
        "module": [
            "tests",
            "workflows",
            "basic_code_execution_node",
            "try_workflow",
        ],
    }
