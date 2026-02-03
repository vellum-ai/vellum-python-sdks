from deepdiff import DeepDiff

from vellum.workflows.nodes.utils import ADORNMENT_MODULE_NAME
from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display

from tests.workflows.basic_code_execution_node.try_workflow import TrySimpleCodeExecutionWorkflow
from tests.workflows.basic_code_execution_node.workflow import SimpleCodeExecutionWithFilepathWorkflow
from tests.workflows.basic_code_execution_node.workflow_with_code import SimpleCodeExecutionWithCodeWorkflow


def test_serialize_workflow_with_filepath():
    # GIVEN a Workflow with a code execution node
    # WHEN we serialize it
    workflow_display = get_workflow_display(workflow_class=SimpleCodeExecutionWithFilepathWorkflow)
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

    # AND each node should be serialized correctly

    code_execution_node = next(
        n for n in workflow_raw_data["nodes"] if (n.get("base") or {}).get("name") == "CodeExecutionNode"
    )
    assert code_execution_node == {
        "id": "b4a0526b-0e31-4f63-892a-6d5197d09acf",
        "type": "CODE_EXECUTION",
        "inputs": [
            {
                "id": "e7a6c15f-083f-4775-8315-22b8fb62b9ba",
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
                "id": "1248f512-cc1b-4daa-a444-3bf7a1f1b8f9",
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
            "source_handle_id": "6aed9e19-9d26-457b-966d-0a9112f84070",
            "target_handle_id": "f1ea9f65-e225-49cc-a779-6bd0797ba22a",
            "code_input_id": "e7a6c15f-083f-4775-8315-22b8fb62b9ba",
            "runtime_input_id": "1248f512-cc1b-4daa-a444-3bf7a1f1b8f9",
            "output_type": "NUMBER",
            "packages": [{"name": "openai", "version": "1.0.0"}],
            "output_id": "730c8f17-891c-40b4-b43d-26672bd38eef",
            "log_output_id": "8eea2893-1e79-4d1c-ba51-2e045968abfb",
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
        "trigger": {
            "id": "f1ea9f65-e225-49cc-a779-6bd0797ba22a",
            "merge_behavior": "AWAIT_ANY",
        },
        "ports": [{"id": "6aed9e19-9d26-457b-966d-0a9112f84070", "name": "default", "type": "DEFAULT"}],
        "outputs": [
            {
                "id": "730c8f17-891c-40b4-b43d-26672bd38eef",
                "name": "result",
                "schema": {"type": "integer"},
                "type": "NUMBER",
                "value": None,
            },
            {
                "id": "8eea2893-1e79-4d1c-ba51-2e045968abfb",
                "name": "log",
                "schema": {"type": "string"},
                "type": "STRING",
                "value": None,
            },
        ],
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
    workflow_display = get_workflow_display(workflow_class=SimpleCodeExecutionWithCodeWorkflow)
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

    # AND each node should be serialized correctly

    code_execution_node = next(
        n for n in workflow_raw_data["nodes"] if (n.get("base") or {}).get("name") == "CodeExecutionNode"
    )
    assert code_execution_node == {
        "id": "ae9c5da6-242e-4e0d-abe6-344e2ada3ce3",
        "type": "CODE_EXECUTION",
        "inputs": [
            {
                "id": "331db512-0127-46ad-aeed-1abacb287a9e",
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
                "id": "dd7e4f60-858a-457d-9ad3-50a25871650f",
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
            "source_handle_id": "d2560e23-cbb6-4b73-b082-294982da72aa",
            "target_handle_id": "e4a738e8-bbcf-47d2-b7c9-6a034dd412f0",
            "code_input_id": "331db512-0127-46ad-aeed-1abacb287a9e",
            "runtime_input_id": "dd7e4f60-858a-457d-9ad3-50a25871650f",
            "output_type": "NUMBER",
            "packages": [],
            "output_id": "9b2b939b-c840-4e01-99c1-43a3418d7fb7",
            "log_output_id": "e3536bf9-cf37-4d16-b835-770a9ee6cc53",
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
        "trigger": {
            "id": "e4a738e8-bbcf-47d2-b7c9-6a034dd412f0",
            "merge_behavior": "AWAIT_ANY",
        },
        "ports": [{"id": "d2560e23-cbb6-4b73-b082-294982da72aa", "name": "default", "type": "DEFAULT"}],
        "outputs": [
            {
                "id": "9b2b939b-c840-4e01-99c1-43a3418d7fb7",
                "name": "result",
                "schema": {"type": "integer"},
                "type": "NUMBER",
                "value": None,
            },
            {
                "id": "e3536bf9-cf37-4d16-b835-770a9ee6cc53",
                "name": "log",
                "schema": {"type": "string"},
                "type": "STRING",
                "value": None,
            },
        ],
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
    workflow_display = get_workflow_display(workflow_class=TrySimpleCodeExecutionWorkflow)
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

    # AND each node should be serialized correctly

    code_execution_node = next(
        n for n in workflow_raw_data["nodes"] if (n.get("base") or {}).get("name") == "CodeExecutionNode"
    )
    assert code_execution_node == {
        "id": "1c910367-dff1-4466-85bc-6a8ec4ca039d",
        "type": "CODE_EXECUTION",
        "inputs": [
            {
                "id": "5049de20-77c9-4bcf-a572-260ec18c0528",
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
                "id": "167a0eb0-3bb7-4f9c-9517-15eda41b7b58",
                "key": "runtime",
                "value": {
                    "rules": [{"type": "CONSTANT_VALUE", "data": {"type": "STRING", "value": "PYTHON_3_11_6"}}],
                    "combinator": "OR",
                },
            },
        ],
        "data": {
            "label": "Simple Code Execution Node",
            "error_output_id": "b466ebdc-db85-4807-bccd-94c4d1b97478",
            "source_handle_id": "dede45ee-e17a-447c-b1d3-ed0d29ff1057",
            "target_handle_id": "f4a58613-628e-4a6d-aeae-4f81cf96bbf4",
            "code_input_id": "5049de20-77c9-4bcf-a572-260ec18c0528",
            "runtime_input_id": "167a0eb0-3bb7-4f9c-9517-15eda41b7b58",
            "output_type": "NUMBER",
            "packages": [{"name": "openai", "version": "1.0.0", "repository": "test-repo"}],
            "output_id": "a483823a-e856-4ad3-ab3b-cac3c2961536",
            "log_output_id": "0022691d-4707-476f-a9f5-4947b5e36f07",
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
                "id": "d602b4ed-fb9d-45ef-8d07-1b6c2d8cd893",
                "label": "Try Node",
                "base": {"name": "TryNode", "module": ["vellum", "workflows", "nodes", "core", "try_node", "node"]},
                "attributes": [
                    {
                        "id": "2a313b7c-accd-4af2-a05b-c73b73c222b7",
                        "name": "on_error_code",
                        "value": {"type": "CONSTANT_VALUE", "value": {"type": "JSON", "value": None}},
                    }
                ],
            }
        ],
        "trigger": {
            "id": "f4a58613-628e-4a6d-aeae-4f81cf96bbf4",
            "merge_behavior": "AWAIT_ANY",
        },
        "ports": [{"id": "dede45ee-e17a-447c-b1d3-ed0d29ff1057", "name": "default", "type": "DEFAULT"}],
        "outputs": [
            {
                "id": "a483823a-e856-4ad3-ab3b-cac3c2961536",
                "name": "result",
                "schema": {"type": "integer"},
                "type": "NUMBER",
                "value": None,
            },
            {
                "id": "0022691d-4707-476f-a9f5-4947b5e36f07",
                "name": "log",
                "schema": {"type": "string"},
                "type": "STRING",
                "value": None,
            },
        ],
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
