import pytest
from uuid import UUID
from typing import Type

from vellum.client.types.variable_prompt_block import VariablePromptBlock
from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs import BaseInputs
from vellum.workflows.nodes import BaseNode
from vellum.workflows.nodes.displayable.inline_prompt_node.node import InlinePromptNode
from vellum.workflows.ports.port import Port
from vellum.workflows.references.lazy import LazyReference
from vellum.workflows.state.base import BaseState
from vellum_ee.workflows.display.nodes.vellum.inline_prompt_node import BaseInlinePromptNodeDisplay
from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display


def test_serialize_node__lazy_reference_in_prompt_inputs():
    # GIVEN a prompt node with a lazy reference in the prompt inputs
    class LazyReferencePromptNode(InlinePromptNode):
        prompt_inputs = {"attr": LazyReference[str]("OtherNode.Outputs.result")}
        blocks = []
        ml_model = "gpt-4o"

    class OtherNode(BaseNode):
        class Outputs:
            result: str

    # AND a workflow with both nodes
    class Workflow(BaseWorkflow):
        graph = LazyReferencePromptNode >> OtherNode

    # WHEN the workflow is serialized
    workflow_display = get_workflow_display(workflow_class=Workflow)
    serialized_workflow: dict = workflow_display.serialize()

    # THEN the node should properly serialize the attribute reference
    lazy_reference_node = next(
        node
        for node in serialized_workflow["workflow_raw_data"]["nodes"]
        if node["id"] == str(LazyReferencePromptNode.__id__)
    )

    assert lazy_reference_node["inputs"] == [
        {
            "id": "aa81c1bc-d5d8-4ae8-8946-e9f4d0c1ab5f",
            "key": "attr",
            "value": {
                "combinator": "OR",
                "rules": [
                    {
                        "type": "NODE_OUTPUT",
                        "data": {
                            "node_id": str(OtherNode.__id__),
                            "output_id": "7f377cb8-4eca-4f1c-9239-9925f9495d84",
                        },
                    }
                ],
            },
        }
    ]


def _no_display_class(Node: Type[InlinePromptNode]):
    return None


def _display_class_with_node_input_ids_by_name(Node: Type[InlinePromptNode]):
    class PromptNodeDisplay(BaseInlinePromptNodeDisplay[Node]):  # type: ignore[valid-type]
        node_input_ids_by_name = {"foo": UUID("fba6a4d5-835a-4e99-afb7-f6a4aed15110")}

    return PromptNodeDisplay


def _display_class_with_node_input_ids_by_name_with_inputs_prefix(Node: Type[InlinePromptNode]):
    class PromptNodeDisplay(BaseInlinePromptNodeDisplay[Node]):  # type: ignore[valid-type]
        node_input_ids_by_name = {"prompt_inputs.foo": UUID("fba6a4d5-835a-4e99-afb7-f6a4aed15110")}

    return PromptNodeDisplay


@pytest.mark.parametrize(
    ["GetDisplayClass", "expected_input_id"],
    [
        (_no_display_class, "9b036991-67ff-4cd0-a4d7-b4ed581e8b6d"),
        (_display_class_with_node_input_ids_by_name, "fba6a4d5-835a-4e99-afb7-f6a4aed15110"),
        (_display_class_with_node_input_ids_by_name_with_inputs_prefix, "fba6a4d5-835a-4e99-afb7-f6a4aed15110"),
    ],
    ids=[
        "no_display_class",
        "display_class_with_node_input_ids_by_name",
        "display_class_with_node_input_ids_by_name_with_inputs_prefix",
    ],
)
def test_serialize_node__prompt_inputs(GetDisplayClass, expected_input_id):
    # GIVEN a prompt node with inputs
    class MyPromptNode(InlinePromptNode):
        prompt_inputs = {"foo": "bar"}
        blocks = []
        ml_model = "gpt-4o"

    # AND a workflow with the prompt node
    class Workflow(BaseWorkflow):
        graph = MyPromptNode

    # AND a display class
    GetDisplayClass(MyPromptNode)

    # WHEN the workflow is serialized
    workflow_display = get_workflow_display(workflow_class=Workflow)
    serialized_workflow: dict = workflow_display.serialize()

    # THEN the node should properly serialize the inputs
    my_prompt_node = next(
        node for node in serialized_workflow["workflow_raw_data"]["nodes"] if node["id"] == str(MyPromptNode.__id__)
    )

    assert my_prompt_node["inputs"] == [
        {
            "id": expected_input_id,
            "key": "foo",
            "value": {
                "rules": [
                    {
                        "type": "CONSTANT_VALUE",
                        "data": {
                            "type": "STRING",
                            "value": "bar",
                        },
                    }
                ],
                "combinator": "OR",
            },
        }
    ]


def test_serialize_node__prompt_inputs__state_reference():
    # GIVEN a state definition
    class MyState(BaseState):
        foo: str

    # AND a prompt node with inputs
    class MyPromptNode(InlinePromptNode):
        prompt_inputs = {"foo": MyState.foo, "bar": "baz"}
        blocks = []
        ml_model = "gpt-4o"

    # AND a workflow with the prompt node
    class Workflow(BaseWorkflow[BaseInputs, MyState]):
        graph = MyPromptNode

    # WHEN the workflow is serialized
    workflow_display = get_workflow_display(workflow_class=Workflow)
    serialized_workflow: dict = workflow_display.serialize()

    # THEN the node should skip the state reference input rule
    my_prompt_node = next(
        node for node in serialized_workflow["workflow_raw_data"]["nodes"] if node["id"] == str(MyPromptNode.__id__)
    )

    assert my_prompt_node["inputs"] == [
        {
            "id": "e47e0a80-afbb-4888-b06b-8dc78edd8572",
            "key": "foo",
            "value": {
                "rules": [],
                "combinator": "OR",
            },
        },
        {
            "id": "b83c40f7-0159-442f-af03-e80870363c52",
            "key": "bar",
            "value": {
                "rules": [
                    {
                        "type": "CONSTANT_VALUE",
                        "data": {
                            "type": "STRING",
                            "value": "baz",
                        },
                    }
                ],
                "combinator": "OR",
            },
        },
    ]

    # AND the prompt attributes should include a dictionary reference with the state reference
    prompt_inputs_attribute = next(
        attribute for attribute in my_prompt_node["attributes"] if attribute["name"] == "prompt_inputs"
    )
    assert prompt_inputs_attribute == {
        "id": "3b6e1363-e41b-458e-ad28-95a61fdedac1",
        "name": "prompt_inputs",
        "value": {
            "type": "DICTIONARY_REFERENCE",
            "entries": [
                {
                    "id": "feadab18-07c6-4790-adf0-28be20a5447a",
                    "key": "foo",
                    "value": {
                        "type": "WORKFLOW_STATE",
                        "state_variable_id": "45649791-c642-4405-aff9-a1fafd780ea1",
                    },
                },
                {
                    "id": "4f252277-d0a5-48ad-8cc5-be03bf0dbd19",
                    "key": "bar",
                    "value": {
                        "type": "CONSTANT_VALUE",
                        "value": {
                            "type": "STRING",
                            "value": "baz",
                        },
                    },
                },
            ],
        },
    }


def test_serialize_node__unreferenced_variable_block__still_serializes():
    # GIVEN a prompt node with an unreferenced variable block
    class MyPromptNode(InlinePromptNode):
        blocks = [VariablePromptBlock(input_variable="foo")]

    # AND a workflow with the prompt node
    class MyWorkflow(BaseWorkflow):
        graph = MyPromptNode

    # WHEN the prompt node is serialized
    workflow_display = get_workflow_display(workflow_class=MyWorkflow)
    serialized_workflow: dict = workflow_display.serialize()

    # THEN the node should skip the state reference input rule
    assert serialized_workflow["workflow_raw_data"]["nodes"][1]["data"]["exec_config"]["prompt_template_block_data"][
        "blocks"
    ] == [
        {
            "id": "fecbb5f3-e0a3-42ed-9774-6c68fd5db50c",
            "block_type": "VARIABLE",
            "input_variable_id": "ea3f6348-8553-4375-bd27-527df4e4f3c2",
            "state": "ENABLED",
            "cache_config": None,
        }
    ]

    # AND we should have a warning of the invalid reference
    # TODO: Come up with a proposal for how nodes should propagate warnings
    # warnings = list(workflow_display.errors)
    # assert len(warnings) == 1
    # assert "Missing input variable 'foo' for prompt block 0" in str(warnings[0])


def test_serialize_node__port_groups():
    # GIVEN a prompt node with ports
    class MyPromptNode(InlinePromptNode):
        class Ports(InlinePromptNode.Ports):
            apple = Port.on_if(LazyReference(lambda: MyPromptNode.Outputs.text).equals("apple"))
            banana = Port.on_if(LazyReference(lambda: MyPromptNode.Outputs.text).equals("banana"))

    # AND a workflow with the prompt node
    class MyWorkflow(BaseWorkflow):
        graph = MyPromptNode

    # WHEN the prompt node is serialized
    workflow_display = get_workflow_display(workflow_class=MyWorkflow)
    serialized_workflow: dict = workflow_display.serialize()

    # THEN the node should have the ports serialized
    my_prompt_node = next(
        node for node in serialized_workflow["workflow_raw_data"]["nodes"] if node["id"] == str(MyPromptNode.__id__)
    )
    ports = my_prompt_node["ports"]
    assert len(ports) == 2
    assert ports[0]["id"] == "149d97a4-3da3-44a9-95f7-ea7b8d38b877"
    assert ports[1]["id"] == "71f2d2b3-194f-4492-bc1c-a5ca1f60fb0a"
    assert ports[0]["name"] == "apple"
    assert ports[1]["name"] == "banana"

    # AND the legacy source_handle_id should be the default port
    assert my_prompt_node["data"]["source_handle_id"] == "149d97a4-3da3-44a9-95f7-ea7b8d38b877"
