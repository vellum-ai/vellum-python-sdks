from deepdiff import DeepDiff

from vellum.workflows.nodes.utils import ADORNMENT_MODULE_NAME
from vellum_ee.workflows.display.workflows import VellumWorkflowDisplay
from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display

from tests.workflows.basic_code_execution_node.try_workflow import TrySimpleCodeExecutionWorkflow
from tests.workflows.basic_code_execution_node.workflow import SimpleCodeExecutionWithFilepathWorkflow
from tests.workflows.basic_code_execution_node.workflow_with_code import SimpleCodeExecutionWithCodeWorkflow


def test_serialize_workflow_with_filepath():
    # GIVEN a Workflow with a code execution node
    # WHEN we serialize it
    workflow_display = get_workflow_display(
        base_display_class=VellumWorkflowDisplay, workflow_class=SimpleCodeExecutionWithFilepathWorkflow
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
    assert len(input_variables) == 0

    # AND its output variables should be what we expect
    output_variables = serialized_workflow["output_variables"]
    assert len(output_variables) == 2
    assert not DeepDiff(
        [
            {"id": "1cee930f-342f-421c-89fc-ff212b3764bb", "key": "log", "type": "STRING"},
            {"id": "f6a3e3e0-f83f-4491-8b7a-b20fddd7160c", "key": "result", "type": "NUMBER"},
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
        "id": "bd18f11c-5f7a-45d5-9970-0b1cf10d3761",
        "type": "ENTRYPOINT",
        "inputs": [],
        "data": {"label": "Entrypoint Node", "source_handle_id": "118e4298-aa79-467c-b8b4-2df540905e86"},
        "display_data": {"position": {"x": 0.0, "y": 0.0}},
        "base": None,
        "definition": None,
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
            "packages": [{"name": "openai", "version": "1.0.0"}],
            "output_id": "0fde9607-353f-42c2-85c4-20f720ebc1ec",
            "log_output_id": "7cac05e3-b7c3-475e-8df8-422b496c3398",
        },
        "display_data": {"position": {"x": 0.0, "y": 0.0}},
        "base": {
            "module": [
                "vellum",
                "workflows",
                "nodes",
                "displayable",
                "code_execution_node",
                "node",
            ],
            "name": "CodeExecutionNode",
        },
        "definition": {
            "module": ["tests", "workflows", "basic_code_execution_node", "workflow"],
            "name": "SimpleCodeExecutionNode",
        },
    }
    assert not DeepDiff(
        [
            {
                "id": "994d5c2e-00d2-4dff-9a9d-804766d03698",
                "type": "TERMINAL",
                "data": {
                    "label": "Final Output",
                    "name": "result",
                    "target_handle_id": "30fb0f4a-61c3-49de-a0aa-7dfdcee6ea07",
                    "output_id": "f6a3e3e0-f83f-4491-8b7a-b20fddd7160c",
                    "output_type": "NUMBER",
                    "node_input_id": "529bdd20-0985-4c99-87dc-590907937c1d",
                },
                "inputs": [
                    {
                        "id": "529bdd20-0985-4c99-87dc-590907937c1d",
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
                "base": {
                    "name": "FinalOutputNode",
                    "module": ["vellum", "workflows", "nodes", "displayable", "final_output_node", "node"],
                },
                "definition": None,
            },
            {
                "id": "c6e3aced-1fc9-48d2-ae55-d2a880e359cb",
                "type": "TERMINAL",
                "data": {
                    "label": "Final Output",
                    "name": "log",
                    "target_handle_id": "1e126004-9de7-42c0-b1e1-87f9eb0642e2",
                    "output_id": "1cee930f-342f-421c-89fc-ff212b3764bb",
                    "output_type": "STRING",
                    "node_input_id": "09501b65-d9b3-4920-81d4-96f93c840667",
                },
                "inputs": [
                    {
                        "id": "09501b65-d9b3-4920-81d4-96f93c840667",
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
                "base": {
                    "name": "FinalOutputNode",
                    "module": ["vellum", "workflows", "nodes", "displayable", "final_output_node", "node"],
                },
                "definition": None,
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
                "id": "32673715-d88c-4727-b284-21ae4efe3f85",
                "source_node_id": "bd18f11c-5f7a-45d5-9970-0b1cf10d3761",
                "source_handle_id": "118e4298-aa79-467c-b8b4-2df540905e86",
                "target_node_id": "c07155b3-7d99-4d2d-9b29-b5298013aa46",
                "target_handle_id": "e02a2701-22c0-4533-8b00-175998e7350a",
                "type": "DEFAULT",
            },
            {
                "id": "d1e66711-75b3-41c3-beb6-424894fdd307",
                "source_node_id": "c07155b3-7d99-4d2d-9b29-b5298013aa46",
                "source_handle_id": "832f81ec-427b-42a8-825c-e62c43c1f961",
                "target_node_id": "994d5c2e-00d2-4dff-9a9d-804766d03698",
                "target_handle_id": "30fb0f4a-61c3-49de-a0aa-7dfdcee6ea07",
                "type": "DEFAULT",
            },
            {
                "id": "67d4c43e-80f9-4875-b6ab-9ecbba19fc7a",
                "source_node_id": "c07155b3-7d99-4d2d-9b29-b5298013aa46",
                "source_handle_id": "832f81ec-427b-42a8-825c-e62c43c1f961",
                "target_node_id": "c6e3aced-1fc9-48d2-ae55-d2a880e359cb",
                "target_handle_id": "1e126004-9de7-42c0-b1e1-87f9eb0642e2",
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
        "name": "SimpleCodeExecutionWithFilepathWorkflow",
        "module": [
            "tests",
            "workflows",
            "basic_code_execution_node",
            "workflow",
        ],
    }


def test_serialize_workflow_with_code():
    # GIVEN a Workflow with a code execution node
    # WHEN we serialize it
    workflow_display = get_workflow_display(
        base_display_class=VellumWorkflowDisplay, workflow_class=SimpleCodeExecutionWithCodeWorkflow
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
    assert len(input_variables) == 0

    # AND its output variables should be what we expect
    output_variables = serialized_workflow["output_variables"]
    assert len(output_variables) == 2
    assert not DeepDiff(
        [
            {"id": "283d6849-f3ed-4beb-b261-cf70f90e8d10", "key": "result", "type": "NUMBER"},
            {"id": "4c136180-050b-4422-a7a4-2a1c6729042c", "key": "log", "type": "STRING"},
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
        "id": "22555158-d8ba-41b4-a6fc-87c3b25bd073",
        "type": "ENTRYPOINT",
        "inputs": [],
        "data": {"label": "Entrypoint Node", "source_handle_id": "e82390bb-c68c-48c1-9f87-7fbfff494c45"},
        "display_data": {"position": {"x": 0.0, "y": 0.0}},
        "base": None,
        "definition": None,
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
                            "data": {"type": "STRING", "value": 'def main() -> str:\n    return "Hello, World!"\n'},
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
        "base": {
            "name": "CodeExecutionNode",
            "module": ["vellum", "workflows", "nodes", "displayable", "code_execution_node", "node"],
        },
        "definition": {
            "name": "SimpleCodeExecutionNode",
            "module": ["tests", "workflows", "basic_code_execution_node", "workflow_with_code"],
        },
    }
    assert not DeepDiff(
        [
            {
                "id": "52f285fe-1f52-4920-b01b-499762b95220",
                "type": "TERMINAL",
                "data": {
                    "label": "Final Output",
                    "name": "result",
                    "target_handle_id": "de8f2cc2-8c32-4782-87d5-4eb5afcd42e3",
                    "output_id": "283d6849-f3ed-4beb-b261-cf70f90e8d10",
                    "output_type": "NUMBER",
                    "node_input_id": "101d5222-8578-413a-be80-b1acf7559a0d",
                },
                "inputs": [
                    {
                        "id": "101d5222-8578-413a-be80-b1acf7559a0d",
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
                "base": {
                    "name": "FinalOutputNode",
                    "module": ["vellum", "workflows", "nodes", "displayable", "final_output_node", "node"],
                },
                "definition": None,
            },
            {
                "id": "eccf97c7-e766-471f-9703-4d2595800e66",
                "type": "TERMINAL",
                "data": {
                    "label": "Final Output",
                    "name": "log",
                    "target_handle_id": "6b7d7f2c-5cc8-4005-9e66-cdb2c97b1998",
                    "output_id": "4c136180-050b-4422-a7a4-2a1c6729042c",
                    "output_type": "STRING",
                    "node_input_id": "de7ea5c4-da2f-4cfd-9192-0257d0f9ba53",
                },
                "inputs": [
                    {
                        "id": "de7ea5c4-da2f-4cfd-9192-0257d0f9ba53",
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
                "base": {
                    "name": "FinalOutputNode",
                    "module": ["vellum", "workflows", "nodes", "displayable", "final_output_node", "node"],
                },
                "definition": None,
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
                "id": "72f2a432-621f-4a3a-8b41-17a5168cba69",
                "source_node_id": "22555158-d8ba-41b4-a6fc-87c3b25bd073",
                "source_handle_id": "e82390bb-c68c-48c1-9f87-7fbfff494c45",
                "target_node_id": "c07155b3-7d99-4d2d-9b29-b5298013aa46",
                "target_handle_id": "e02a2701-22c0-4533-8b00-175998e7350a",
                "type": "DEFAULT",
            },
            {
                "id": "2ac757e4-87c3-402c-928f-a3845df10c9f",
                "source_node_id": "c07155b3-7d99-4d2d-9b29-b5298013aa46",
                "source_handle_id": "832f81ec-427b-42a8-825c-e62c43c1f961",
                "target_node_id": "eccf97c7-e766-471f-9703-4d2595800e66",
                "target_handle_id": "6b7d7f2c-5cc8-4005-9e66-cdb2c97b1998",
                "type": "DEFAULT",
            },
            {
                "id": "fcc6353a-265c-4a65-9e70-4eb92a04e4e1",
                "source_node_id": "c07155b3-7d99-4d2d-9b29-b5298013aa46",
                "source_handle_id": "832f81ec-427b-42a8-825c-e62c43c1f961",
                "target_node_id": "52f285fe-1f52-4920-b01b-499762b95220",
                "target_handle_id": "de8f2cc2-8c32-4782-87d5-4eb5afcd42e3",
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
        "name": "SimpleCodeExecutionWithCodeWorkflow",
        "module": ["tests", "workflows", "basic_code_execution_node", "workflow_with_code"],
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
        "base": None,
        "definition": None,
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
            "packages": [{"name": "openai", "version": "1.0.0"}],
            "output_id": "0fde9607-353f-42c2-85c4-20f720ebc1ec",
            "log_output_id": "7cac05e3-b7c3-475e-8df8-422b496c3398",
        },
        "display_data": {"position": {"x": 0.0, "y": 0.0}},
        "base": {
            "module": [
                "vellum",
                "workflows",
                "nodes",
                "displayable",
                "code_execution_node",
                "node",
            ],
            "name": "CodeExecutionNode",
        },
        "definition": {
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
        "adornments": [
            {
                "id": "3344083c-a32c-4a32-920b-0fb5093448fa",
                "label": "TryNode",
                "base": {"name": "TryNode", "module": ["vellum", "workflows", "nodes", "core", "try_node", "node"]},
                "attributes": [
                    {
                        "id": "ab2fbab0-e2a0-419b-b1ef-ce11ecf11e90",
                        "name": "on_error_code",
                        "value": {"type": "CONSTANT_VALUE", "value": {"type": "JSON", "value": None}},
                    }
                ],
            }
        ],
    }

    final_output_nodes = workflow_raw_data["nodes"][2:]
    assert not DeepDiff(
        [
            {
                "id": "af4fc1ef-7701-43df-b5e7-4f354f707db2",
                "type": "TERMINAL",
                "data": {
                    "label": "Final Output",
                    "name": "log",
                    "target_handle_id": "d243df8d-46f6-4928-ac31-7c775c5d73a9",
                    "output_id": "5fbd27a0-9831-49c7-93c8-9c2a28c78696",
                    "output_type": "STRING",
                    "node_input_id": "a6ffaacf-1284-4e70-907e-042bb281e6fa",
                },
                "inputs": [
                    {
                        "id": "a6ffaacf-1284-4e70-907e-042bb281e6fa",
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
                "base": {
                    "name": "FinalOutputNode",
                    "module": ["vellum", "workflows", "nodes", "displayable", "final_output_node", "node"],
                },
                "definition": None,
            },
            {
                "id": "4cbfa5f7-fc12-4ab2-81cb-168c5caef4f0",
                "type": "TERMINAL",
                "data": {
                    "label": "Final Output",
                    "name": "result",
                    "target_handle_id": "9c43709e-25cb-4548-b840-3fcf6a1c9f3e",
                    "output_id": "400f9ffe-e700-4204-a810-e06123565947",
                    "output_type": "NUMBER",
                    "node_input_id": "2cbb7351-a3e8-4a6b-b33e-204b04da7ad6",
                },
                "inputs": [
                    {
                        "id": "2cbb7351-a3e8-4a6b-b33e-204b04da7ad6",
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
                "base": {
                    "name": "FinalOutputNode",
                    "module": ["vellum", "workflows", "nodes", "displayable", "final_output_node", "node"],
                },
                "definition": None,
            },
        ],
        sorted(final_output_nodes, key=lambda x: x["id"], reverse=True),
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
