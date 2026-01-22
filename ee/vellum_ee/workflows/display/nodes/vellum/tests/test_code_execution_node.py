import pytest
from uuid import UUID
from typing import Type

from vellum.client.core.api_error import ApiError
from vellum.workflows.environment import EnvironmentVariables
from vellum.workflows.nodes.displayable.code_execution_node.node import CodeExecutionNode
from vellum.workflows.references.vellum_secret import VellumSecretReference
from vellum.workflows.state.base import BaseState
from vellum.workflows.workflows.base import BaseWorkflow
from vellum_ee.workflows.display.nodes.vellum.code_execution_node import BaseCodeExecutionNodeDisplay
from vellum_ee.workflows.display.utils.exceptions import NodeValidationError
from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display


def _no_display_class(Node: Type[CodeExecutionNode]):
    return None


def _display_class_with_node_input_ids_by_name(Node: Type[CodeExecutionNode]):
    class CodeExecutionNodeDisplay(BaseCodeExecutionNodeDisplay[Node]):  # type: ignore[valid-type]
        node_input_ids_by_name = {"foo": UUID("fba6a4d5-835a-4e99-afb7-f6a4aed15110")}

    return CodeExecutionNodeDisplay


def _display_class_with_node_input_ids_by_name_with_inputs_prefix(Node: Type[CodeExecutionNode]):
    class CodeExecutionNodeDisplay(BaseCodeExecutionNodeDisplay[Node]):  # type: ignore[valid-type]
        node_input_ids_by_name = {"code_inputs.foo": UUID("fba6a4d5-835a-4e99-afb7-f6a4aed15110")}

    return CodeExecutionNodeDisplay


@pytest.mark.parametrize(
    ["GetDisplayClass", "expected_input_id"],
    [
        (_no_display_class, "20ff166f-af59-4515-8ff5-205226c01aa4"),
        (_display_class_with_node_input_ids_by_name, "fba6a4d5-835a-4e99-afb7-f6a4aed15110"),
        (_display_class_with_node_input_ids_by_name_with_inputs_prefix, "fba6a4d5-835a-4e99-afb7-f6a4aed15110"),
    ],
    ids=[
        "no_display_class",
        "display_class_with_node_input_ids_by_name",
        "display_class_with_node_input_ids_by_name_with_inputs_prefix",
    ],
)
def test_serialize_node__code_node_inputs(GetDisplayClass, expected_input_id):
    # GIVEN a code node with inputs
    class MyCodeExecutionNode(CodeExecutionNode):
        code_inputs = {"foo": "bar"}

    # AND a workflow with the code node
    class Workflow(BaseWorkflow):
        graph = MyCodeExecutionNode

    # AND a display class
    GetDisplayClass(MyCodeExecutionNode)

    # WHEN the workflow is serialized
    workflow_display = get_workflow_display(workflow_class=Workflow)
    serialized_workflow: dict = workflow_display.serialize()

    # THEN the node should properly serialize the inputs
    my_code_execution_node = next(
        node for node in serialized_workflow["workflow_raw_data"]["nodes"] if node["type"] == "CODE_EXECUTION"
    )

    assert my_code_execution_node["inputs"] == [
        {
            "id": expected_input_id,
            "key": "foo",
            "value": {
                "combinator": "OR",
                "rules": [
                    {
                        "type": "CONSTANT_VALUE",
                        "data": {
                            "type": "STRING",
                            "value": "bar",
                        },
                    }
                ],
            },
        },
        {
            "id": "50678b9f-bdea-41c0-bc3d-425ea38466ee",
            "key": "code",
            "value": {
                "combinator": "OR",
                "rules": [
                    {
                        "type": "CONSTANT_VALUE",
                        "data": {
                            "type": "STRING",
                            "value": "",
                        },
                    }
                ],
            },
        },
        {
            "id": "6d2840f3-a5c1-4376-8616-ced4fffc6cf2",
            "key": "runtime",
            "value": {
                "combinator": "OR",
                "rules": [
                    {
                        "type": "CONSTANT_VALUE",
                        "data": {
                            "type": "STRING",
                            "value": "PYTHON_3_11_6",
                        },
                    }
                ],
            },
        },
    ]


def test_serialize_node__with_unresolved_secret_references(vellum_client):
    # GIVEN a node has access to a secret reference
    class MyNode(CodeExecutionNode):
        code_inputs = {"api_key": VellumSecretReference("MY_API_KEY")}

    # AND the secret is not found
    vellum_client.workspace_secrets.retrieve.side_effect = ApiError(
        status_code=404,
        body="Secret not found",
    )

    # AND a workflow with the code node
    class Workflow(BaseWorkflow):
        graph = MyNode

    # WHEN we serialize the workflow
    workflow_display = get_workflow_display(workflow_class=Workflow)
    data: dict = workflow_display.serialize()

    # THEN the condition should be serialized correctly
    node = next(node for node in data["workflow_raw_data"]["nodes"] if node["type"] == "CODE_EXECUTION")
    assert node["inputs"][0]["value"] == {
        "combinator": "OR",
        "rules": [
            {
                "type": "WORKSPACE_SECRET",
                "data": {
                    "type": "STRING",
                    "workspace_secret_id": None,
                },
            }
        ],
    }

    # AND we should have a warning of the invalid reference
    # TODO: Come up with a proposal for how nodes should propagate warnings
    # warnings = list(workflow_display.errors)
    # assert len(warnings) == 1
    # assert "Failed to resolve secret reference 'MY_API_KEY'" in str(warnings[0])


def test_serialize_node__with_non_exist_code_input_path():
    # GIVEN a code node with a non-existent code input path
    class MyNode(CodeExecutionNode):
        filepath = "non_existent_file.py"

    # AND a workflow with the code node
    class Workflow(BaseWorkflow):
        graph = MyNode

    # WHEN we serialize the workflow
    workflow_display = get_workflow_display(workflow_class=Workflow)
    with pytest.raises(NodeValidationError) as exc_info:
        workflow_display.serialize()
    assert "Filepath 'non_existent_file.py' does not exist" in str(exc_info.value)


def test_serialize_node__with_environment_variable_references():
    """
    Tests that environment variable references in code node inputs serialize correctly.
    """

    # GIVEN a code node with environment variable references in code_inputs
    class MyCodeExecutionNode(CodeExecutionNode):
        code_inputs = {
            "api_key": EnvironmentVariables.get("MY_API_KEY"),
            "other_config": {"nested_key": EnvironmentVariables.get("NESTED_KEY")},
        }

    # AND a workflow with the code node
    class Workflow(BaseWorkflow):
        graph = MyCodeExecutionNode

    # WHEN the workflow is serialized
    workflow_display = get_workflow_display(workflow_class=Workflow)
    serialized_workflow: dict = workflow_display.serialize()

    # THEN the node should properly serialize the environment variable references
    my_code_execution_node = next(
        node for node in serialized_workflow["workflow_raw_data"]["nodes"] if node["type"] == "CODE_EXECUTION"
    )

    # AND the api_key input should be serialized as an ENVIRONMENT_VARIABLE
    api_key_input = next(inp for inp in my_code_execution_node["inputs"] if inp["key"] == "api_key")
    assert api_key_input["value"] == {
        "combinator": "OR",
        "rules": [
            {
                "type": "ENVIRONMENT_VARIABLE",
                "data": {
                    "environment_variable": "MY_API_KEY",
                },
            }
        ],
    }

    # AND the nested environment variable should also be serialized correctly
    other_config_input = next(inp for inp in my_code_execution_node["inputs"] if inp["key"] == "other_config")
    assert other_config_input["value"]["combinator"] == "OR"
    assert len(other_config_input["value"]["rules"]) == 1
    assert other_config_input["value"]["rules"][0]["type"] == "CONSTANT_VALUE"
    nested_data = other_config_input["value"]["rules"][0]["data"]
    assert nested_data["type"] == "JSON"
    assert nested_data["value"]["type"] == "DICTIONARY_REFERENCE"
    assert len(nested_data["value"]["entries"]) == 1
    assert nested_data["value"]["entries"][0]["key"] == "nested_key"
    assert nested_data["value"]["entries"][0]["value"]["type"] == "ENVIRONMENT_VARIABLE"
    assert nested_data["value"]["entries"][0]["value"]["environment_variable"] == "NESTED_KEY"


def test_serialize_node__with_non_exist_code_input_path_with_dry_run():
    # GIVEN a code node with a non-existent code input path
    class MyNode(CodeExecutionNode):
        filepath = "non_existent_file.py"

    # AND a workflow with the code node
    class Workflow(BaseWorkflow):
        graph = MyNode

    # WHEN we serialize the workflow with dry_run=True
    workflow_display = get_workflow_display(workflow_class=Workflow, dry_run=True)
    data: dict = workflow_display.serialize()

    # THEN the workflow should not raise an error
    assert data == {
        "workflow_raw_data": {
            "nodes": [
                {
                    "id": "9b9e2a5d-01a4-46b2-80a3-d9484b2c0e08",
                    "type": "ENTRYPOINT",
                    "inputs": [],
                    "data": {"label": "Entrypoint Node", "source_handle_id": "3e2a3f52-5047-4e2e-9a21-37bd43c63250"},
                    "display_data": {"position": {"x": 0.0, "y": 0.0}},
                    "base": None,
                    "definition": None,
                },
                {
                    "id": "f41cebba-a048-4852-a3d7-0f3100927166",
                    "type": "CODE_EXECUTION",
                    "inputs": [
                        {
                            "id": "b807bd5f-7d49-4597-89cf-044aa84cf8d6",
                            "key": "code",
                            "value": {
                                "rules": [{"type": "CONSTANT_VALUE", "data": {"type": "JSON", "value": None}}],
                                "combinator": "OR",
                            },
                        },
                        {
                            "id": "dcd1e1a4-49e2-4d6b-95f9-8ec5fd2f8f5d",
                            "key": "runtime",
                            "value": {
                                "rules": [
                                    {"type": "CONSTANT_VALUE", "data": {"type": "STRING", "value": "PYTHON_3_11_6"}}
                                ],
                                "combinator": "OR",
                            },
                        },
                    ],
                    "data": {
                        "label": "My Node",
                        "error_output_id": None,
                        "source_handle_id": "dc9edb2e-4392-4a2c-ab92-cc1b9c0cbd53",
                        "target_handle_id": "66e7ef63-518b-40e7-911a-e38e8bcaec81",
                        "code_input_id": "b807bd5f-7d49-4597-89cf-044aa84cf8d6",
                        "runtime_input_id": "dcd1e1a4-49e2-4d6b-95f9-8ec5fd2f8f5d",
                        "output_type": "STRING",
                        "packages": [],
                        "output_id": "98cae9b9-45cc-4897-a0f5-df250b56c00d",
                        "log_output_id": "66c06c97-a9d1-4abf-840f-3f6c29709612",
                    },
                    "display_data": {"position": {"x": 0.0, "y": 0.0}},
                    "base": {
                        "name": "CodeExecutionNode",
                        "module": ["vellum", "workflows", "nodes", "displayable", "code_execution_node", "node"],
                    },
                    "definition": {
                        "name": "MyNode",
                        "module": [
                            "vellum_ee",
                            "workflows",
                            "display",
                            "nodes",
                            "vellum",
                            "tests",
                            "test_code_execution_node",
                        ],
                    },
                    "ports": [{"id": "dc9edb2e-4392-4a2c-ab92-cc1b9c0cbd53", "name": "default", "type": "DEFAULT"}],
                    "trigger": {"id": "66e7ef63-518b-40e7-911a-e38e8bcaec81", "merge_behavior": "AWAIT_ANY"},
                    "outputs": [
                        {
                            "id": "98cae9b9-45cc-4897-a0f5-df250b56c00d",
                            "name": "result",
                            "schema": {"type": "string"},
                            "type": "STRING",
                            "value": None,
                        },
                        {
                            "id": "66c06c97-a9d1-4abf-840f-3f6c29709612",
                            "name": "log",
                            "schema": {"type": "string"},
                            "type": "STRING",
                            "value": None,
                        },
                    ],
                },
            ],
            "edges": [
                {
                    "id": "85e0961e-f968-49a0-beed-e21373f0ecda",
                    "source_node_id": "9b9e2a5d-01a4-46b2-80a3-d9484b2c0e08",
                    "source_handle_id": "3e2a3f52-5047-4e2e-9a21-37bd43c63250",
                    "target_node_id": "f41cebba-a048-4852-a3d7-0f3100927166",
                    "target_handle_id": "66e7ef63-518b-40e7-911a-e38e8bcaec81",
                    "type": "DEFAULT",
                }
            ],
            "display_data": {"viewport": {"x": 0.0, "y": 0.0, "zoom": 1.0}},
            "definition": {
                "name": "Workflow",
                "module": ["vellum_ee", "workflows", "display", "nodes", "vellum", "tests", "test_code_execution_node"],
            },
            "output_values": [],
        },
        "input_variables": [],
        "state_variables": [],
        "output_variables": [],
    }


def test_serialize_node__with_custom_output_type():
    # GIVEN a code node with a custom output type
    class MyNode(CodeExecutionNode[BaseState, dict[str, int]]):
        code = """\
return {
    "hello": 1,
}
"""

    # AND a workflow with the code node
    class Workflow(BaseWorkflow):
        graph = MyNode

    # WHEN we serialize the workflow
    workflow_display = get_workflow_display(workflow_class=Workflow)
    serialized_workflow: dict = workflow_display.serialize()

    # THEN the node's outputs should serialize correctly
    my_code_execution_node = next(
        node for node in serialized_workflow["workflow_raw_data"]["nodes"] if node["type"] == "CODE_EXECUTION"
    )
    assert my_code_execution_node["outputs"] == [
        {
            "id": "01de8e8b-5e0e-4344-93b0-e002bbaed840",
            "name": "result",
            "value": None,
            "type": "JSON",
            "schema": {"type": "object", "additionalProperties": {"type": "integer"}},
        },
        {
            "id": "64bf62e0-adc7-48cc-b689-8bf9b7e4eeef",
            "name": "log",
            "value": None,
            "type": "STRING",
            "schema": {"type": "string"},
        },
    ]
    assert my_code_execution_node["data"]["output_type"] == "JSON"
