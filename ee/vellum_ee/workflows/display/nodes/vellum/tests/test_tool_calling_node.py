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
from vellum.workflows.nodes.displayable.tool_calling_node.utils import (
    create_function_node,
    create_router_node,
    create_tool_prompt_node,
)
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
        "id": "fb85d86d-f291-4a0d-b867-f7545df7af59",
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
        "id": "80ed13f9-64d2-47ee-bb91-3378de7ad2c0",
        "name": "prompt_inputs",
        "value": {
            "type": "DICTIONARY_REFERENCE",
            "entries": [
                {
                    "id": "981b8cdf-c08d-42a1-a226-76de8acf192f",
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
        "id": "7352d310-204c-4291-8757-a84a6e68591a",
        "name": "prompt_inputs",
        "value": {
            "type": "DICTIONARY_REFERENCE",
            "entries": [
                {
                    "id": "05c092c7-4031-43b7-8c3d-b1a317ca271d",
                    "key": "foo",
                    "value": {"type": "CONSTANT_VALUE", "value": {"type": "STRING", "value": "bar"}},
                },
                {
                    "id": "b0de6603-fcdd-44a3-b33a-56f05bd03bb4",
                    "key": "baz",
                    "value": {"type": "WORKFLOW_INPUT", "input_variable_id": "8d57cf1d-147c-427b-9a5e-e5f6ab76e2eb"},
                },
            ],
        },
    }


def test_serialize_node__tool_calling_node__mcp_server_api_key():
    """Tests that MCPServer with EnvironmentVariableReference serializes as ARRAY_REFERENCE."""

    # GIVEN a tool calling node with an mcp server using an environment variable for the API key
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

    # AND the functions attribute should be an ARRAY_REFERENCE with a DICTIONARY_REFERENCE
    # containing the MCP server fields, with api_key_header_value as ENVIRONMENT_VARIABLE
    assert functions_attribute == {
        "id": "ff00c2d6-f99c-458b-9bcd-181f8e43b2d1",
        "name": "functions",
        "value": {
            "type": "ARRAY_REFERENCE",
            "items": [
                {
                    "type": "DICTIONARY_REFERENCE",
                    "entries": [
                        {
                            "id": "8cff4f0a-86d9-43fd-8d0b-542c845db53e",
                            "key": "type",
                            "value": {"type": "CONSTANT_VALUE", "value": {"type": "STRING", "value": "MCP_SERVER"}},
                        },
                        {
                            "id": "29203be4-407c-4056-aaa3-6e6d1249113e",
                            "key": "name",
                            "value": {"type": "CONSTANT_VALUE", "value": {"type": "STRING", "value": "my-mcp-server"}},
                        },
                        {
                            "id": "69813bb2-12c1-432b-9ef3-a0071bd29149",
                            "key": "description",
                            "value": {"type": "CONSTANT_VALUE", "value": {"type": "STRING", "value": ""}},
                        },
                        {
                            "id": "83cd2f84-bf35-4996-9840-3754a79e1091",
                            "key": "url",
                            "value": {
                                "type": "CONSTANT_VALUE",
                                "value": {"type": "STRING", "value": "https://my-mcp-server.com"},
                            },
                        },
                        {
                            "id": "5ad23cee-497e-4ca3-ba51-d13f56985c75",
                            "key": "authorization_type",
                            "value": {"type": "CONSTANT_VALUE", "value": {"type": "STRING", "value": "API_KEY"}},
                        },
                        {
                            "id": "45964d28-1a9b-40a1-b544-62da92d2f62a",
                            "key": "bearer_token_value",
                            "value": {"type": "CONSTANT_VALUE", "value": {"type": "JSON", "value": None}},
                        },
                        {
                            "id": "c4952fa6-1ffb-4e88-863f-3d0867b19b7a",
                            "key": "api_key_header_key",
                            "value": {
                                "type": "CONSTANT_VALUE",
                                "value": {"type": "STRING", "value": "my-api-key-header-key"},
                            },
                        },
                        {
                            "id": "7dc9cdb0-d139-4a1d-8c6f-9941c6b82b62",
                            "key": "api_key_header_value",
                            "value": {
                                "type": "ENVIRONMENT_VARIABLE",
                                "environment_variable": "my-api-key-header-value",
                            },
                        },
                    ],
                    "definition": {"name": "MCPServer", "module": ["vellum", "workflows", "types", "definition"]},
                }
            ],
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
        "id": "a8a0133f-7913-451a-89da-f8dea5f352a2",
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
                "id": "ea36d8ff-3f6e-41eb-8a7b-ba3ca8e05f49",
                "name": "prompt_outputs",
                "value": {
                    "node_id": "c75146e1-ea10-4f58-90fd-887322725496",
                    "node_output_id": "baef5c93-612a-453d-b739-223041ef0429",
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
        "id": "d2884fa0-2d3d-4220-a335-bdcef56a00d5",
        "label": "Router Node",
        "outputs": [],
        "ports": [
            {
                "expression": {
                    "lhs": {
                        "lhs": {
                            "lhs": {
                                "state_variable_id": "30a4672a-96dc-471a-878c-90e0f1f7f043",
                                "type": "WORKFLOW_STATE",
                            },
                            "operator": "<",
                            "rhs": {
                                "lhs": {
                                    "node_id": "c75146e1-ea10-4f58-90fd-887322725496",
                                    "node_output_id": "baef5c93-612a-453d-b739-223041ef0429",
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
                                        "node_id": "c75146e1-ea10-4f58-90fd-887322725496",
                                        "node_output_id": "baef5c93-612a-453d-b739-223041ef0429",
                                        "type": "NODE_OUTPUT",
                                    },
                                    "operator": "accessField",
                                    "rhs": {
                                        "state_variable_id": "30a4672a-96dc-471a-878c-90e0f1f7f043",
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
                                        "node_id": "c75146e1-ea10-4f58-90fd-887322725496",
                                        "node_output_id": "baef5c93-612a-453d-b739-223041ef0429",
                                        "type": "NODE_OUTPUT",
                                    },
                                    "operator": "accessField",
                                    "rhs": {
                                        "state_variable_id": "30a4672a-96dc-471a-878c-90e0f1f7f043",
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
                "id": "81d85d92-7f51-4f41-84be-8e2b0eeb4f59",
                "name": "my_function",
                "type": "IF",
            },
            {"expression": None, "id": "a433bba4-a0d6-44f3-b53b-0d5231e442cf", "name": "default", "type": "ELSE"},
        ],
        "trigger": {"id": "9055a5d0-68a1-40cf-bc05-a8c65bd19abe", "merge_behavior": "AWAIT_ATTRIBUTES"},
        "type": "GENERIC",
    }


def test_serialize_function_node():
    """
    Test that the function node created by create_function_node serializes with icon and color.
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

    # WHEN we create a function node using create_function_node
    function_node = create_function_node(
        function=my_function,
        tool_prompt_node=tool_prompt_node,
    )

    function_node_display_class = get_node_display_class(function_node)
    function_node_display = function_node_display_class()

    class Workflow(BaseWorkflow[BaseInputs, ToolCallingState]):
        graph = tool_prompt_node >> function_node

    workflow_display = get_workflow_display(workflow_class=Workflow)
    display_context = workflow_display.display_context

    # WHEN we serialize the function node
    serialized_function_node = function_node_display.serialize(display_context)

    # THEN the function node should include icon and color in display_data
    display_data = serialized_function_node["display_data"]
    assert isinstance(display_data, dict)
    assert display_data["icon"] == "vellum:icon:rectangle-code"
    assert display_data["color"] == "purple"


def test_serialize_inline_prompt_node__mcp_server_not_serialized():
    """
    Test that MCP servers in inline prompt node functions are not serialized as function blocks.
    MCP servers should be skipped during serialization (they return None from _generate_function_tools).
    """

    # GIVEN an MCP server
    mcp_server = MCPServer(
        name="my-mcp-server",
        url="https://my-mcp-server.com",
        authorization_type=AuthorizationType.API_KEY,
        api_key_header_key="my-api-key-header-key",
        api_key_header_value=EnvironmentVariableReference(name="my-api-key-header-value"),
    )

    # AND a regular function
    def my_function(arg1: str) -> str:
        return f"Result: {arg1}"

    # AND an inline prompt node with both MCP server and regular function
    class MyInlinePromptNode(InlinePromptNode):
        ml_model = "gpt-4o-mini"
        blocks = []
        functions = [mcp_server, my_function]
        prompt_inputs = None
        parameters = PromptParameters()

    # WHEN we serialize the inline prompt node
    inline_prompt_node_display_class = get_node_display_class(MyInlinePromptNode)
    inline_prompt_node_display = inline_prompt_node_display_class()

    class Workflow(BaseWorkflow[BaseInputs, BaseState]):
        graph = MyInlinePromptNode

    workflow_display = get_workflow_display(workflow_class=Workflow)
    display_context = workflow_display.display_context

    serialized_node = inline_prompt_node_display.serialize(display_context)

    # THEN the serialized node should have exec_config with prompt_template_block_data
    assert isinstance(serialized_node, dict)
    assert serialized_node["type"] == "PROMPT"
    assert isinstance(serialized_node["data"], dict)
    assert "exec_config" in serialized_node["data"]
    exec_config = serialized_node["data"]["exec_config"]
    assert isinstance(exec_config, dict)
    assert "prompt_template_block_data" in exec_config
    prompt_template_block_data = exec_config["prompt_template_block_data"]
    assert isinstance(prompt_template_block_data, dict)
    blocks = prompt_template_block_data["blocks"]
    assert isinstance(blocks, list)

    # AND there should be only one FUNCTION_DEFINITION block (from the regular function)
    # MCP server should not be serialized
    function_blocks = [
        block for block in blocks if isinstance(block, dict) and block.get("block_type") == "FUNCTION_DEFINITION"
    ]
    assert len(function_blocks) == 1
    assert function_blocks == [
        {
            "id": "b6b7b0c2-78b6-498f-8f97-fdaa81e082ec",
            "block_type": "FUNCTION_DEFINITION",
            "properties": {
                "function_name": "my_function",
                "function_description": None,
                "function_parameters": {
                    "type": "object",
                    "properties": {"arg1": {"type": "string"}},
                    "required": ["arg1"],
                },
                "function_forced": None,
                "function_strict": None,
            },
        }
    ]


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
        "id": "9f3a85b5-a0c7-4b72-beef-d68b4eb2a428",
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
        "id": "d218d7c7-41f4-46d4-a9ed-89640cba1b9b",
        "name": "prompt_inputs",
        "value": {
            "type": "DICTIONARY_REFERENCE",
            "entries": [
                {
                    "id": "c181c554-a97f-4254-9bc8-1c30a8f3fb5f",
                    "key": "chat_history",
                    "value": {
                        "type": "BINARY_EXPRESSION",
                        "lhs": {"type": "CONSTANT_VALUE", "value": {"type": "JSON", "value": []}},
                        "operator": "concat",
                        "rhs": {
                            "type": "WORKFLOW_STATE",
                            "state_variable_id": "c1d692a7-3d87-4283-8d9c-daee82c61854",
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
        deployment=WorkflowDeploymentReleaseWorkflowDeployment(id="test-deployment-id", name="test-name"),
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
        "id": "f482dc81-e320-402d-83df-f60d278797d8",
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
