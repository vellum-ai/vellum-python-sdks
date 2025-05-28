from vellum.client.types.code_execution_package import CodeExecutionPackage
from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs import BaseInputs
from vellum.workflows.nodes.displayable.inline_prompt_node.node import InlinePromptNode
from vellum.workflows.nodes.experimental.tool_calling_node.node import ToolCallingNode
from vellum.workflows.state.base import BaseState
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


def test_serialize_node__function_packages():
    # GIVEN a tool calling node with function packages
    def foo():
        pass

    def bar():
        pass

    class MyToolCallingNode(ToolCallingNode):
        functions = [foo, bar]
        function_packages = {
            foo: [
                CodeExecutionPackage(name="first_package", version="1.0.0"),
                CodeExecutionPackage(name="second_package", version="2.0.0"),
            ],
            bar: [
                CodeExecutionPackage(name="third_package", version="3.0.0"),
            ],
        }

    # AND a workflow with the tool calling node
    class Workflow(BaseWorkflow):
        graph = MyToolCallingNode

    # WHEN the workflow is serialized
    workflow_display = get_workflow_display(workflow_class=Workflow)
    serialized_workflow: dict = workflow_display.serialize()

    # THEN the node should properly serialize the function packages
    my_tool_calling_node = next(
        node
        for node in serialized_workflow["workflow_raw_data"]["nodes"]
        if node["id"] == str(MyToolCallingNode.__id__)
    )

    function_packages_attribute = next(
        attribute for attribute in my_tool_calling_node["attributes"] if attribute["name"] == "function_packages"
    )

    assert function_packages_attribute == {
        "id": "c315228f-870a-4288-abf7-a217b5b8c253",
        "name": "function_packages",
        "value": {
            "type": "CONSTANT_VALUE",
            "value": {
                "type": "JSON",
                "value": {
                    "foo": [
                        {"version": "1.0.0", "name": "first_package"},
                        {"version": "2.0.0", "name": "second_package"},
                    ],
                    "bar": [{"version": "3.0.0", "name": "third_package"}],
                },
            },
        },
    }


def test_serialize_node__none_function_packages():
    # GIVEN a tool calling node with no function packages
    def foo():
        pass

    class MyToolCallingNode(ToolCallingNode):
        functions = [foo]

    # AND a workflow with the tool calling node
    class Workflow(BaseWorkflow):
        graph = MyToolCallingNode

    # WHEN the workflow is serialized
    workflow_display = get_workflow_display(workflow_class=Workflow)
    serialized_workflow: dict = workflow_display.serialize()

    # THEN the node should properly serialize the functions
    my_tool_calling_node = next(
        node
        for node in serialized_workflow["workflow_raw_data"]["nodes"]
        if node["id"] == str(MyToolCallingNode.__id__)
    )

    function_packages_attribute = next(
        attribute for attribute in my_tool_calling_node["attributes"] if attribute["name"] == "function_packages"
    )

    assert function_packages_attribute == {
        "id": "05c86dea-ea4b-46c4-883b-7912a6680491",
        "name": "function_packages",
        "value": {"type": "CONSTANT_VALUE", "value": {"type": "JSON", "value": None}},
    }
