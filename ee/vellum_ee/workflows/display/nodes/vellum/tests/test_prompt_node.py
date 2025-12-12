import pytest
from uuid import UUID
from typing import Type

from vellum.client.types.prompt_parameters import PromptParameters
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
            "id": "e80bda60-b6b7-4c53-ad99-41d0bd47d3bd",
            "key": "attr",
            "value": {
                "combinator": "OR",
                "rules": [
                    {
                        "type": "NODE_OUTPUT",
                        "data": {
                            "node_id": str(OtherNode.__id__),
                            "output_id": "fa5eaae0-fd4a-48db-a3c8-8893653106cb",
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
        (_no_display_class, "f435df49-a8bf-4de0-bb49-ff5bb92de30e"),
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

    my_prompt_node = next(
        node for node in serialized_workflow["workflow_raw_data"]["nodes"] if node["id"] == str(MyPromptNode.__id__)
    )
    assert my_prompt_node["inputs"] == [
        {
            "id": "7c5d23b3-c5ed-4ed6-a685-43fbe9a9baf8",
            "key": "foo",
            "value": {
                "rules": [
                    {"type": "WORKFLOW_STATE", "data": {"state_variable_id": "dd3391bf-c818-4eba-aac5-912618ba412f"}}
                ],
                "combinator": "OR",
            },
        },
        {
            "id": "e138f06e-d705-46bc-8ac4-c844b0e9131a",
            "key": "bar",
            "value": {
                "rules": [{"type": "CONSTANT_VALUE", "data": {"type": "STRING", "value": "baz"}}],
                "combinator": "OR",
            },
        },
    ]

    # AND the prompt attributes should include a dictionary reference with the state reference
    prompt_inputs_attribute = next(
        attribute for attribute in my_prompt_node["attributes"] if attribute["name"] == "prompt_inputs"
    )
    assert prompt_inputs_attribute == {
        "id": "768704cc-812b-4a06-8348-ed46160a48f9",
        "name": "prompt_inputs",
        "value": {
            "type": "DICTIONARY_REFERENCE",
            "entries": [
                {
                    "id": "4a601d66-dc7d-4e48-a933-52a13fdc8d80",
                    "key": "foo",
                    "value": {
                        "type": "WORKFLOW_STATE",
                        "state_variable_id": "dd3391bf-c818-4eba-aac5-912618ba412f",
                    },
                },
                {
                    "id": "341f8329-5d5f-417b-a20d-e88234a17c49",
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
            "id": "2ce1605d-411f-4e94-a8a8-e85deb677b26",
            "block_type": "VARIABLE",
            "input_variable_id": "d70ce218-604d-4534-bd38-55a617ac0b8a",
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
    assert ports[0]["id"] == "4a1a1b86-f9f5-4364-a9cd-4929d4202e1d"
    assert ports[1]["id"] == "54e7594b-8ca3-4c45-9dd7-e0b973d7800f"
    assert ports[0]["name"] == "apple"
    assert ports[1]["name"] == "banana"

    # AND the legacy source_handle_id should be the default port
    assert my_prompt_node["data"]["source_handle_id"] == "4a1a1b86-f9f5-4364-a9cd-4929d4202e1d"


def test_serialize_node__prompt_parameters__dynamic_references():
    # GIVEN input definition
    class MyInputs(BaseInputs):
        input_value: str

    # AND a prompt node with PromptParameters containing dynamic references
    class DynamicPromptNode(InlinePromptNode):
        blocks = []
        ml_model = "gpt-4o"
        parameters = PromptParameters(custom_parameters={"json_schema": MyInputs.input_value})

    # AND a workflow with the prompt node
    class Workflow(BaseWorkflow[MyInputs, BaseState]):
        graph = DynamicPromptNode

    # WHEN the workflow is serialized
    workflow_display = get_workflow_display(workflow_class=Workflow)
    serialized_workflow: dict = workflow_display.serialize()

    # THEN the node should properly serialize the PromptParameters
    dynamic_prompt_node = next(
        node
        for node in serialized_workflow["workflow_raw_data"]["nodes"]
        if node["id"] == str(DynamicPromptNode.__id__)
    )

    # AND the parameters should be properly serialized in exec_config
    exec_config = dynamic_prompt_node["data"]["exec_config"]
    assert "parameters" in exec_config

    parameters = exec_config["parameters"]
    assert parameters == {}

    # AND the parameters should also be serialized in the attributes array
    parameters_attribute = next(
        (attr for attr in dynamic_prompt_node.get("attributes", []) if attr["name"] == "parameters"), None
    )
    assert parameters_attribute is not None
    assert parameters_attribute["name"] == "parameters"
    assert parameters_attribute["value"]["type"] == "DICTIONARY_REFERENCE"
    assert parameters_attribute["value"]["entries"] == [
        {
            "id": "652844a5-1f66-4211-ab0d-77c0c7d29a8a",
            "key": "stop",
            "value": {"type": "CONSTANT_VALUE", "value": {"type": "JSON", "value": None}},
        },
        {
            "id": "52def0d8-9d2b-4ff3-b9b7-e0212de3987d",
            "key": "temperature",
            "value": {"type": "CONSTANT_VALUE", "value": {"type": "JSON", "value": None}},
        },
        {
            "id": "3444b1bc-5cd3-413a-8023-6dfe08e1a7c6",
            "key": "max_tokens",
            "value": {"type": "CONSTANT_VALUE", "value": {"type": "JSON", "value": None}},
        },
        {
            "id": "36956dde-3a3d-47f3-982d-ee38e8b9d900",
            "key": "top_p",
            "value": {"type": "CONSTANT_VALUE", "value": {"type": "JSON", "value": None}},
        },
        {
            "id": "6755f4a6-ab90-4004-b3f7-495d06cdbdfa",
            "key": "top_k",
            "value": {"type": "CONSTANT_VALUE", "value": {"type": "JSON", "value": None}},
        },
        {
            "id": "ba427da5-55c8-4daf-a84e-4ac62784aa5e",
            "key": "frequency_penalty",
            "value": {"type": "CONSTANT_VALUE", "value": {"type": "JSON", "value": None}},
        },
        {
            "id": "736ccb67-efec-4958-a4c0-12f8c068856f",
            "key": "presence_penalty",
            "value": {"type": "CONSTANT_VALUE", "value": {"type": "JSON", "value": None}},
        },
        {
            "id": "1162f136-b72e-4848-8424-d1357053eb16",
            "key": "logit_bias",
            "value": {"type": "CONSTANT_VALUE", "value": {"type": "JSON", "value": None}},
        },
        {
            "id": "56958af3-ed56-409d-bf1d-a357f01b917d",
            "key": "custom_parameters",
            "value": {
                "entries": [
                    {
                        "id": "6e93e248-f818-4770-ba6a-fa859c28799b",
                        "key": "json_schema",
                        "value": {
                            "input_variable_id": "c02d1201-86d1-4364-b3b3-4fc6824db8a4",
                            "type": "WORKFLOW_INPUT",
                        },
                    }
                ],
                "type": "DICTIONARY_REFERENCE",
            },
        },
    ]
