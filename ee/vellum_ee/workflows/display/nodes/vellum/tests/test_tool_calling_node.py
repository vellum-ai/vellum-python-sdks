from datetime import datetime

from vellum.client.types.prompt_parameters import PromptParameters
from vellum.client.types.release_review_reviewer import ReleaseReviewReviewer
from vellum.client.types.workflow_deployment_release import (
    ReleaseEnvironment,
    ReleaseReleaseTag,
    SlimReleaseReview,
    WorkflowDeploymentRelease,
    WorkflowDeploymentReleaseWorkflowDeployment,
    WorkflowDeploymentReleaseWorkflowVersion,
)
from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs import BaseInputs
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.nodes.displayable.code_execution_node.node import CodeExecutionNode
from vellum.workflows.nodes.displayable.inline_prompt_node.node import InlinePromptNode
from vellum.workflows.nodes.displayable.tool_calling_node.node import ToolCallingNode
from vellum.workflows.nodes.displayable.tool_calling_node.state import ToolCallingState
from vellum.workflows.nodes.displayable.tool_calling_node.utils import create_router_node, create_tool_prompt_node
from vellum.workflows.outputs.base import BaseOutputs
from vellum.workflows.state.base import BaseState
from vellum.workflows.types.definition import (
    AuthorizationType,
    DeploymentDefinition,
    EnvironmentVariableReference,
    MCPServer,
)
from vellum_ee.workflows.display.nodes.get_node_display_class import get_node_display_class
from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display


def test_serialize_node__prompt_inputs__constant_value():
    # GIVEN a prompt node with constant value inputs
    class MyPromptNode(ToolCallingNode):
        prompt_inputs = {"foo": "bar"}

    # AND a workflow with the prompt node
    class Workflow(BaseWorkflow):
        graph = MyPromptNode

    # WHEN the workflow is serialized
    workflow_display = get_workflow_display(workflow_class=Workflow)
    serialized_workflow: dict = workflow_display.serialize()

    # THEN the node should properly serialize the inputs
    my_prompt_node = next(
        node for node in serialized_workflow["workflow_raw_data"]["nodes"] if node["id"] == str(MyPromptNode.__id__)
    )

    prompt_inputs_attribute = next(
        attribute for attribute in my_prompt_node["attributes"] if attribute["name"] == "prompt_inputs"
    )

    assert prompt_inputs_attribute == {
        "id": "3d9a4d2e-c9bd-4417-8a0c-52f15efdbe30",
        "name": "prompt_inputs",
        "value": {"type": "CONSTANT_VALUE", "value": {"type": "JSON", "value": {"foo": "bar"}}},
    }


def test_serialize_node__prompt_inputs__input_reference():
    # GIVEN a state definition
    class MyInput(BaseInputs):
        foo: str

    # AND a prompt node with inputs
    class MyPromptNode(InlinePromptNode):
        prompt_inputs = {"foo": MyInput.foo}

    # AND a workflow with the prompt node
    class Workflow(BaseWorkflow[MyInput, BaseState]):
        graph = MyPromptNode

    # WHEN the workflow is serialized
    workflow_display = get_workflow_display(workflow_class=Workflow)
    serialized_workflow: dict = workflow_display.serialize()

    # THEN the node should skip the state reference input rule
    my_prompt_node = next(
        node for node in serialized_workflow["workflow_raw_data"]["nodes"] if node["id"] == str(MyPromptNode.__id__)
    )

    prompt_inputs_attribute = next(
        attribute for attribute in my_prompt_node["attributes"] if attribute["name"] == "prompt_inputs"
    )

    assert prompt_inputs_attribute == {
        "id": "6cde4776-7f4a-411c-95a8-69c8b3a64b42",
        "name": "prompt_inputs",
        "value": {
            "type": "DICTIONARY_REFERENCE",
            "entries": [
                {
                    "id": "ab7902ef-de14-4edc-835c-366d3ef6a70e",
                    "key": "foo",
                    "value": {"type": "WORKFLOW_INPUT", "input_variable_id": "e3657390-fd3c-4fea-8cdd-fc5ea79f3278"},
                }
            ],
        },
    }


def test_serialize_node__prompt_inputs__mixed_values():
    # GIVEN a prompt node with mixed values
    class MyInput(BaseInputs):
        foo: str

    # AND a prompt node with mixed values
    class MyPromptNode(InlinePromptNode):
        prompt_inputs = {"foo": "bar", "baz": MyInput.foo}

    # AND a workflow with the prompt node
    class Workflow(BaseWorkflow[MyInput, BaseState]):
        graph = MyPromptNode

    # WHEN the workflow is serialized
    workflow_display = get_workflow_display(workflow_class=Workflow)
    serialized_workflow: dict = workflow_display.serialize()

    # THEN the node should properly serialize the inputs
    my_prompt_node = next(
        node for node in serialized_workflow["workflow_raw_data"]["nodes"] if node["id"] == str(MyPromptNode.__id__)
    )

    prompt_inputs_attribute = next(
        attribute for attribute in my_prompt_node["attributes"] if attribute["name"] == "prompt_inputs"
    )

    assert prompt_inputs_attribute == {
        "id": "c4ca6e3d-0f71-4802-a618-1e87880cb7cf",
        "name": "prompt_inputs",
        "value": {
            "type": "DICTIONARY_REFERENCE",
            "entries": [
                {
                    "id": "0fc7e25e-075c-4849-b89b-9729d1aeada1",
                    "key": "foo",
                    "value": {"type": "CONSTANT_VALUE", "value": {"type": "STRING", "value": "bar"}},
                },
                {
                    "id": "bba42c89-fa7b-4cb7-bc16-0d21ce060a4b",
                    "key": "baz",
                    "value": {"type": "WORKFLOW_INPUT", "input_variable_id": "8d57cf1d-147c-427b-9a5e-e5f6ab76e2eb"},
                },
            ],
        },
    }


def test_serialize_node__tool_calling_node__mcp_server_api_key():
    # GIVEN a tool calling node with an mcp server
    class MyToolCallingNode(ToolCallingNode):
        functions = [
            MCPServer(
                name="my-mcp-server",
                url="https://my-mcp-server.com",
                authorization_type=AuthorizationType.API_KEY,
                api_key_header_key="my-api-key-header-key",
                api_key_header_value=EnvironmentVariableReference(name="my-api-key-header-value"),
            )
        ]

    # AND a workflow with the tool calling node
    class Workflow(BaseWorkflow):
        graph = MyToolCallingNode

    # WHEN the workflow is serialized
    workflow_display = get_workflow_display(workflow_class=Workflow)
    serialized_workflow: dict = workflow_display.serialize()

    # THEN the node should properly serialize the mcp server
    my_tool_calling_node = next(
        node
        for node in serialized_workflow["workflow_raw_data"]["nodes"]
        if node["id"] == str(MyToolCallingNode.__id__)
    )

    functions_attribute = next(
        attribute for attribute in my_tool_calling_node["attributes"] if attribute["name"] == "functions"
    )

    assert functions_attribute == {
        "id": "6c0f7d4f-3c8a-4201-b588-8398d3c97480",
        "name": "functions",
        "value": {
            "type": "CONSTANT_VALUE",
            "value": {
                "type": "JSON",
                "value": [
                    {
                        "type": "MCP_SERVER",
                        "name": "my-mcp-server",
                        "description": "",
                        "url": "https://my-mcp-server.com",
                        "authorization_type": "API_KEY",
                        "bearer_token_value": None,
                        "api_key_header_key": "my-api-key-header-key",
                        "api_key_header_value": "my-api-key-header-value",
                    }
                ],
            },
        },
    }


def test_serialize_node__tool_calling_node__mcp_server_no_authorization():
    # GIVEN a tool calling node with an mcp server
    class MyToolCallingNode(ToolCallingNode):
        functions = [
            MCPServer(
                name="my-mcp-server",
                url="https://my-mcp-server.com",
            )
        ]

    # AND a workflow with the tool calling node
    class Workflow(BaseWorkflow):
        graph = MyToolCallingNode

    # WHEN the workflow is serialized
    workflow_display = get_workflow_display(workflow_class=Workflow)
    serialized_workflow: dict = workflow_display.serialize()

    # THEN the node should properly serialize the mcp server
    my_tool_calling_node = next(
        node
        for node in serialized_workflow["workflow_raw_data"]["nodes"]
        if node["id"] == str(MyToolCallingNode.__id__)
    )

    functions_attribute = next(
        attribute for attribute in my_tool_calling_node["attributes"] if attribute["name"] == "functions"
    )

    assert functions_attribute == {
        "id": "c8957551-cb3d-49af-8053-acd256c1d852",
        "name": "functions",
        "value": {
            "type": "CONSTANT_VALUE",
            "value": {
                "type": "JSON",
                "value": [
                    {
                        "type": "MCP_SERVER",
                        "name": "my-mcp-server",
                        "description": "",
                        "url": "https://my-mcp-server.com",
                        "authorization_type": None,
                        "bearer_token_value": None,
                        "api_key_header_key": None,
                        "api_key_header_value": None,
                    }
                ],
            },
        },
    }


def test_serialize_tool_router_node():
    """
    Test that the tool router node created by create_router_node serializes successfully.
    """

    # GIVEN a simple function for tool calling
    def my_function(arg1: str) -> str:
        return f"Result: {arg1}"

    tool_prompt_node = create_tool_prompt_node(
        ml_model="gpt-4o-mini",
        blocks=[],
        functions=[my_function],
        prompt_inputs=None,
        parameters=PromptParameters(),
    )

    # WHEN we create a router node using create_router_node
    router_node = create_router_node(
        functions=[my_function],
        tool_prompt_node=tool_prompt_node,
    )

    router_node_display_class = get_node_display_class(router_node)
    router_node_display = router_node_display_class()

    class Workflow(BaseWorkflow[BaseInputs, ToolCallingState]):
        graph = tool_prompt_node >> router_node

    workflow_display = get_workflow_display(workflow_class=Workflow)
    display_context = workflow_display.display_context

    # WHEN we serialize the router node
    serialized_router_node = router_node_display.serialize(display_context)

    # THEN the router node should serialize to the exact expected structure
    assert serialized_router_node == {
        "adornments": None,
        "attributes": [
            {
                "id": "cd208919-c66b-451b-a739-bcf7d3451dea",
                "name": "prompt_outputs",
                "value": {
                    "node_id": "19e664fc-3b57-48d2-b47a-b143b475406a",
                    "node_output_id": "c2a5a7f7-a234-45dc-adee-bc6fc0bd28dd",
                    "type": "NODE_OUTPUT",
                },
            }
        ],
        "base": {
            "module": ["vellum", "workflows", "nodes", "displayable", "tool_calling_node", "utils"],
            "name": "RouterNode",
        },
        "definition": {
            "module": ["vellum", "workflows", "nodes", "displayable", "tool_calling_node", "utils"],
            "name": "RouterNode",
        },
        "display_data": {"position": {"x": 0.0, "y": 0.0}},
        "id": "690c66e1-1e18-4984-b695-84beb0157541",
        "label": "Router Node",
        "outputs": [],
        "ports": [
            {
                "expression": {
                    "lhs": {
                        "lhs": {
                            "lhs": {
                                "state_variable_id": "0dd7f5a1-1d73-4153-9191-ca828ace4920",
                                "type": "WORKFLOW_STATE",
                            },
                            "operator": "<",
                            "rhs": {
                                "lhs": {
                                    "node_id": "19e664fc-3b57-48d2-b47a-b143b475406a",
                                    "node_output_id": "c2a5a7f7-a234-45dc-adee-bc6fc0bd28dd",
                                    "type": "NODE_OUTPUT",
                                },
                                "operator": "length",
                                "type": "UNARY_EXPRESSION",
                            },
                            "type": "BINARY_EXPRESSION",
                        },
                        "operator": "and",
                        "rhs": {
                            "lhs": {
                                "lhs": {
                                    "lhs": {
                                        "node_id": "19e664fc-3b57-48d2-b47a-b143b475406a",
                                        "node_output_id": "c2a5a7f7-a234-45dc-adee-bc6fc0bd28dd",
                                        "type": "NODE_OUTPUT",
                                    },
                                    "operator": "accessField",
                                    "rhs": {
                                        "state_variable_id": "0dd7f5a1-1d73-4153-9191-ca828ace4920",
                                        "type": "WORKFLOW_STATE",
                                    },
                                    "type": "BINARY_EXPRESSION",
                                },
                                "operator": "accessField",
                                "rhs": {"type": "CONSTANT_VALUE", "value": {"type": "STRING", "value": "type"}},
                                "type": "BINARY_EXPRESSION",
                            },
                            "operator": "=",
                            "rhs": {"type": "CONSTANT_VALUE", "value": {"type": "STRING", "value": "FUNCTION_CALL"}},
                            "type": "BINARY_EXPRESSION",
                        },
                        "type": "BINARY_EXPRESSION",
                    },
                    "operator": "and",
                    "rhs": {
                        "lhs": {
                            "lhs": {
                                "lhs": {
                                    "lhs": {
                                        "node_id": "19e664fc-3b57-48d2-b47a-b143b475406a",
                                        "node_output_id": "c2a5a7f7-a234-45dc-adee-bc6fc0bd28dd",
                                        "type": "NODE_OUTPUT",
                                    },
                                    "operator": "accessField",
                                    "rhs": {
                                        "state_variable_id": "0dd7f5a1-1d73-4153-9191-ca828ace4920",
                                        "type": "WORKFLOW_STATE",
                                    },
                                    "type": "BINARY_EXPRESSION",
                                },
                                "operator": "accessField",
                                "rhs": {"type": "CONSTANT_VALUE", "value": {"type": "STRING", "value": "value"}},
                                "type": "BINARY_EXPRESSION",
                            },
                            "operator": "accessField",
                            "rhs": {"type": "CONSTANT_VALUE", "value": {"type": "STRING", "value": "name"}},
                            "type": "BINARY_EXPRESSION",
                        },
                        "operator": "=",
                        "rhs": {"type": "CONSTANT_VALUE", "value": {"type": "STRING", "value": "my_function"}},
                        "type": "BINARY_EXPRESSION",
                    },
                    "type": "BINARY_EXPRESSION",
                },
                "id": "afb4b09d-659b-459e-9a28-cf73ba6e0574",
                "name": "my_function",
                "type": "IF",
            },
            {"expression": None, "id": "4ecd916e-b5d0-407e-aab4-35551c76d02c", "name": "default", "type": "ELSE"},
        ],
        "trigger": {"id": "73a96f44-c2dd-40cc-96f6-49b9f914b166", "merge_behavior": "AWAIT_ATTRIBUTES"},
        "type": "GENERIC",
    }


def test_serialize_node__tool_calling_node__subworkflow_with_parent_input_reference():
    """
    Test that a tool calling node with a subworkflow that references parent inputs serializes correctly
    """

    # GIVEN a workflow inputs class
    class MyInputs(BaseInputs):
        text: str
        greeting: str

    # AND a code execution node that references parent inputs
    class CodeExecution(CodeExecutionNode[BaseState, str]):
        code = ""
        code_inputs = {
            "text": MyInputs.text,
        }
        runtime = "PYTHON_3_11_6"
        packages = []

    # AND a subworkflow that uses the code execution node
    class FunctionSubworkflow(BaseWorkflow):
        graph = CodeExecution

        class Outputs(BaseWorkflow.Outputs):
            output = CodeExecution.Outputs.result

    # AND a tool calling node that uses the subworkflow
    class MyToolCallingNode(ToolCallingNode):
        ml_model = "gpt-4.1"
        prompt_inputs = {
            "text": MyInputs.text,
        }
        blocks = []
        parameters = PromptParameters()
        functions = [FunctionSubworkflow]

    # AND a workflow with the tool calling node
    class Workflow(BaseWorkflow[MyInputs, BaseState]):
        graph = MyToolCallingNode

    # WHEN the workflow is serialized
    workflow_display = get_workflow_display(workflow_class=Workflow)
    serialized_workflow: dict = workflow_display.serialize()

    # THEN the node should properly serialize the functions with parent input references
    my_tool_calling_node = next(
        node
        for node in serialized_workflow["workflow_raw_data"]["nodes"]
        if node["id"] == str(MyToolCallingNode.__id__)
    )

    functions_attribute = next(
        attribute for attribute in my_tool_calling_node["attributes"] if attribute["name"] == "functions"
    )

    data = functions_attribute["value"]["value"]["value"][0]
    nodes = data["exec_config"]["workflow_raw_data"]["nodes"]
    code_exec_node = next((node for node in nodes if node["type"] == "CODE_EXECUTION"), None)

    assert code_exec_node is not None
    text_input = next((input for input in code_exec_node["inputs"] if input["key"] == "text"), None)
    assert text_input == {
        "id": "da92a1c4-d37c-4008-a1ab-c0bcc0cd20d0",
        "key": "text",
        "value": {
            "rules": [
                {"type": "INPUT_VARIABLE", "data": {"input_variable_id": "6f0c1889-3f08-4c5c-bb24-f7b94169105c"}}
            ],
            "combinator": "OR",
        },
    }


def test_serialize_tool_prompt_node_with_inline_workflow():
    """
    Test that the tool prompt node created by create_tool_prompt_node serializes successfully with inline workflow.
    """

    # GIVEN a simple inline workflow for tool calling
    class SimpleWorkflowInputs(BaseInputs):
        message: str

    class SimpleNode(BaseNode):
        message = SimpleWorkflowInputs.message

        class Outputs(BaseOutputs):
            result: str

        def run(self) -> Outputs:
            return self.Outputs(result=f"Processed: {self.message}")

    class SimpleInlineWorkflow(BaseWorkflow[SimpleWorkflowInputs, BaseState]):
        """A simple workflow for testing inline tool serialization."""

        graph = SimpleNode

        class Outputs(BaseOutputs):
            result = SimpleNode.Outputs.result

    # WHEN we create a tool prompt node using create_tool_prompt_node with inline workflow
    tool_prompt_node = create_tool_prompt_node(
        ml_model="gpt-4o-mini",
        blocks=[],
        functions=[SimpleInlineWorkflow],
        prompt_inputs=None,
        parameters=PromptParameters(),
    )

    tool_prompt_node_display_class = get_node_display_class(tool_prompt_node)
    tool_prompt_node_display = tool_prompt_node_display_class()

    # AND we create a workflow that uses this tool prompt node
    class TestWorkflow(BaseWorkflow[BaseInputs, ToolCallingState]):
        graph = tool_prompt_node

    # WHEN we serialize the entire workflow
    workflow_display = get_workflow_display(workflow_class=TestWorkflow)
    display_context = workflow_display.display_context
    serialized_tool_prompt_node = tool_prompt_node_display.serialize(display_context)

    # THEN prompt inputs should be serialized correctly
    attributes = serialized_tool_prompt_node["attributes"]
    assert isinstance(attributes, list)
    prompt_inputs_attr = next(
        (attr for attr in attributes if isinstance(attr, dict) and attr["name"] == "prompt_inputs"), None
    )
    assert prompt_inputs_attr == {
        "id": "bc1320a2-23e4-4238-8b00-efbf88e91856",
        "name": "prompt_inputs",
        "value": {
            "type": "DICTIONARY_REFERENCE",
            "entries": [
                {
                    "id": "76ceec7b-ec37-474f-ba38-2bfd27cecc5d",
                    "key": "chat_history",
                    "value": {
                        "type": "BINARY_EXPRESSION",
                        "lhs": {"type": "CONSTANT_VALUE", "value": {"type": "JSON", "value": []}},
                        "operator": "concat",
                        "rhs": {
                            "type": "WORKFLOW_STATE",
                            "state_variable_id": "7a1caaf5-99df-487a-8b2d-6512df2d871a",
                        },
                    },
                }
            ],
        },
    }


def test_serialize_tool_prompt_node_with_workflow_deployment(vellum_client):
    """
    Test that the tool prompt node serializes successfully with a workflow deployment.
    """
    vellum_client.workflow_deployments.retrieve_workflow_deployment_release.return_value = WorkflowDeploymentRelease(
        id="test-id",
        created=datetime.now(),
        environment=ReleaseEnvironment(
            id="test-id",
            name="test-name",
            label="test-label",
        ),
        created_by=None,
        workflow_version=WorkflowDeploymentReleaseWorkflowVersion(
            id="test-id",
            input_variables=[],
            output_variables=[],
        ),
        deployment=WorkflowDeploymentReleaseWorkflowDeployment(name="test-name"),
        description="test-description",
        release_tags=[
            ReleaseReleaseTag(
                name="test-name",
                source="USER",
            )
        ],
        reviews=[
            SlimReleaseReview(
                id="test-id",
                created=datetime.now(),
                reviewer=ReleaseReviewReviewer(
                    id="test-id",
                    full_name="test-name",
                ),
                state="APPROVED",
            )
        ],
    )

    # GIVEN a workflow deployment
    workflow_deployment = DeploymentDefinition(
        deployment="test-deployment",
        release_tag="test-release-tag",
    )

    # WHEN we create a tool prompt node using create_tool_prompt_node with a workflow deployment
    tool_prompt_node = create_tool_prompt_node(
        ml_model="gpt-4o-mini",
        blocks=[],
        functions=[workflow_deployment],
        prompt_inputs=None,
        parameters=PromptParameters(),
    )

    tool_prompt_node_display_class = get_node_display_class(tool_prompt_node)
    tool_prompt_node_display = tool_prompt_node_display_class()

    # AND we create a workflow that uses this tool prompt node
    class TestWorkflow(BaseWorkflow[BaseInputs, ToolCallingState]):
        graph = tool_prompt_node

    # WHEN we serialize the entire workflow
    workflow_display = get_workflow_display(workflow_class=TestWorkflow)
    display_context = workflow_display.display_context
    serialized_tool_prompt_node = tool_prompt_node_display.serialize(display_context)

    # THEN functions attribute should be serialized correctly
    attributes = serialized_tool_prompt_node["attributes"]
    assert isinstance(attributes, list)
    functions_attr = next((attr for attr in attributes if isinstance(attr, dict) and attr["name"] == "functions"), None)
    assert functions_attr == {
        "id": "6326ccc4-7cf6-4235-ba3c-a6e860b0c48b",
        "name": "functions",
        "value": {
            "type": "CONSTANT_VALUE",
            "value": {
                "type": "JSON",
                "value": [
                    {
                        "type": "WORKFLOW_DEPLOYMENT",
                        "name": "test-name",
                        "description": "test-description",
                        "deployment": "test-deployment",
                        "release_tag": "test-release-tag",
                    }
                ],
            },
        },
    }
