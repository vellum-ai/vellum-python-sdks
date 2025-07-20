from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs import BaseInputs
from vellum.workflows.nodes.displayable.inline_prompt_node.node import InlinePromptNode
from vellum.workflows.nodes.displayable.tool_calling_node.node import ToolCallingNode
from vellum.workflows.state.base import BaseState
from vellum.workflows.types.definition import ComposioToolDefinition
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


def test_serialize_node__functions__composio_tool():
    # GIVEN a ComposioToolDefinition
    composio_tool = ComposioToolDefinition(
        toolkit="GITHUB", action="GITHUB_CREATE_AN_ISSUE", description="Create a new issue in a GitHub repository"
    )

    # AND a ToolCallingNode with the ComposioToolDefinition
    class MyToolCallingNode(ToolCallingNode):
        functions = [composio_tool]

    # AND a workflow with the tool calling node
    class Workflow(BaseWorkflow):
        graph = MyToolCallingNode

    # WHEN the workflow is serialized
    workflow_display = get_workflow_display(workflow_class=Workflow)
    serialized_workflow: dict = workflow_display.serialize()

    # THEN the node should properly serialize the ComposioToolDefinition
    my_tool_node = next(
        node
        for node in serialized_workflow["workflow_raw_data"]["nodes"]
        if node["id"] == str(MyToolCallingNode.__id__)
    )

    functions_attribute = next(
        attribute for attribute in my_tool_node["attributes"] if attribute["name"] == "functions"
    )

    expected_composio_function = {
        "type": "COMPOSIO",
        "name": "github_github_create_an_issue",
        "toolkit": "GITHUB",
        "action": "GITHUB_CREATE_AN_ISSUE",
        "description": "Create a new issue in a GitHub repository",
        "display_name": None,
    }

    assert functions_attribute["value"]["type"] == "CONSTANT_VALUE"
    assert functions_attribute["value"]["value"]["type"] == "JSON"
    assert len(functions_attribute["value"]["value"]["value"]) == 1
    assert functions_attribute["value"]["value"]["value"][0] == expected_composio_function


def test_serialize_node__functions__composio_tool_with_display_name():
    # GIVEN a ComposioToolDefinition with display_name
    composio_tool = ComposioToolDefinition(
        toolkit="SLACK",
        action="SLACK_SEND_MESSAGE",
        description="Send a message to a Slack channel",
        display_name="Send Slack Message",
    )

    # AND a ToolCallingNode with the ComposioToolDefinition
    class MyToolCallingNode(ToolCallingNode):
        functions = [composio_tool]

    # AND a workflow with the tool calling node
    class Workflow(BaseWorkflow):
        graph = MyToolCallingNode

    # WHEN the workflow is serialized
    workflow_display = get_workflow_display(workflow_class=Workflow)
    serialized_workflow: dict = workflow_display.serialize()

    # THEN the node should properly serialize the ComposioToolDefinition with display_name
    my_tool_node = next(
        node
        for node in serialized_workflow["workflow_raw_data"]["nodes"]
        if node["id"] == str(MyToolCallingNode.__id__)
    )

    functions_attribute = next(
        attribute for attribute in my_tool_node["attributes"] if attribute["name"] == "functions"
    )

    expected_composio_function = {
        "type": "COMPOSIO",
        "name": "slack_slack_send_message",
        "toolkit": "SLACK",
        "action": "SLACK_SEND_MESSAGE",
        "description": "Send a message to a Slack channel",
        "display_name": "Send Slack Message",
    }

    assert functions_attribute["value"]["type"] == "CONSTANT_VALUE"
    assert functions_attribute["value"]["value"]["type"] == "JSON"
    assert len(functions_attribute["value"]["value"]["value"]) == 1
    assert functions_attribute["value"]["value"]["value"][0] == expected_composio_function


def test_serialize_node__functions__mixed_composio_and_regular_function():
    # GIVEN a regular Python function
    def get_weather(location: str) -> str:
        """Get weather for a location."""
        return f"Sunny in {location}"

    # AND a ComposioToolDefinition
    composio_tool = ComposioToolDefinition(
        toolkit="GITHUB", action="GITHUB_CREATE_AN_ISSUE", description="Create a new issue in a GitHub repository"
    )

    # AND a ToolCallingNode with both
    class MyToolCallingNode(ToolCallingNode):
        functions = [get_weather, composio_tool]

    # AND a workflow with the tool calling node
    class Workflow(BaseWorkflow):
        graph = MyToolCallingNode

    # WHEN the workflow is serialized
    workflow_display = get_workflow_display(workflow_class=Workflow)
    serialized_workflow: dict = workflow_display.serialize()

    # THEN the node should properly serialize both function types
    my_tool_node = next(
        node
        for node in serialized_workflow["workflow_raw_data"]["nodes"]
        if node["id"] == str(MyToolCallingNode.__id__)
    )

    functions_attribute = next(
        attribute for attribute in my_tool_node["attributes"] if attribute["name"] == "functions"
    )

    assert functions_attribute["value"]["type"] == "CONSTANT_VALUE"
    assert functions_attribute["value"]["value"]["type"] == "JSON"
    functions_list = functions_attribute["value"]["value"]["value"]
    assert len(functions_list) == 2

    # Check that we have one CODE_EXECUTION and one COMPOSIO function
    function_types = [func["type"] for func in functions_list]
    assert "CODE_EXECUTION" in function_types
    assert "COMPOSIO" in function_types

    # Find and verify the ComposioToolDefinition serialization
    composio_function = next(func for func in functions_list if func["type"] == "COMPOSIO")
    expected_composio_function = {
        "type": "COMPOSIO",
        "name": "github_github_create_an_issue",
        "toolkit": "GITHUB",
        "action": "GITHUB_CREATE_AN_ISSUE",
        "description": "Create a new issue in a GitHub repository",
        "display_name": None,
    }
    assert composio_function == expected_composio_function

    # Verify regular function still serializes correctly
    code_function = next(func for func in functions_list if func["type"] == "CODE_EXECUTION")
    assert code_function["name"] == "get_weather"
    assert "definition" in code_function
    assert "src" in code_function


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
