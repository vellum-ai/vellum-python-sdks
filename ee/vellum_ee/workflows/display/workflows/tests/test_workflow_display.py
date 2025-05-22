import pytest
from uuid import uuid4

from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.nodes.core.inline_subworkflow_node.node import InlineSubworkflowNode
from vellum.workflows.nodes.core.retry_node.node import RetryNode
from vellum.workflows.nodes.core.templating_node.node import TemplatingNode
from vellum.workflows.nodes.core.try_node.node import TryNode
from vellum.workflows.nodes.displayable.final_output_node.node import FinalOutputNode
from vellum.workflows.references.lazy import LazyReference
from vellum.workflows.workflows.base import BaseWorkflow
from vellum_ee.workflows.display.editor.types import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseNodeDisplay
from vellum_ee.workflows.display.nodes.vellum.retry_node import BaseRetryNodeDisplay
from vellum_ee.workflows.display.nodes.vellum.try_node import BaseTryNodeDisplay
from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display


def test_serialize_workflow__node_referenced_in_workflow_outputs_not_in_graph():
    # GIVEN a couple of nodes
    class InNode(BaseNode):
        pass

    class OutNode(BaseNode):
        class Outputs(BaseNode.Outputs):
            foo: str

    # AND A workflow that references the OutNode in its outputs but only has the InNode in its graph
    class Workflow(BaseWorkflow):
        graph = InNode

        class Outputs(BaseWorkflow.Outputs):
            final = OutNode.Outputs.foo

    # WHEN we serialize it
    workflow_display = get_workflow_display(workflow_class=Workflow)

    # THEN it should raise an error
    with pytest.raises(ValueError) as exc_info:
        workflow_display.serialize()

    # AND the error message should be user friendly
    assert str(exc_info.value) == "Failed to serialize output 'final': Reference to node 'OutNode' not found in graph."


def test_serialize_workflow__workflow_outputs_reference_non_node_outputs():
    # GIVEN one Workflow
    class FirstWorkflow(BaseWorkflow):
        class Outputs(BaseWorkflow.Outputs):
            foo = "bar"

    # AND A workflow that references the Outputs of that Workflow
    class Workflow(BaseWorkflow):
        class Outputs(BaseWorkflow.Outputs):
            final = FirstWorkflow.Outputs.foo

    # WHEN we serialize it
    workflow_display = get_workflow_display(workflow_class=Workflow)

    # THEN it should raise an error
    with pytest.raises(ValueError) as exc_info:
        workflow_display.serialize()

    # AND the error message should be user friendly
    assert (
        str(exc_info.value)
        == """Failed to serialize output 'final': Reference to outputs \
'test_serialize_workflow__workflow_outputs_reference_non_node_outputs.<locals>.FirstWorkflow.Outputs' is invalid."""
    )


def test_serialize_workflow__node_display_class_not_registered():
    # GIVEN a workflow with a node that has a display class referencing display data
    class StartNode(BaseNode):
        class Outputs(BaseNode.Outputs):
            result: str

    class StartNodeDisplay(BaseNodeDisplay[StartNode]):
        node_input_ids_by_name = {}
        display_data = NodeDisplayData(position=NodeDisplayPosition(x=0, y=0), width=None, height=None)

    class MyWorkflow(BaseWorkflow):
        graph = StartNode

        class Outputs(BaseWorkflow.Outputs):
            answer = StartNode.Outputs.result

    # WHEN we serialize it
    workflow_display = get_workflow_display(workflow_class=MyWorkflow)
    data = workflow_display.serialize()

    # THEN it should should succeed
    assert data is not None


def test_get_event_display_context__node_display_filled_without_base_display():
    # GIVEN a simple workflow
    class StartNode(BaseNode):
        class Outputs(BaseNode.Outputs):
            foo: str

    class MyWorkflow(BaseWorkflow):
        graph = StartNode

    # WHEN we gather the event display context
    display_context = get_workflow_display(workflow_class=MyWorkflow).get_event_display_context()

    # THEN the node display should be included
    assert StartNode.__id__ in display_context.node_displays
    node_event_display = display_context.node_displays[StartNode.__id__]

    # AND so should their output ids
    assert StartNode.__output_ids__ == node_event_display.output_display


def test_get_event_display_context__node_display_filled_without_output_display():
    # GIVEN a simple workflow
    class StartNode(BaseNode):
        class Outputs(BaseNode.Outputs):
            foo: str

    class MyWorkflow(BaseWorkflow):
        graph = StartNode

    class StartNodeDisplay(BaseNodeDisplay[StartNode]):
        pass

    # WHEN we gather the event display context
    display_context = get_workflow_display(workflow_class=MyWorkflow).get_event_display_context()

    # THEN the node display should be included
    assert StartNode.__id__ in display_context.node_displays
    node_event_display = display_context.node_displays[StartNode.__id__]

    # AND so should their output ids
    assert node_event_display.output_display.keys() == {"foo"}


def test_get_event_display_context__node_display_to_include_subworkflow_display():
    # GIVEN a simple workflow
    class InnerNode(BaseNode):
        pass

    class Subworkflow(BaseWorkflow):
        graph = InnerNode

    # AND a workflow that includes the subworkflow
    class SubworkflowNode(InlineSubworkflowNode):
        subworkflow = Subworkflow

    class MyWorkflow(BaseWorkflow):
        graph = SubworkflowNode

    # WHEN we gather the event display context
    display_context = get_workflow_display(workflow_class=MyWorkflow).get_event_display_context()

    # THEN the subworkflow display should be included
    assert SubworkflowNode.__id__ in display_context.node_displays
    node_event_display = display_context.node_displays[SubworkflowNode.__id__]

    assert node_event_display.subworkflow_display is not None
    assert InnerNode.__id__ in node_event_display.subworkflow_display.node_displays


@pytest.mark.parametrize(
    ["AdornmentNode", "AdornmentNodeDisplay", "expected_adornment_output_names"],
    [
        [RetryNode, BaseRetryNodeDisplay, {"foo"}],
        [TryNode, BaseTryNodeDisplay, {"foo", "error"}],
    ],
    ids=["retry_node", "try_node"],
)
def test_get_event_display_context__node_display_for_adornment_nodes(
    AdornmentNode,
    AdornmentNodeDisplay,
    expected_adornment_output_names,
):
    # GIVEN a simple workflow with an adornment
    @AdornmentNode.wrap()
    class MyNode(BaseNode):
        class Outputs(BaseNode.Outputs):
            foo: str

    class MyWorkflow(BaseWorkflow):
        graph = MyNode

    # AND a display class for the node
    adornment_node_id = uuid4()
    inner_node_id = uuid4()

    @AdornmentNodeDisplay.wrap(node_id=adornment_node_id)
    class MyNodeDisplay(BaseNodeDisplay[MyNode]):
        node_id = inner_node_id

    # WHEN we gather the event display context
    display_context = get_workflow_display(workflow_class=MyWorkflow).get_event_display_context()

    # THEN the subworkflow display should be included
    assert adornment_node_id in display_context.node_displays
    node_event_display = display_context.node_displays[adornment_node_id]
    assert node_event_display.subworkflow_display is not None
    assert inner_node_id in node_event_display.subworkflow_display.node_displays

    # AND the inner node should have the correct outputs
    inner_node_display = node_event_display.subworkflow_display.node_displays[inner_node_id]
    assert inner_node_display.output_display.keys() == {"foo"}
    assert node_event_display.output_display.keys() == expected_adornment_output_names


def test_get_event_display_context__templating_node_input_display():
    # GIVEN a simple workflow with a templating node referencing another node output
    class DataNode(BaseNode):
        class Outputs:
            bar: str

    class MyNode(TemplatingNode):
        inputs = {"foo": DataNode.Outputs.bar}

    class MyWorkflow(BaseWorkflow):
        graph = DataNode >> MyNode

    # WHEN we gather the event display context
    display_context = get_workflow_display(workflow_class=MyWorkflow).get_event_display_context()

    # THEN the subworkflow display should be included
    assert MyNode.__id__ in display_context.node_displays
    node_event_display = display_context.node_displays[MyNode.__id__]

    assert node_event_display.input_display.keys() == {"inputs.foo"}


def test_get_event_display_context__node_display_for_mutiple_adornments():
    # GIVEN a simple workflow with multiple adornments
    @TryNode.wrap()
    @RetryNode.wrap()
    class MyNode(BaseNode):
        class Outputs(BaseNode.Outputs):
            foo: str

    class MyWorkflow(BaseWorkflow):
        graph = MyNode

    # AND a display class for the node
    node_id = uuid4()
    inner_node_id = uuid4()
    innermost_node_id = uuid4()

    @BaseTryNodeDisplay.wrap(node_id=node_id)
    @BaseRetryNodeDisplay.wrap(node_id=inner_node_id)
    class MyNodeDisplay(BaseNodeDisplay[MyNode]):
        node_id = innermost_node_id

    # WHEN we gather the event display context
    display_context = get_workflow_display(workflow_class=MyWorkflow).get_event_display_context()

    # THEN the subworkflow display should be included
    assert node_id in display_context.node_displays
    node_event_display = display_context.node_displays[node_id]
    assert node_event_display.subworkflow_display

    # AND the inner node should be included
    assert inner_node_id in node_event_display.subworkflow_display.node_displays
    inner_node_event_display = node_event_display.subworkflow_display.node_displays[inner_node_id]
    assert inner_node_event_display.subworkflow_display

    # AND the innermost node should be included
    assert innermost_node_id in inner_node_event_display.subworkflow_display.node_displays
    innermost_node_event_display = inner_node_event_display.subworkflow_display.node_displays[innermost_node_id]
    assert not innermost_node_event_display.subworkflow_display


def test_get_event_display_context__workflow_output_display_with_none():
    # GIVEN a workflow with a workflow output that is None
    class MyWorkflow(BaseWorkflow):
        class Outputs(BaseWorkflow.Outputs):
            foo = None
            bar = "baz"

    # WHEN we gather the event display context
    display_context = get_workflow_display(workflow_class=MyWorkflow).get_event_display_context()

    # THEN the workflow output display should be included
    assert display_context.workflow_outputs.keys() == {"foo", "bar"}


def test_serialize_workflow__inherited_node_display_class_not_registered():
    # GIVEN a node meant to be used as a base
    class StartNode(BaseNode):
        class Outputs(BaseNode.Outputs):
            result: str

    # AND a node that inherits from it
    class InheritedNode(StartNode):
        foo: str

    # AND a workflow that uses the inherited node
    class MyWorkflow(BaseWorkflow):
        graph = InheritedNode

        class Outputs(BaseWorkflow.Outputs):
            answer = InheritedNode.Outputs.result

    # WHEN we serialize it
    workflow_display = get_workflow_display(workflow_class=MyWorkflow)
    data = workflow_display.serialize()

    # THEN it should should succeed
    assert data is not None


def test_serialize_workflow__inherited_workflow_display_class_not_registered():
    # GIVEN a node
    class StartNode(BaseNode):
        class Outputs(BaseNode.Outputs):
            result: str

    # AND a workflow that uses the node
    class MyWorkflow(BaseWorkflow):
        graph = StartNode

    # AND a workflow that inherits from it
    class InheritedWorkflow(MyWorkflow):
        class Outputs(MyWorkflow.Outputs):
            answer = StartNode.Outputs.result

    # WHEN we serialize it
    workflow_display = get_workflow_display(workflow_class=InheritedWorkflow)
    data = workflow_display.serialize()

    # THEN it should should succeed
    assert data is not None


def test_serialize_workflow__terminal_node_mismatches_workflow_output_name():
    # GIVEN a node
    class ExitNode(FinalOutputNode):
        class Outputs(FinalOutputNode.Outputs):
            value = "hello"

    # AND a workflow that uses the node
    class MyWorkflow(BaseWorkflow):
        graph = ExitNode

        class Outputs(BaseWorkflow.Outputs):
            answer = ExitNode.Outputs.value

    # WHEN we serialize it
    workflow_display = get_workflow_display(workflow_class=MyWorkflow)
    data = workflow_display.serialize()

    # THEN it should have an output name that matches the workflow output
    assert isinstance(data["workflow_raw_data"], dict)
    assert isinstance(data["workflow_raw_data"]["nodes"], list)
    terminal_node = [
        node for node in data["workflow_raw_data"]["nodes"] if isinstance(node, dict) and node["type"] == "TERMINAL"
    ][0]
    assert isinstance(terminal_node["data"], dict)
    assert terminal_node["data"]["name"] == "answer"

    # AND the output variable should have the correct name
    assert isinstance(data["output_variables"], list)
    assert isinstance(data["output_variables"][0], dict)
    assert data["output_variables"][0]["key"] == "answer"
    assert data["output_variables"][0]["type"] == "STRING"

    # AND the output value should have the correct name
    output_variable_id = data["output_variables"][0]["id"]
    assert isinstance(data["workflow_raw_data"]["output_values"], list)
    assert isinstance(data["workflow_raw_data"]["output_values"][0], dict)
    assert data["workflow_raw_data"]["output_values"][0]["output_variable_id"] == output_variable_id
    assert data["workflow_raw_data"]["output_values"][0]["value"] == {
        "type": "NODE_OUTPUT",
        "node_id": str(ExitNode.__id__),
        "node_output_id": str(ExitNode.__output_ids__["value"]),
    }


def test_serialize_workflow__nested_lazy_reference():
    # GIVEN an inner node that references the output of an outer node
    class InnerNode(BaseNode):
        foo = LazyReference[str]("OuterNode.Outputs.bar")

        class Outputs(BaseNode.Outputs):
            foo = "foo"

    # AND a workflow that uses the inner node
    class InnerWorkflow(BaseWorkflow):
        graph = InnerNode

        class Outputs(BaseWorkflow.Outputs):
            foo = InnerNode.Outputs.foo

    # AND a subworkflow that uses the inner workflow
    class SubworkflowNode(InlineSubworkflowNode):
        subworkflow = InnerWorkflow

    # AND the outer node
    class OuterNode(BaseNode):
        class Outputs(BaseNode.Outputs):
            bar: str

    # AND a workflow that uses the subworkflow node and the outer node
    class MyWorkflow(BaseWorkflow):
        graph = SubworkflowNode >> OuterNode

        class Outputs(BaseWorkflow.Outputs):
            answer = SubworkflowNode.Outputs.foo

    # WHEN we serialize it
    workflow_display = get_workflow_display(workflow_class=MyWorkflow)
    data: dict = workflow_display.serialize()

    # THEN it should have properly serialized the lazy reference
    subworkflow_node = next(
        node for node in data["workflow_raw_data"]["nodes"] if isinstance(node, dict) and node["type"] == "SUBWORKFLOW"
    )
    inner_node = next(
        node
        for node in subworkflow_node["data"]["workflow_raw_data"]["nodes"]
        if isinstance(node, dict) and node["type"] == "GENERIC"
    )

    assert inner_node["attributes"][0]["value"] == {
        "type": "NODE_OUTPUT",
        "node_id": str(OuterNode.__id__),
        "node_output_id": str(OuterNode.__output_ids__["bar"]),
    }


def test_serialize_workflow__array_values():
    # GIVEN a node with array and nested array values
    class MyNode(BaseNode):
        class Outputs(BaseNode.Outputs):
            array_value = ["item1", "item2", "item3"]
            nested_array_value = [["item1", "item2", "item3"], ["item4", "item5", "item6"]]
            mixed_array_value = [["item1"], "item2", "item3"]

    # AND a workflow that uses these outputs
    class MyWorkflow(BaseWorkflow):
        graph = MyNode

        class Outputs(BaseWorkflow.Outputs):
            array_output = MyNode.Outputs.array_value
            nested_array_output = MyNode.Outputs.nested_array_value

    # WHEN we serialize it
    workflow_display = get_workflow_display(workflow_class=MyWorkflow)
    data = workflow_display.serialize()

    # THEN it should properly serialize the array and dictionary values
    assert isinstance(data["workflow_raw_data"], dict)
    assert isinstance(data["workflow_raw_data"]["nodes"], list)
    raw_nodes = data["workflow_raw_data"]["nodes"]
    generic_nodes = [node for node in raw_nodes if isinstance(node, dict) and node["type"] == "GENERIC"]
    assert len(generic_nodes) > 0
    my_node = generic_nodes[0]

    outputs = my_node["outputs"]
    assert isinstance(outputs, list)

    array_outputs = [val for val in outputs if isinstance(val, dict) and val["name"] == "array_value"]
    assert len(array_outputs) > 0
    array_output = array_outputs[0]

    assert isinstance(array_output, dict)
    assert "value" in array_output
    assert array_output["value"] == {
        "type": "CONSTANT_VALUE",
        "value": {"type": "JSON", "value": ["item1", "item2", "item3"]},
    }

    nested_array_outputs = [val for val in outputs if isinstance(val, dict) and val["name"] == "nested_array_value"]
    assert len(nested_array_outputs) > 0
    nested_array_output = nested_array_outputs[0]

    assert isinstance(nested_array_output, dict)
    assert "value" in nested_array_output
    assert nested_array_output["value"] == {
        "type": "CONSTANT_VALUE",
        "value": {"type": "JSON", "value": [["item1", "item2", "item3"], ["item4", "item5", "item6"]]},
    }

    mixed_array_outputs = [val for val in outputs if isinstance(val, dict) and val["name"] == "mixed_array_value"]
    assert len(mixed_array_outputs) > 0
    mixed_array_output = mixed_array_outputs[0]

    assert isinstance(mixed_array_output, dict)
    assert "value" in mixed_array_output
    assert mixed_array_output["value"] == {
        "type": "CONSTANT_VALUE",
        "value": {"type": "JSON", "value": [["item1"], "item2", "item3"]},
    }


def test_serialize_workflow__array_reference():
    # GIVEN a node with array containing non-constant values (node references)
    class FirstNode(BaseNode):
        class Outputs(BaseNode.Outputs):
            value1: str
            value2: str

    class SecondNode(BaseNode):
        class Outputs(BaseNode.Outputs):
            # Array containing a mix of constants and node references
            mixed_array = ["constant1", FirstNode.Outputs.value1, "constant2", FirstNode.Outputs.value2]
            mixed_nested_array = [["constant1", FirstNode.Outputs.value1], ["constant2", FirstNode.Outputs.value2]]

    # AND a workflow that uses these outputs
    class MyWorkflow(BaseWorkflow):
        graph = FirstNode >> SecondNode

        class Outputs(BaseWorkflow.Outputs):
            mixed_array_output = SecondNode.Outputs.mixed_array
            mixed_nested_array_output = SecondNode.Outputs.mixed_nested_array

    # WHEN we serialize it
    workflow_display = get_workflow_display(workflow_class=MyWorkflow)
    data = workflow_display.serialize()

    # THEN it should serialize as an ARRAY_REFERENCE
    assert isinstance(data["workflow_raw_data"], dict)
    assert isinstance(data["workflow_raw_data"]["nodes"], list)
    assert len(data["workflow_raw_data"]["nodes"]) == 5
    second_node = data["workflow_raw_data"]["nodes"][2]
    assert isinstance(second_node, dict)

    assert "outputs" in second_node
    assert isinstance(second_node["outputs"], list)
    outputs = second_node["outputs"]

    mixed_array_outputs = [val for val in outputs if isinstance(val, dict) and val["name"] == "mixed_array"]
    assert len(mixed_array_outputs) > 0
    mixed_array_output = mixed_array_outputs[0]

    assert isinstance(mixed_array_output, dict)
    assert "value" in mixed_array_output
    assert mixed_array_output["value"] == {
        "type": "ARRAY_REFERENCE",
        "items": [
            {"type": "CONSTANT_VALUE", "value": {"type": "STRING", "value": "constant1"}},
            {
                "type": "NODE_OUTPUT",
                "node_id": "702a08b5-61e8-4a7a-a83d-77f49e39c5be",
                "node_output_id": "419b6afa-fab5-493a-ba1e-4606f4641616",
            },
            {"type": "CONSTANT_VALUE", "value": {"type": "STRING", "value": "constant2"}},
            {
                "type": "NODE_OUTPUT",
                "node_id": "702a08b5-61e8-4a7a-a83d-77f49e39c5be",
                "node_output_id": "d1cacc41-478d-49a3-a6b3-1ba2d51291e2",
            },
        ],
    }

    mixed_nested_array_outputs = [
        val for val in outputs if isinstance(val, dict) and val["name"] == "mixed_nested_array"
    ]
    assert len(mixed_nested_array_outputs) > 0
    mixed_nested_array_output = mixed_nested_array_outputs[0]

    assert isinstance(mixed_nested_array_output, dict)
    assert "value" in mixed_nested_array_output
    assert mixed_nested_array_output["value"] == {
        "type": "ARRAY_REFERENCE",
        "items": [
            {
                "type": "ARRAY_REFERENCE",
                "items": [
                    {"type": "CONSTANT_VALUE", "value": {"type": "STRING", "value": "constant1"}},
                    {
                        "type": "NODE_OUTPUT",
                        "node_id": "702a08b5-61e8-4a7a-a83d-77f49e39c5be",
                        "node_output_id": "419b6afa-fab5-493a-ba1e-4606f4641616",
                    },
                ],
            },
            {
                "type": "ARRAY_REFERENCE",
                "items": [
                    {"type": "CONSTANT_VALUE", "value": {"type": "STRING", "value": "constant2"}},
                    {
                        "type": "NODE_OUTPUT",
                        "node_id": "702a08b5-61e8-4a7a-a83d-77f49e39c5be",
                        "node_output_id": "d1cacc41-478d-49a3-a6b3-1ba2d51291e2",
                    },
                ],
            },
        ],
    }


def test_serialize_workflow__dict_values():
    # GIVEN a node with a dictionary value
    class MyNode(BaseNode):
        class Outputs(BaseNode.Outputs):
            dict_value = {"key1": "value1", "key2": "value2"}
            nested_dict_value = {
                "key1": {"nested_key1": "value1", "nested_key2": "value2"},
                "key2": {"nested_key1": "value1", "nested_key2": "value2"},
            }
            mixed_dict_value = {"key1": "value1", "key2": {"key3": "value3", "key4": "value4"}}

    # AND a workflow that uses these outputs
    class MyWorkflow(BaseWorkflow):
        graph = MyNode

        class Outputs(BaseWorkflow.Outputs):
            dict_output = MyNode.Outputs.dict_value

    # WHEN we serialize it
    workflow_display = get_workflow_display(workflow_class=MyWorkflow)
    data = workflow_display.serialize()

    # THEN it should serialize as a CONSTANT_VALUE
    assert isinstance(data["workflow_raw_data"], dict)
    assert isinstance(data["workflow_raw_data"]["nodes"], list)
    my_node = next(
        node for node in data["workflow_raw_data"]["nodes"] if isinstance(node, dict) and node["type"] == "GENERIC"
    )

    assert isinstance(my_node["outputs"], list)
    outputs = my_node["outputs"]

    dict_output = next(val for val in outputs if isinstance(val, dict) and val["name"] == "dict_value")
    assert isinstance(dict_output, dict)
    assert "value" in dict_output
    assert dict_output["value"] == {
        "type": "CONSTANT_VALUE",
        "value": {"type": "JSON", "value": {"key1": "value1", "key2": "value2"}},
    }

    nested_dict_output = next(val for val in outputs if isinstance(val, dict) and val["name"] == "nested_dict_value")
    assert isinstance(nested_dict_output, dict)
    assert "value" in nested_dict_output
    assert nested_dict_output["value"] == {
        "type": "CONSTANT_VALUE",
        "value": {
            "type": "JSON",
            "value": {
                "key1": {"nested_key1": "value1", "nested_key2": "value2"},
                "key2": {"nested_key1": "value1", "nested_key2": "value2"},
            },
        },
    }

    mixed_dict_output = next(val for val in outputs if isinstance(val, dict) and val["name"] == "mixed_dict_value")
    assert isinstance(mixed_dict_output, dict)
    assert "value" in mixed_dict_output
    assert mixed_dict_output["value"] == {
        "type": "CONSTANT_VALUE",
        "value": {"type": "JSON", "value": {"key1": "value1", "key2": {"key3": "value3", "key4": "value4"}}},
    }


def test_serialize_workflow__dict_reference():
    # GIVEN a node with a dictionary containing non-constant values (node references)
    class FirstNode(BaseNode):
        class Outputs(BaseNode.Outputs):
            value1: str

    class SecondNode(BaseNode):
        class Outputs(BaseNode.Outputs):
            # Dictionary containing a mix of constants and node references
            mixed_dict = {
                "key1": "constant1",
                "key2": FirstNode.Outputs.value1,
                "key3": "constant2",
                "key4": FirstNode.Outputs.value1,
            }
            mixed_nested_dict = {
                "key1": {"key1": "constant1", "key2": FirstNode.Outputs.value1},
                "key2": {"key1": "constant2", "key2": FirstNode.Outputs.value1},
            }

    # AND a workflow that uses these outputs
    class MyWorkflow(BaseWorkflow):
        graph = FirstNode >> SecondNode

        class Outputs(BaseWorkflow.Outputs):
            mixed_dict_output = SecondNode.Outputs.mixed_dict
            mixed_nested_dict_output = SecondNode.Outputs.mixed_nested_dict

    # WHEN we serialize it
    workflow_display = get_workflow_display(workflow_class=MyWorkflow)
    data = workflow_display.serialize()

    # THEN it should serialize as a CONSTANT_VALUE
    assert isinstance(data["workflow_raw_data"], dict)
    assert isinstance(data["workflow_raw_data"]["nodes"], list)
    second_node = data["workflow_raw_data"]["nodes"][2]

    assert isinstance(second_node, dict)
    assert "outputs" in second_node
    assert isinstance(second_node["outputs"], list)

    outputs = second_node["outputs"]
    mixed_dict_output = next(val for val in outputs if isinstance(val, dict) and val["name"] == "mixed_dict")
    assert isinstance(mixed_dict_output, dict)
    assert "value" in mixed_dict_output
    assert mixed_dict_output["value"] == {
        "type": "DICTIONARY_REFERENCE",
        "entries": [
            {
                "id": "b528ce26-68ee-42ba-828d-199441810685",
                "key": "key1",
                "value": {"type": "CONSTANT_VALUE", "value": {"type": "STRING", "value": "constant1"}},
            },
            {
                "id": "a7acccfe-2f80-42ee-a307-c1eb0b137c2b",
                "key": "key2",
                "value": {
                    "type": "NODE_OUTPUT",
                    "node_id": "13b4f5c0-e6aa-4ef9-9a1a-79476bc32500",
                    "node_output_id": "50a6bc11-afb3-49f2-879c-b28f5e16d974",
                },
            },
            {
                "id": "8f41013e-7a9f-4659-ac17-c25c6ec6fe99",
                "key": "key3",
                "value": {"type": "CONSTANT_VALUE", "value": {"type": "STRING", "value": "constant2"}},
            },
            {
                "id": "609e84e8-573a-44ea-b3aa-82c3f3cc2c36",
                "key": "key4",
                "value": {
                    "type": "NODE_OUTPUT",
                    "node_id": "13b4f5c0-e6aa-4ef9-9a1a-79476bc32500",
                    "node_output_id": "50a6bc11-afb3-49f2-879c-b28f5e16d974",
                },
            },
        ],
    }

    mixed_nested_dict_output = next(
        val for val in outputs if isinstance(val, dict) and val["name"] == "mixed_nested_dict"
    )
    assert isinstance(mixed_nested_dict_output, dict)
    assert "value" in mixed_nested_dict_output
    assert mixed_nested_dict_output["value"] == {
        "type": "DICTIONARY_REFERENCE",
        "entries": [
            {
                "id": "02abe9d0-bf93-4eea-b34a-902dae7c2b90",
                "key": "key1",
                "value": {
                    "type": "DICTIONARY_REFERENCE",
                    "entries": [
                        {
                            "id": "b528ce26-68ee-42ba-828d-199441810685",
                            "key": "key1",
                            "value": {"type": "CONSTANT_VALUE", "value": {"type": "STRING", "value": "constant1"}},
                        },
                        {
                            "id": "a7acccfe-2f80-42ee-a307-c1eb0b137c2b",
                            "key": "key2",
                            "value": {
                                "type": "NODE_OUTPUT",
                                "node_id": "13b4f5c0-e6aa-4ef9-9a1a-79476bc32500",
                                "node_output_id": "50a6bc11-afb3-49f2-879c-b28f5e16d974",
                            },
                        },
                    ],
                },
            },
            {
                "id": "c8640477-13cc-412e-82cc-35cbe9e78ff2",
                "key": "key2",
                "value": {
                    "type": "DICTIONARY_REFERENCE",
                    "entries": [
                        {
                            "id": "86709f21-a811-4351-993e-a8e9f1c7774f",
                            "key": "key1",
                            "value": {"type": "CONSTANT_VALUE", "value": {"type": "STRING", "value": "constant2"}},
                        },
                        {
                            "id": "a7acccfe-2f80-42ee-a307-c1eb0b137c2b",
                            "key": "key2",
                            "value": {
                                "type": "NODE_OUTPUT",
                                "node_id": "13b4f5c0-e6aa-4ef9-9a1a-79476bc32500",
                                "node_output_id": "50a6bc11-afb3-49f2-879c-b28f5e16d974",
                            },
                        },
                    ],
                },
            },
        ],
    }
