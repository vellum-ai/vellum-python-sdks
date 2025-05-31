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


def test_serialize_node__function_configs():
    # GIVEN a tool calling node with function packages
    def two_packages():
        pass

    def one_package():
        pass

    def runtime_only():
        pass

    def packages_only():
        pass

    def no_config():
        pass

    class MyToolCallingNode(ToolCallingNode):
        functions = [two_packages, one_package, runtime_only, packages_only, no_config]
        function_configs = {
            "two_packages": {
                "runtime": "PYTHON_3_11_6",
                "packages": [
                    CodeExecutionPackage(name="test_package_1", version="1.0.0"),
                    CodeExecutionPackage(name="test_package_2", version="2.0.0"),
                ],
            },
            "one_package": {
                "runtime": "PYTHON_3_11_6",
                "packages": [CodeExecutionPackage(name="test_package_3", version="3.0.0")],
            },
            "runtime_only": {
                "runtime": "PYTHON_3_11_6",
            },
            "packages_only": {
                "packages": [CodeExecutionPackage(name="test_package_4", version="4.0.0")],
            },
            # no_config does not specify config
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

    functions_attribute = next(
        attribute for attribute in my_tool_calling_node["attributes"] if attribute["name"] == "functions"
    )
    assert functions_attribute == {
        "id": "d1841455-4edd-4172-9e74-8bdebd3ea83a",
        "name": "functions",
        "value": {
            "type": "CONSTANT_VALUE",
            "value": {
                "type": "JSON",
                "value": [
                    {
                        "type": "CODE_EXECUTION",
                        "definition": {
                            "state": None,
                            "cache_config": None,
                            "name": "two_packages",
                            "description": None,
                            "parameters": {"type": "object", "properties": {}, "required": []},
                            "forced": None,
                            "strict": None,
                        },
                        "src": "    def two_packages():\n        pass\n",
                        "runtime": "PYTHON_3_11_6",
                        "packages": [
                            {"version": "1.0.0", "name": "test_package_1"},
                            {"version": "2.0.0", "name": "test_package_2"},
                        ],
                    },
                    {
                        "type": "CODE_EXECUTION",
                        "definition": {
                            "state": None,
                            "cache_config": None,
                            "name": "one_package",
                            "description": None,
                            "parameters": {"type": "object", "properties": {}, "required": []},
                            "forced": None,
                            "strict": None,
                        },
                        "src": "    def one_package():\n        pass\n",
                        "runtime": "PYTHON_3_11_6",
                        "packages": [{"version": "3.0.0", "name": "test_package_3"}],
                    },
                    {
                        "type": "CODE_EXECUTION",
                        "definition": {
                            "state": None,
                            "cache_config": None,
                            "name": "runtime_only",
                            "description": None,
                            "parameters": {"type": "object", "properties": {}, "required": []},
                            "forced": None,
                            "strict": None,
                        },
                        "src": "    def runtime_only():\n        pass\n",
                        "runtime": "PYTHON_3_11_6",
                        "packages": [],  # no packages specified
                    },
                    {
                        "type": "CODE_EXECUTION",
                        "definition": {
                            "state": None,
                            "cache_config": None,
                            "name": "packages_only",
                            "description": None,
                            "parameters": {"type": "object", "properties": {}, "required": []},
                            "forced": None,
                            "strict": None,
                        },
                        "src": "    def packages_only():\n        pass\n",
                        "runtime": "PYTHON_3_11_6",  # default runtime
                        "packages": [{"version": "4.0.0", "name": "test_package_4"}],
                    },
                    {
                        "type": "CODE_EXECUTION",
                        "definition": {
                            "state": None,
                            "cache_config": None,
                            "name": "no_config",
                            "description": None,
                            "parameters": {"type": "object", "properties": {}, "required": []},
                            "forced": None,
                            "strict": None,
                        },
                        "src": "    def no_config():\n        pass\n",
                        "runtime": "PYTHON_3_11_6",  # default runtime
                        "packages": [],  # no packages specified
                    },
                ],
            },
        },
    }


def test_serialize_node__function_configs__none():
    # GIVEN a tool calling node with no function configs
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

    functions = next(attribute for attribute in my_tool_calling_node["attributes"] if attribute["name"] == "functions")
    assert functions == {
        "id": "99a0e63a-d1f6-45be-9ead-ff2e5f57ff42",
        "name": "functions",
        "value": {
            "type": "CONSTANT_VALUE",
            "value": {
                "type": "JSON",
                "value": [
                    {
                        "type": "CODE_EXECUTION",
                        "definition": {
                            "state": None,
                            "cache_config": None,
                            "name": "foo",
                            "description": None,
                            "parameters": {"type": "object", "properties": {}, "required": []},
                            "forced": None,
                            "strict": None,
                        },
                        "src": "    def foo():\n        pass\n",
                        "runtime": "PYTHON_3_11_6",
                        "packages": [],
                    }
                ],
            },
        },
    }
