import pytest
from uuid import UUID
from typing import Type

from vellum.client.types.variable_prompt_block import VariablePromptBlock
from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs import BaseInputs
from vellum.workflows.nodes import BaseNode
from vellum.workflows.nodes.displayable.inline_prompt_node.node import InlinePromptNode
from vellum.workflows.nodes.experimental.tool_calling_node.node import ToolCallingNode
from vellum.workflows.ports.port import Port
from vellum.workflows.references.lazy import LazyReference
from vellum.workflows.state.base import BaseState
from vellum_ee.workflows.display.nodes.vellum.inline_prompt_node import BaseInlinePromptNodeDisplay
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
        "id": "e8e1d3a1-bda7-4f6b-a329-127e3ba86149",
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
                {"key": "foo", "value": {"type": "CONSTANT_VALUE", "value": {"type": "STRING", "value": "bar"}}},
                {
                    "key": "baz",
                    "value": {"type": "WORKFLOW_INPUT", "input_variable_id": "8d57cf1d-147c-427b-9a5e-e5f6ab76e2eb"},
                },
            ],
        },
    }
