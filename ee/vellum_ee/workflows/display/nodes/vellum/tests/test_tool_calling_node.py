from vellum.client.types.prompt_parameters import PromptParameters
from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs import BaseInputs
from vellum.workflows.nodes.displayable.inline_prompt_node.node import InlinePromptNode
from vellum.workflows.nodes.displayable.tool_calling_node.node import ToolCallingNode
from vellum.workflows.nodes.displayable.tool_calling_node.state import ToolCallingState
from vellum.workflows.nodes.displayable.tool_calling_node.utils import create_router_node, create_tool_prompt_node
from vellum.workflows.state.base import BaseState
from vellum.workflows.types.definition import AuthorizationType, EnvironmentVariableReference, MCPServer
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

    # THEN the router node should serialize successfully with the expected structure
    assert serialized_router_node is not None
    assert isinstance(serialized_router_node, dict)

    # AND it should have the expected top-level structure
    assert serialized_router_node["adornments"] is None
    assert serialized_router_node["type"] == "GENERIC"
    assert serialized_router_node["label"] == "RouterNode"
    assert serialized_router_node["outputs"] == []

    # AND it should have the correct base and definition
    assert serialized_router_node["base"] == {
        "module": ["vellum", "workflows", "nodes", "displayable", "tool_calling_node", "utils"],
        "name": "RouterNode",
    }
    assert serialized_router_node["definition"] == {
        "module": ["vellum", "workflows", "nodes", "displayable", "tool_calling_node", "utils"],
        "name": "RouterNode",
    }

    assert "display_data" in serialized_router_node
    display_data = serialized_router_node["display_data"]
    assert isinstance(display_data, dict)
    assert display_data["position"] == {"x": 0.0, "y": 0.0}

    assert "trigger" in serialized_router_node
    trigger = serialized_router_node["trigger"]
    assert isinstance(trigger, dict)
    assert trigger["merge_behavior"] == "AWAIT_ATTRIBUTES"
    assert "id" in trigger

    assert "attributes" in serialized_router_node
    attributes = serialized_router_node["attributes"]
    assert isinstance(attributes, list)
    assert len(attributes) == 1
    prompt_outputs_attr = attributes[0]
    assert isinstance(prompt_outputs_attr, dict)
    assert prompt_outputs_attr["name"] == "prompt_outputs"
    prompt_outputs_value = prompt_outputs_attr["value"]
    assert isinstance(prompt_outputs_value, dict)
    assert prompt_outputs_value["type"] == "NODE_OUTPUT"
    assert "node_id" in prompt_outputs_value
    assert "node_output_id" in prompt_outputs_value

    assert "ports" in serialized_router_node
    ports = serialized_router_node["ports"]
    assert isinstance(ports, list)
    assert len(ports) == 2

    my_function_port = ports[0]
    assert isinstance(my_function_port, dict)
    assert my_function_port["name"] == "my_function"
    assert my_function_port["type"] == "IF"
    assert "expression" in my_function_port
    assert "id" in my_function_port

    expression = my_function_port["expression"]
    assert isinstance(expression, dict)
    assert expression["type"] == "BINARY_EXPRESSION"
    assert expression["operator"] == "and"

    default_port = ports[1]
    assert isinstance(default_port, dict)
    assert default_port["name"] == "default"
    assert default_port["type"] == "ELSE"
    assert default_port["expression"] is None
    assert "id" in default_port
