import pytest
from uuid import UUID, uuid4
from typing import Any, Optional

from vellum.workflows.inputs import BaseInputs
from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.nodes.core.inline_subworkflow_node.node import InlineSubworkflowNode
from vellum.workflows.nodes.core.retry_node.node import RetryNode
from vellum.workflows.nodes.core.templating_node.node import TemplatingNode
from vellum.workflows.nodes.core.try_node.node import TryNode
from vellum.workflows.nodes.displayable.final_output_node.node import FinalOutputNode
from vellum.workflows.references.lazy import LazyReference
from vellum.workflows.state.base import BaseState
from vellum.workflows.triggers.integration import IntegrationTrigger
from vellum.workflows.types.core import JsonObject
from vellum.workflows.workflows.base import BaseWorkflow
from vellum_ee.workflows.display.editor.types import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes.base_node_display import BaseNodeDisplay
from vellum_ee.workflows.display.nodes.vellum.retry_node import BaseRetryNodeDisplay
from vellum_ee.workflows.display.nodes.vellum.try_node import BaseTryNodeDisplay
from vellum_ee.workflows.display.types import WorkflowDisplayContext
from vellum_ee.workflows.display.utils.exceptions import UserFacingException
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
    with pytest.raises(UserFacingException) as exc_info:
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
    serialized_workflow = workflow_display.serialize()

    # THEN it should successfully serialize the workflow output reference to a constant
    assert isinstance(serialized_workflow, dict)
    output_variables = serialized_workflow["output_variables"]
    assert isinstance(output_variables, list)
    assert output_variables == [{"id": "2b32416b-ccfc-4231-a3a6-d08e76327815", "key": "final", "type": "STRING"}]

    # AND the output value should be a constant value
    workflow_raw_data = serialized_workflow["workflow_raw_data"]
    assert isinstance(workflow_raw_data, dict)
    output_values = workflow_raw_data["output_values"]
    assert isinstance(output_values, list)
    assert output_values == [
        {
            "output_variable_id": "2b32416b-ccfc-4231-a3a6-d08e76327815",
            "value": {"type": "CONSTANT_VALUE", "value": {"type": "STRING", "value": "bar"}},
        }
    ]

    first_output_variable = output_variables[0]
    assert isinstance(first_output_variable, dict)
    first_output_value = output_values[0]
    assert isinstance(first_output_value, dict)
    assert first_output_variable["id"] == first_output_value["output_variable_id"]


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


def test_get_event_display_context__trigger_attributes_included():
    """Trigger attributes should be included in workflow_inputs for display in executions list."""

    # GIVEN a workflow with an integration trigger that has attributes
    class SlackTrigger(IntegrationTrigger):
        message: str
        channel: str

        class Config:
            provider = "COMPOSIO"
            integration_name = "SLACK"
            slug = "slack_new_message"

    class ProcessNode(BaseNode):
        pass

    class MyWorkflow(BaseWorkflow):
        graph = SlackTrigger >> ProcessNode

    # WHEN we gather the event display context
    display_context = get_workflow_display(workflow_class=MyWorkflow).get_event_display_context()

    # THEN the trigger attributes should be included in workflow_inputs
    assert "message" in display_context.workflow_inputs
    assert "channel" in display_context.workflow_inputs

    # AND the IDs should match the trigger attribute IDs
    trigger_attr_refs = SlackTrigger.attribute_references()
    assert display_context.workflow_inputs["message"] == trigger_attr_refs["message"].id
    assert display_context.workflow_inputs["channel"] == trigger_attr_refs["channel"].id


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
    second_node = next(
        node
        for node in data["workflow_raw_data"]["nodes"]
        if isinstance(node, dict)
        and "definition" in node
        and isinstance(node["definition"], dict)
        and node["definition"]["name"] == "SecondNode"
    )
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
                "node_id": "9a6037fd-e023-4331-8097-5144bacfc110",
                "node_output_id": "37521463-db12-41a3-ad6f-753165880356",
            },
            {"type": "CONSTANT_VALUE", "value": {"type": "STRING", "value": "constant2"}},
            {
                "type": "NODE_OUTPUT",
                "node_id": "9a6037fd-e023-4331-8097-5144bacfc110",
                "node_output_id": "b033bddf-987d-488d-8426-c5bb2dac7501",
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
                        "node_id": "9a6037fd-e023-4331-8097-5144bacfc110",
                        "node_output_id": "37521463-db12-41a3-ad6f-753165880356",
                    },
                ],
            },
            {
                "type": "ARRAY_REFERENCE",
                "items": [
                    {"type": "CONSTANT_VALUE", "value": {"type": "STRING", "value": "constant2"}},
                    {
                        "type": "NODE_OUTPUT",
                        "node_id": "9a6037fd-e023-4331-8097-5144bacfc110",
                        "node_output_id": "b033bddf-987d-488d-8426-c5bb2dac7501",
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
                "id": "c717464d-127e-4970-a3d8-31761dd83deb",
                "key": "key1",
                "value": {"type": "CONSTANT_VALUE", "value": {"type": "STRING", "value": "constant1"}},
            },
            {
                "id": "ca19400f-9cce-4b4f-860f-63c98f43ad88",
                "key": "key2",
                "value": {
                    "type": "NODE_OUTPUT",
                    "node_id": "0f81f7b9-392b-4f0e-8584-0ff040fba961",
                    "node_output_id": "0b63e869-e978-4ec9-9f47-0cc1c7e22076",
                },
            },
            {
                "id": "10df74b1-56f8-4414-8042-3d4f5a51314d",
                "key": "key3",
                "value": {"type": "CONSTANT_VALUE", "value": {"type": "STRING", "value": "constant2"}},
            },
            {
                "id": "4803c0f8-e582-4693-b9c3-1d6d54f999b1",
                "key": "key4",
                "value": {
                    "type": "NODE_OUTPUT",
                    "node_id": "0f81f7b9-392b-4f0e-8584-0ff040fba961",
                    "node_output_id": "0b63e869-e978-4ec9-9f47-0cc1c7e22076",
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
                "id": "c717464d-127e-4970-a3d8-31761dd83deb",
                "key": "key1",
                "value": {
                    "type": "DICTIONARY_REFERENCE",
                    "entries": [
                        {
                            "id": "c717464d-127e-4970-a3d8-31761dd83deb",
                            "key": "key1",
                            "value": {"type": "CONSTANT_VALUE", "value": {"type": "STRING", "value": "constant1"}},
                        },
                        {
                            "id": "ca19400f-9cce-4b4f-860f-63c98f43ad88",
                            "key": "key2",
                            "value": {
                                "type": "NODE_OUTPUT",
                                "node_id": "0f81f7b9-392b-4f0e-8584-0ff040fba961",
                                "node_output_id": "0b63e869-e978-4ec9-9f47-0cc1c7e22076",
                            },
                        },
                    ],
                },
            },
            {
                "id": "ca19400f-9cce-4b4f-860f-63c98f43ad88",
                "key": "key2",
                "value": {
                    "type": "DICTIONARY_REFERENCE",
                    "entries": [
                        {
                            "id": "c717464d-127e-4970-a3d8-31761dd83deb",
                            "key": "key1",
                            "value": {"type": "CONSTANT_VALUE", "value": {"type": "STRING", "value": "constant2"}},
                        },
                        {
                            "id": "ca19400f-9cce-4b4f-860f-63c98f43ad88",
                            "key": "key2",
                            "value": {
                                "type": "NODE_OUTPUT",
                                "node_id": "0f81f7b9-392b-4f0e-8584-0ff040fba961",
                                "node_output_id": "0b63e869-e978-4ec9-9f47-0cc1c7e22076",
                            },
                        },
                    ],
                },
            },
        ],
    }


def test_serialize_workflow__empty_rules_indexerror():
    """Test that workflow serialization handles dictionary key access correctly."""

    # GIVEN a node with dictionary output
    class StartNode(BaseNode):
        class Outputs(BaseNode.Outputs):
            data: dict = {"key": "value"}

    # AND a workflow that references dictionary key access in its outputs
    class MyWorkflow(BaseWorkflow):
        graph = StartNode

        class Outputs(BaseWorkflow.Outputs):
            # This dictionary key access should be handled gracefully
            problematic_output = StartNode.Outputs.data["bar"]

    # WHEN we serialize the workflow
    workflow_display = get_workflow_display(workflow_class=MyWorkflow)
    result: dict = workflow_display.serialize()

    assert result is not None
    assert "output_variables" in result
    assert "workflow_raw_data" in result

    # AND the workflow output should contain the dictionary key access
    output_variables = result["output_variables"]
    assert len(output_variables) == 1
    assert output_variables[0]["key"] == "problematic_output"


def test_serialize_workflow__input_variables():
    # GIVEN a workflow with inputs
    class Inputs(BaseInputs):
        empty_string: str = ""
        input_1: str
        input_2: Optional[str]
        input_3: int = 1
        input_4: Optional[int] = 2

    class MyWorkflow(BaseWorkflow[Inputs, BaseState]):
        pass

    # WHEN we serialize it
    workflow_display = get_workflow_display(workflow_class=MyWorkflow)
    data = workflow_display.serialize()

    # THEN the inputs should be serialized correctly
    assert "input_variables" in data
    input_variables = data["input_variables"]
    assert isinstance(input_variables, list)
    assert len(input_variables) == 5

    empty_string = next(var for var in input_variables if isinstance(var, dict) and var["key"] == "empty_string")
    assert empty_string == {
        "id": "09c3e825-8932-4d37-990a-b8a7c2a3bdec",
        "key": "empty_string",
        "type": "STRING",
        "default": {"type": "STRING", "value": ""},
        "required": False,
        "extensions": {"color": None},
        "schema": {"type": "string"},
    }

    input_1 = next(var for var in input_variables if isinstance(var, dict) and var["key"] == "input_1")
    assert input_1 == {
        "id": "13bd7980-3fbd-486c-9ebd-a29d84f7bda0",
        "key": "input_1",
        "type": "STRING",
        "default": None,
        "required": True,
        "extensions": {"color": None},
        "schema": {"type": "string"},
    }

    input_2 = next(var for var in input_variables if isinstance(var, dict) and var["key"] == "input_2")
    assert input_2 == {
        "id": "13847952-beab-408d-945e-cfa079e6e124",
        "key": "input_2",
        "type": "STRING",
        "default": None,
        "required": False,
        "extensions": {"color": None},
        "schema": {"anyOf": [{"type": "string"}, {"type": "null"}]},
    }

    input_3 = next(var for var in input_variables if isinstance(var, dict) and var["key"] == "input_3")
    assert input_3 == {
        "id": "2e38e1a4-09ff-4bb8-a12e-9bf54d4f3a5e",
        "key": "input_3",
        "type": "NUMBER",
        "default": {"type": "NUMBER", "value": 1.0},
        "required": False,
        "extensions": {"color": None},
        "schema": {"type": "integer"},
    }

    input_4 = next(var for var in input_variables if isinstance(var, dict) and var["key"] == "input_4")
    assert input_4 == {
        "id": "d945b6ae-2490-4bfb-9b1c-b1e484dfd4f6",
        "key": "input_4",
        "type": "NUMBER",
        "default": {"type": "NUMBER", "value": 2.0},
        "required": False,
        "extensions": {"color": None},
        "schema": {"anyOf": [{"type": "integer"}, {"type": "null"}]},
    }


def test_serialize_workflow__state_variables():
    # GIVEN a workflow with state variables
    class State(BaseState):
        empty_string: str = ""
        state_1: str = "hello"
        state_2: Optional[str] = None
        state_3: int = 1
        state_4: Optional[int] = 2

    class MyWorkflow(BaseWorkflow[BaseInputs, State]):
        pass

    # WHEN we serialize it
    workflow_display = get_workflow_display(workflow_class=MyWorkflow)
    data = workflow_display.serialize()

    # THEN the state variables should be serialized correctly
    assert "state_variables" in data
    state_variables = data["state_variables"]
    assert isinstance(state_variables, list)
    assert len(state_variables) == 5

    empty_string = next(var for var in state_variables if isinstance(var, dict) and var["key"] == "empty_string")
    assert empty_string == {
        "id": "c69e2507-f610-4a6f-84cc-a5bc2aa48551",
        "key": "empty_string",
        "type": "STRING",
        "default": {"type": "STRING", "value": ""},
        "required": False,
        "extensions": {"color": None},
    }

    state_1 = next(var for var in state_variables if isinstance(var, dict) and var["key"] == "state_1")
    assert state_1 == {
        "id": "151113d2-9bbf-428d-a1c1-0a9cf4fdedf3",
        "key": "state_1",
        "type": "STRING",
        "default": {"type": "STRING", "value": "hello"},
        "required": False,
        "extensions": {"color": None},
    }

    state_2 = next(var for var in state_variables if isinstance(var, dict) and var["key"] == "state_2")
    assert state_2 == {
        "id": "9a8d7a55-8bd2-497d-820c-dee665144a48",
        "key": "state_2",
        "type": "STRING",
        "default": None,
        "required": False,
        "extensions": {"color": None},
    }

    state_3 = next(var for var in state_variables if isinstance(var, dict) and var["key"] == "state_3")
    assert state_3 == {
        "id": "ffde4327-12c4-4c55-82d6-3ab88f0b1037",
        "key": "state_3",
        "type": "NUMBER",
        "default": {"type": "NUMBER", "value": 1.0},
        "required": False,
        "extensions": {"color": None},
    }

    state_4 = next(var for var in state_variables if isinstance(var, dict) and var["key"] == "state_4")
    assert state_4 == {
        "id": "2467c1e6-b6aa-42d7-b079-84c8a650fbca",
        "key": "state_4",
        "type": "NUMBER",
        "default": {"type": "NUMBER", "value": 2.0},
        "required": False,
        "extensions": {"color": None},
    }


def test_serialize_workflow__with_complete_node_failure_prunes_edges():
    """Test that edges are pruned when a node completely fails to serialize (serialized_node is null)."""

    # GIVEN a node that completely fails to serialize
    class FailingNode(BaseNode):
        class Outputs(BaseNode.Outputs):
            result: str

    class FailingNodeDisplay(BaseNodeDisplay[FailingNode]):
        def serialize(
            self, display_context: WorkflowDisplayContext, error_output_id: Optional[UUID] = None, **kwargs: Any
        ) -> JsonObject:
            raise NotImplementedError("Complete node serialization failure")

    # AND a workflow with the failing node connected to another node
    class WorkingNode(BaseNode):
        class Outputs(BaseNode.Outputs):
            value: str

    class Workflow(BaseWorkflow):
        graph = FailingNode >> WorkingNode

    # WHEN we serialize the workflow with dry_run=True
    workflow_display = get_workflow_display(workflow_class=Workflow, dry_run=True)

    # AND we register the failing display class
    workflow_display.display_context.node_displays[FailingNode] = FailingNodeDisplay()

    data: dict = workflow_display.serialize()

    # THEN the workflow should serialize but with no edges (pruned due to invalid node)
    assert data["workflow_raw_data"]["edges"] == []

    # AND only the working node and entrypoint should be in the serialized nodes
    assert len(data["workflow_raw_data"]["nodes"]) == 2
    node_types = [node["type"] for node in data["workflow_raw_data"]["nodes"]]
    assert "ENTRYPOINT" in node_types
    assert "GENERIC" in node_types  # This is the WorkingNode that should still be serialized


def test_serialize_workflow__node_with_invalid_input_reference():
    """Test that serialization captures errors when nodes reference a non-existent input attribute."""

    # GIVEN a workflow with defined inputs
    class Inputs(BaseInputs):
        valid_input: str

    # AND a templating node that references a non-existent input
    class MyTemplatingNode(TemplatingNode):
        class Outputs(TemplatingNode.Outputs):
            pass

        template = "valid: {{ valid_input }}, invalid: {{ invalid_ref }}"
        inputs = {
            "valid_input": Inputs.valid_input,
            "invalid_ref": Inputs.invalid_ref,
        }

    # AND a base node that also references the non-existent input
    class MyBaseNode(BaseNode):
        invalid_ref = Inputs.invalid_ref

        class Outputs(BaseNode.Outputs):
            result: str

        def run(self) -> BaseNode.Outputs:
            return self.Outputs(result="done")

    class MyBaseNodeDisplay(BaseNodeDisplay[MyBaseNode]):
        __serializable_inputs__ = {MyBaseNode.invalid_ref}

    # WHEN we create a workflow with both nodes and serialize with dry_run=True
    class MyWorkflow(BaseWorkflow[Inputs, BaseState]):
        graph = MyTemplatingNode >> MyBaseNode

    workflow_display = get_workflow_display(workflow_class=MyWorkflow, dry_run=True)
    serialized = workflow_display.serialize()

    # THEN the serialization should succeed without raising an exception
    assert serialized is not None
    assert "workflow_raw_data" in serialized

    errors = list(workflow_display.display_context.errors)
    assert len(errors) > 0

    # AND the error messages should reference the missing attribute
    error_messages = [str(e) for e in errors]
    assert any("invalid_ref" in msg for msg in error_messages)

    invalid_nodes = list(workflow_display.display_context.invalid_nodes)
    assert len(invalid_nodes) >= 2
