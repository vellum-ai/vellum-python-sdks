from uuid import UUID
from typing import Any, Dict, List, cast

from vellum.workflows.constants import VellumIntegrationProviderType
from vellum.workflows.graph import Graph
from vellum.workflows.inputs import BaseInputs
from vellum.workflows.nodes import BaseNode, InlineSubworkflowNode
from vellum.workflows.outputs.base import BaseOutputs
from vellum.workflows.ports.port import Port
from vellum.workflows.references.lazy import LazyReference
from vellum.workflows.state import BaseState
from vellum.workflows.triggers.integration import IntegrationTrigger
from vellum.workflows.workflows.base import BaseWorkflow
from vellum_ee.workflows.display.base import EdgeDisplay, WorkflowInputsDisplay
from vellum_ee.workflows.display.editor.types import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseNodeDisplay
from vellum_ee.workflows.display.workflows.base_workflow_display import BaseWorkflowDisplay
from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display


def test_base_workflow_display__serialize_empty_workflow():
    # GIVEN an empty workflow
    class ExampleWorkflow(BaseWorkflow):
        pass

    display = get_workflow_display(workflow_class=ExampleWorkflow)

    # WHEN serializing the workflow
    exec_config = display.serialize()

    # THEN it should return the expected config
    # Note: autolayout is not applied since Display.layout is not set to "auto"
    assert exec_config == {
        "input_variables": [],
        "state_variables": [],
        "output_variables": [],
        "workflow_raw_data": {
            "definition": {
                "module": ["vellum_ee", "workflows", "display", "tests", "test_base_workflow_display"],
                "name": "ExampleWorkflow",
            },
            "display_data": {"viewport": {"x": 0.0, "y": 0.0, "zoom": 1.0}},
            "edges": [],
            "nodes": [
                {
                    "data": {"label": "Entrypoint Node", "source_handle_id": "0af025a4-3b25-457d-a7ae-e3a7ba15c86c"},
                    "base": None,
                    "definition": None,
                    "display_data": {"position": {"x": 0.0, "y": 0.0}},
                    "id": "3c41cdd9-999a-48b8-9088-f6dfa1369bfd",
                    "inputs": [],
                    "type": "ENTRYPOINT",
                }
            ],
            "output_values": [],
        },
    }


def test_vellum_workflow_display__serialize_input_variables_with_capitalized_variable_override():
    # GIVEN a workflow with input variables
    class Inputs(BaseInputs):
        foo: str

    class StartNode(BaseNode):
        class Outputs(BaseNode.Outputs):
            output = Inputs.foo

    class ExampleWorkflow(BaseWorkflow[Inputs, BaseState]):
        graph = StartNode

    class ExampleWorkflowDisplay(BaseWorkflowDisplay[ExampleWorkflow]):
        inputs_display = {
            Inputs.foo: WorkflowInputsDisplay(id=UUID("97b63d71-5413-417f-9cf5-49e1b4fd56e4"), name="Foo")
        }

    display = get_workflow_display(
        base_display_class=ExampleWorkflowDisplay,
        workflow_class=ExampleWorkflow,
    )

    # WHEN serializing the workflow
    exec_config = display.serialize()

    # THEN the input variables are what we expect
    input_variables = exec_config["input_variables"]

    assert input_variables == [
        {
            "id": "97b63d71-5413-417f-9cf5-49e1b4fd56e4",
            "key": "Foo",
            "type": "STRING",
            "default": None,
            "required": True,
            "extensions": {"color": None},
            "schema": {"type": "string"},
        }
    ]


def test_vellum_workflow_display_serialize_valid_handle_ids_for_base_nodes():
    # GIVEN a workflow between two base nodes
    class StartNode(BaseNode):
        pass

    class EndNode(BaseNode):
        class Outputs(BaseNode.Outputs):
            hello = "world"

    class Workflow(BaseWorkflow):
        graph = StartNode >> EndNode

        class Outputs(BaseWorkflow.Outputs):
            final_value = EndNode.Outputs.hello

    # AND a display class for this workflow
    workflow_display = get_workflow_display(workflow_class=Workflow)

    # WHEN we serialize the workflow
    exec_config = workflow_display.serialize()

    # THEN the serialized workflow handle ids are valid
    raw_data = exec_config.get("workflow_raw_data")
    assert isinstance(raw_data, dict)
    nodes = raw_data.get("nodes")
    edges = raw_data.get("edges")

    assert isinstance(nodes, list)
    assert isinstance(edges, list)

    edge_source_handle_ids = {edge.get("source_handle_id") for edge in edges if isinstance(edge, dict)}
    edge_target_handle_ids = {edge.get("target_handle_id") for edge in edges if isinstance(edge, dict)}

    start_node = next(
        node for node in nodes if isinstance(node, dict) and node["type"] == "GENERIC" and node["label"] == "Start Node"
    )
    end_node = next(
        node for node in nodes if isinstance(node, dict) and node["type"] == "GENERIC" and node["label"] == "End Node"
    )

    assert isinstance(start_node["ports"], list)
    assert isinstance(start_node["ports"][0], dict)
    assert start_node["ports"][0]["id"] in edge_source_handle_ids

    assert isinstance(end_node["trigger"], dict)
    assert end_node["trigger"]["id"] in edge_target_handle_ids


def test_vellum_workflow_display__serialize_with_unused_nodes_and_edges():
    # GIVEN a workflow with active and unused nodes
    class NodeA(BaseNode):
        class Outputs(BaseNode.Outputs):
            result: str

    class NodeB(BaseNode):
        pass

    class NodeC(BaseNode):
        pass

    # AND A workflow that uses them correctly
    class Workflow(BaseWorkflow):
        graph = NodeA
        unused_graphs = {NodeB >> NodeC}

        class Outputs(BaseWorkflow.Outputs):
            final = NodeA.Outputs.result

    # WHEN we serialize it
    workflow_display = get_workflow_display(workflow_class=Workflow)

    # WHEN we serialize the workflow
    exec_config = workflow_display.serialize()

    # THEN the serialized workflow contains the expected nodes and edges
    raw_data = exec_config["workflow_raw_data"]
    assert isinstance(raw_data, dict)

    nodes = raw_data["nodes"]
    edges = raw_data["edges"]

    assert isinstance(nodes, list)
    assert isinstance(edges, list)

    # Find nodes by their definition name
    node_ids: Dict[str, str] = {}

    for node in nodes:
        assert isinstance(node, dict)
        definition = node.get("definition")
        if definition is None:
            continue

        assert isinstance(definition, dict)
        name = definition.get("name")
        if not isinstance(name, str):
            continue

        if name in ["NodeA", "NodeB", "NodeC"]:
            node_id = node.get("id")
            if isinstance(node_id, str):
                node_ids[name] = node_id

    # Verify all nodes are present
    assert "NodeA" in node_ids, "Active node NodeA not found in serialized output"
    assert "NodeB" in node_ids, "Unused node NodeB not found in serialized output"
    assert "NodeC" in node_ids, "Unused node NodeC not found in serialized output"

    # Verify the edge between NodeB and NodeC is present
    edge_found = False
    for edge in edges:
        assert isinstance(edge, dict)
        source_id = edge.get("source_node_id")
        target_id = edge.get("target_node_id")

        if (
            isinstance(source_id, str)
            and isinstance(target_id, str)
            and source_id == node_ids["NodeB"]
            and target_id == node_ids["NodeC"]
        ):
            edge_found = True
            break

    assert edge_found, "Edge between unused nodes NodeB and NodeC not found in serialized output"


def test_vellum_workflow_display__serialize_with_parse_json_expression():
    # GIVEN a workflow that uses the parse_json function
    from vellum.workflows.references.constant import ConstantValueReference

    class JsonNode(BaseNode):

        class Outputs(BaseNode.Outputs):
            json_result = ConstantValueReference('{"key": "value"}').parse_json()

    class Workflow(BaseWorkflow):
        graph = JsonNode

        class Outputs(BaseWorkflow.Outputs):
            final = JsonNode.Outputs.json_result

    # AND a display class for this workflow
    workflow_display = get_workflow_display(workflow_class=Workflow)

    # WHEN we serialize the workflow
    exec_config = workflow_display.serialize()

    # THEN the serialized workflow contains the parse_json expression
    raw_data = exec_config["workflow_raw_data"]
    assert isinstance(raw_data, dict)

    nodes = raw_data["nodes"]
    assert isinstance(nodes, list)

    json_node = None
    for node in nodes:
        assert isinstance(node, dict)
        definition = node.get("definition")
        if node.get("type") == "GENERIC" and isinstance(definition, dict) and definition.get("name") == "JsonNode":
            json_node = node
            break

    assert json_node is not None

    outputs = json_node.get("outputs", [])
    assert isinstance(outputs, list)

    json_result = None
    for output in outputs:
        assert isinstance(output, dict)
        if output.get("name") == "json_result":
            json_result = output
            break

    assert json_result == {
        "id": "e73fd6b1-1109-4a97-8510-c9ba8e6f5dbe",
        "name": "json_result",
        "type": "JSON",
        "schema": {},
        "value": {
            "type": "UNARY_EXPRESSION",
            "lhs": {
                "type": "CONSTANT_VALUE",
                "value": {
                    "type": "STRING",
                    "value": '{"key": "value"}',
                },
            },
            "operator": "parseJson",
        },
    }


def test_serialize__port_with_lazy_reference():
    # GIVEN a node with a lazy reference in a Port
    class MyNode(BaseNode):

        class Ports(BaseNode.Ports):
            foo = Port.on_if(LazyReference(lambda: MyNode.Outputs.bar))

        class Outputs(BaseNode.Outputs):
            bar: bool

    # AND a workflow that uses the node
    class Workflow(BaseWorkflow):
        graph = MyNode

    # WHEN we serialize the workflow
    workflow_display = get_workflow_display(workflow_class=Workflow)
    exec_config = workflow_display.serialize()

    # THEN the lazy reference should be serialized correctly
    raw_data = exec_config["workflow_raw_data"]
    assert isinstance(raw_data, dict)

    nodes = raw_data["nodes"]
    assert isinstance(nodes, list)

    my_node = nodes[1]
    assert isinstance(my_node, dict)
    ports = my_node.get("ports")
    assert isinstance(ports, list)
    assert ports == [
        {
            "id": "02e90580-e6b6-441c-a5d4-7cd083c11fc7",
            "name": "foo",
            "type": "IF",
            "expression": {
                "type": "NODE_OUTPUT",
                "node_id": str(MyNode.__id__),
                "node_output_id": str(MyNode.__output_ids__["bar"]),
            },
        }
    ]


def test_global_propagation_deep_nested_subworkflows():
    # GIVEN the root workflow, a middle workflow, and an inner workflow

    class RootInputs(BaseInputs):
        root_param: str

    class MiddleInputs(BaseInputs):
        middle_param: str

    class InnerInputs(BaseInputs):
        inner_param: str

    class InnerNode(BaseNode):
        class Outputs(BaseOutputs):
            done: bool

        def run(self) -> Outputs:
            return self.Outputs(done=True)

    class InnerWorkflow(BaseWorkflow[InnerInputs, BaseState]):
        graph = InnerNode

    class MiddleInlineSubworkflowNode(InlineSubworkflowNode):
        subworkflow_inputs = {"inner_param": "x"}
        subworkflow = InnerWorkflow

    class MiddleWorkflow(BaseWorkflow[MiddleInputs, BaseState]):
        graph = MiddleInlineSubworkflowNode

    class OuterInlineSubworkflowNode(InlineSubworkflowNode):
        subworkflow_inputs = {"middle_param": "y"}
        subworkflow = MiddleWorkflow

    class RootWorkflow(BaseWorkflow[RootInputs, BaseState]):
        graph = OuterInlineSubworkflowNode

    # WHEN we build the displays
    root_display = get_workflow_display(workflow_class=RootWorkflow)
    middle_display = get_workflow_display(
        workflow_class=MiddleWorkflow, parent_display_context=root_display.display_context
    )
    inner_display = get_workflow_display(
        workflow_class=InnerWorkflow, parent_display_context=middle_display.display_context
    )

    # THEN the deepest display must include root + middle + inner inputs in its GLOBAL view
    inner_global_names = {ref.name for ref in inner_display.display_context.global_workflow_input_displays.keys()}

    assert inner_global_names == {"middle_param", "inner_param", "root_param"}


def test_serialize_workflow_with_edge_display_data():
    """
    Tests that edges with z_index values serialize display_data correctly.
    """

    # GIVEN a workflow with connected nodes
    class StartNode(BaseNode):
        class Outputs(BaseNode.Outputs):
            result: str

    class EndNode(BaseNode):
        class Outputs(BaseNode.Outputs):
            final: str

    class TestWorkflow(BaseWorkflow):
        graph = StartNode >> EndNode

        class Outputs(BaseWorkflow.Outputs):
            final_result = EndNode.Outputs.final

    class TestWorkflowDisplay(BaseWorkflowDisplay[TestWorkflow]):
        edge_displays = {
            (StartNode.Ports.default, EndNode): EdgeDisplay(id=UUID("12345678-1234-5678-1234-567812345678"), z_index=5)
        }

    # WHEN we serialize the workflow with the custom display
    display = get_workflow_display(
        base_display_class=TestWorkflowDisplay,
        workflow_class=TestWorkflow,
    )
    serialized_workflow = display.serialize()

    # THEN the edge should include display_data with z_index
    workflow_raw_data = cast(Dict[str, Any], serialized_workflow["workflow_raw_data"])
    edges = cast(List[Dict[str, Any]], workflow_raw_data["edges"])

    edge_with_display_data = None
    for edge in edges:
        if edge["id"] == "12345678-1234-5678-1234-567812345678":
            edge_with_display_data = edge
            break

    assert edge_with_display_data is not None, "Edge with custom UUID not found"
    assert edge_with_display_data["display_data"] == {"z_index": 5}

    assert edge_with_display_data["type"] == "DEFAULT"
    assert "source_node_id" in edge_with_display_data
    assert "target_node_id" in edge_with_display_data


def test_serialize_workflow_with_node_display_data():
    """
    Tests that nodes with z_index values serialize display_data correctly.
    """

    # GIVEN a workflow with a node that has custom display data
    class TestNode(BaseNode):
        class Outputs(BaseNode.Outputs):
            result: str

    class TestWorkflow(BaseWorkflow):
        graph = TestNode

        class Outputs(BaseWorkflow.Outputs):
            final_result = TestNode.Outputs.result

    class TestNodeDisplay(BaseNodeDisplay[TestNode]):
        display_data = NodeDisplayData(position=NodeDisplayPosition(x=100, y=200), z_index=10, width=300, height=150)

    class TestWorkflowDisplay(BaseWorkflowDisplay[TestWorkflow]):
        pass

    # WHEN we serialize the workflow with the custom node display
    display = get_workflow_display(
        base_display_class=TestWorkflowDisplay,
        workflow_class=TestWorkflow,
    )
    serialized_workflow = display.serialize()

    # THEN the node should include display_data with z_index
    workflow_raw_data = cast(Dict[str, Any], serialized_workflow["workflow_raw_data"])
    nodes = cast(List[Dict[str, Any]], workflow_raw_data["nodes"])

    test_node = None
    for node in nodes:
        if node.get("type") == "GENERIC":
            definition = node.get("definition")
            if isinstance(definition, dict) and definition.get("name") == "TestNode":
                test_node = node
                break

    assert test_node is not None, "TestNode not found in serialized nodes"
    assert test_node["display_data"] == {"position": {"x": 100, "y": 200}, "z_index": 10, "width": 300, "height": 150}


def test_serialize_workflow_with_node_icon_and_color():
    """
    Tests that nodes with icon and color serialize correctly in workflow context.
    """

    # GIVEN a workflow with a node that has icon and color
    class TestNode(BaseNode):
        class Outputs(BaseNode.Outputs):
            result: str

    class TestWorkflow(BaseWorkflow):
        graph = TestNode

        class Outputs(BaseWorkflow.Outputs):
            final_result = TestNode.Outputs.result

    class TestNodeDisplay(BaseNodeDisplay[TestNode]):
        display_data = NodeDisplayData(position=NodeDisplayPosition(x=100, y=200), icon="vellum:icon:cog", color="navy")

    class TestWorkflowDisplay(BaseWorkflowDisplay[TestWorkflow]):
        pass

    # WHEN we serialize the workflow
    display = get_workflow_display(
        base_display_class=TestWorkflowDisplay,
        workflow_class=TestWorkflow,
    )
    serialized_workflow = display.serialize()

    # THEN the node should include icon and color in display_data
    workflow_raw_data = cast(Dict[str, Any], serialized_workflow["workflow_raw_data"])
    nodes = cast(List[Dict[str, Any]], workflow_raw_data["nodes"])

    test_node = None
    for node in nodes:
        if node.get("type") == "GENERIC":
            definition = node.get("definition")
            if isinstance(definition, dict) and definition.get("name") == "TestNode":
                test_node = node
                break

    assert test_node is not None, "TestNode not found in serialized nodes"
    assert test_node["display_data"]["icon"] == "vellum:icon:cog"
    assert test_node["display_data"]["color"] == "navy"


def test_base_workflow_display__graph_with_trigger_and_regular_node():
    """
    Tests that a workflow with both a trigger edge and a regular node edge serializes correctly.
    """

    # GIVEN a workflow with a trigger and regular nodes
    class SlackMessageTrigger(IntegrationTrigger):
        message: str

        class Config(IntegrationTrigger.Config):
            provider = VellumIntegrationProviderType.COMPOSIO
            integration_name = "SLACK"
            slug = "slack_message"

    class TopNode(BaseNode):
        class Outputs(BaseNode.Outputs):
            result: str

    class BottomNode(BaseNode):
        class Outputs(BaseNode.Outputs):
            final: str

    class TestWorkflow(BaseWorkflow):
        graph = {
            Graph.from_node(TopNode),
            SlackMessageTrigger >> BottomNode,
        }

    # WHEN we serialize the workflow
    workflow_display = get_workflow_display(workflow_class=TestWorkflow)
    exec_config = workflow_display.serialize()

    # THEN the serialized workflow should have the expected structure
    workflow_raw_data = exec_config["workflow_raw_data"]
    assert isinstance(workflow_raw_data, dict)

    nodes = workflow_raw_data["nodes"]
    edges = workflow_raw_data["edges"]
    triggers = exec_config["triggers"]

    assert isinstance(nodes, list)
    assert isinstance(edges, list)
    assert isinstance(triggers, list)

    assert len(triggers) == 1
    trigger = triggers[0]
    assert isinstance(trigger, dict)
    trigger_id = trigger["id"]

    entrypoint_nodes = [n for n in nodes if isinstance(n, dict) and n.get("type") == "ENTRYPOINT"]
    assert len(entrypoint_nodes) == 1
    entrypoint_node = entrypoint_nodes[0]
    assert isinstance(entrypoint_node, dict)
    entrypoint_node_id = entrypoint_node["id"]

    top_node = next(
        (
            node
            for node in nodes
            if isinstance(node, dict)
            and isinstance(node.get("definition"), dict)
            and cast(Dict[str, Any], node.get("definition")).get("name") == "TopNode"
        ),
        None,
    )
    bottom_node = next(
        (
            node
            for node in nodes
            if isinstance(node, dict)
            and isinstance(node.get("definition"), dict)
            and cast(Dict[str, Any], node.get("definition")).get("name") == "BottomNode"
        ),
        None,
    )

    assert top_node is not None, "TopNode not found in serialized nodes"
    assert bottom_node is not None, "BottomNode not found in serialized nodes"
    top_node_id = top_node["id"]
    bottom_node_id = bottom_node["id"]

    entrypoint_edges = [e for e in edges if isinstance(e, dict) and e.get("source_node_id") == entrypoint_node_id]
    assert len(entrypoint_edges) == 1, "Should have exactly one edge from the entrypoint node"

    entrypoint_edge = entrypoint_edges[0]
    assert isinstance(entrypoint_edge, dict)
    assert entrypoint_edge["target_node_id"] == top_node_id, "Entrypoint edge should connect to TopNode"

    trigger_edges = [e for e in edges if isinstance(e, dict) and e.get("source_node_id") == trigger_id]
    assert len(trigger_edges) == 1, "Should have exactly one edge from the trigger"

    trigger_edge = trigger_edges[0]
    assert isinstance(trigger_edge, dict)
    assert trigger_edge["target_node_id"] == bottom_node_id, "Trigger edge should connect to BottomNode"


def test_serialize_subworkflow_output_reference_without_display():
    """
    Tests that a workflow with a subworkflow node followed by a generic node
    that references the subworkflow output can be serialized correctly without a display directory.
    """

    # GIVEN a workflow module with a subworkflow node and a follow-on node
    module_path = "tests.workflows.subworkflow_output_reference_without_display"

    # WHEN we serialize the module
    result = BaseWorkflowDisplay.serialize_module(module_path)

    # THEN it should serialize successfully
    assert hasattr(result, "exec_config")
    assert isinstance(result.exec_config, dict)
    assert "workflow_raw_data" in result.exec_config

    # AND the workflow should have the expected nodes
    workflow_raw_data = result.exec_config["workflow_raw_data"]
    assert isinstance(workflow_raw_data, dict)
    nodes = workflow_raw_data.get("nodes")
    assert isinstance(nodes, list)

    subworkflow_node = next(
        (
            node
            for node in nodes
            if isinstance(node, dict)
            and isinstance(node.get("definition"), dict)
            and node.get("definition", {}).get("name") == "SubworkflowNodeExample"
        ),
        None,
    )
    followon_node = next(
        (
            node
            for node in nodes
            if isinstance(node, dict)
            and isinstance(node.get("definition"), dict)
            and node.get("definition", {}).get("name") == "FollowOnNode"
        ),
        None,
    )

    assert subworkflow_node is not None, "SubworkflowNodeExample not found in serialized nodes"
    assert followon_node is not None, "FollowOnNode not found in serialized nodes"

    # AND the subworkflow node should have output variables
    subworkflow_data = subworkflow_node.get("data", {})
    subworkflow_outputs = subworkflow_data.get("output_variables", [])
    assert len(subworkflow_outputs) > 0, "SubworkflowNodeExample should have output variables"

    result_output = next((out for out in subworkflow_outputs if out.get("key") == "result"), None)
    assert result_output is not None, "SubworkflowNodeExample should have 'result' output"
    expected_output_id = result_output["id"]

    # AND the follow-on node should have an attribute that references the subworkflow output
    followon_attributes = followon_node.get("attributes", [])
    assert len(followon_attributes) > 0, "FollowOnNode should have attributes"

    input_value_attr = next(
        (attr for attr in followon_attributes if isinstance(attr, dict) and attr.get("name") == "input_value"), None
    )

    assert input_value_attr is not None, "input_value attribute not found in FollowOnNode"

    # AND the attribute value should reference the subworkflow node's output
    value = input_value_attr.get("value")
    assert isinstance(value, dict)
    assert value.get("type") == "NODE_OUTPUT"
    assert value.get("node_id") == subworkflow_node.get("id")

    # AND the node_output_id should match the actual output ID from the subworkflow
    actual_output_id = value.get("node_output_id")
    assert actual_output_id == expected_output_id, (
        f"node_output_id mismatch: expected {expected_output_id}, got {actual_output_id}. "
        "The reference to the subworkflow output is broken."
    )


def test_serialize_workflow__auto_layout_applied_when_display_layout_is_auto():
    """
    Tests that autolayout is applied when Workflow.Display.layout is set to 'auto'.
    """

    # GIVEN a workflow with Display.layout = "auto" and nodes at position (0,0)
    class StartNode(BaseNode):
        class Outputs(BaseNode.Outputs):
            result: str

    class EndNode(BaseNode):
        class Outputs(BaseNode.Outputs):
            final: str

    class TestWorkflow(BaseWorkflow):
        graph = StartNode >> EndNode

        class Display(BaseWorkflow.Display):
            layout = "auto"

        class Outputs(BaseWorkflow.Outputs):
            final_result = EndNode.Outputs.final

    # WHEN we serialize the workflow
    display = get_workflow_display(workflow_class=TestWorkflow)
    serialized_workflow = display.serialize()

    # THEN the nodes should have non-zero positions due to autolayout
    workflow_raw_data = cast(Dict[str, Any], serialized_workflow["workflow_raw_data"])
    nodes = cast(List[Dict[str, Any]], workflow_raw_data["nodes"])

    generic_nodes = [n for n in nodes if n.get("type") == "GENERIC"]
    assert len(generic_nodes) == 2

    # AND at least one node should have a non-zero position from autolayout
    has_non_zero_position = any(
        n.get("display_data", {}).get("position", {}).get("x", 0) != 0
        or n.get("display_data", {}).get("position", {}).get("y", 0) != 0
        for n in generic_nodes
    )
    assert has_non_zero_position, "Autolayout should have repositioned at least one node"


def test_serialize_workflow__auto_layout_not_applied_when_display_layout_is_none():
    """
    Tests that autolayout is NOT applied when Workflow.Display.layout is None (default).
    """

    # GIVEN a workflow without Display.layout set (defaults to None)
    class StartNode(BaseNode):
        class Outputs(BaseNode.Outputs):
            result: str

    class EndNode(BaseNode):
        class Outputs(BaseNode.Outputs):
            final: str

    class TestWorkflow(BaseWorkflow):
        graph = StartNode >> EndNode

        class Outputs(BaseWorkflow.Outputs):
            final_result = EndNode.Outputs.final

    # WHEN we serialize the workflow
    display = get_workflow_display(workflow_class=TestWorkflow)
    serialized_workflow = display.serialize()

    # THEN the nodes should remain at position (0,0) since autolayout is not applied
    workflow_raw_data = cast(Dict[str, Any], serialized_workflow["workflow_raw_data"])
    nodes = cast(List[Dict[str, Any]], workflow_raw_data["nodes"])

    generic_nodes = [n for n in nodes if n.get("type") == "GENERIC"]
    assert len(generic_nodes) == 2

    # AND all nodes should have position (0,0) since autolayout was not applied
    for node in generic_nodes:
        position = node.get("display_data", {}).get("position", {})
        assert position.get("x", 0) == 0, f"Node should have x=0, got {position.get('x')}"
        assert position.get("y", 0) == 0, f"Node should have y=0, got {position.get('y')}"


def test_serialize_workflow__custom_display_class_without_layout_attribute():
    """
    Tests that serialization works when a workflow defines a custom Display class
    without the layout attribute (backward compatibility).
    """

    # GIVEN a workflow with a custom Display class that doesn't have layout attribute
    class StartNode(BaseNode):
        class Outputs(BaseNode.Outputs):
            result: str

    class TestWorkflow(BaseWorkflow):
        graph = StartNode

        class Display:
            # Custom Display class without layout attribute
            custom_attribute = "some_value"

        class Outputs(BaseWorkflow.Outputs):
            final_result = StartNode.Outputs.result

    # WHEN we serialize the workflow
    display = get_workflow_display(workflow_class=TestWorkflow)
    serialized_workflow = display.serialize()

    # THEN serialization should succeed without errors
    workflow_raw_data = cast(Dict[str, Any], serialized_workflow["workflow_raw_data"])
    nodes = cast(List[Dict[str, Any]], workflow_raw_data["nodes"])

    # AND autolayout should not be applied (since layout attribute is missing)
    generic_nodes = [n for n in nodes if n.get("type") == "GENERIC"]
    assert len(generic_nodes) == 1

    for node in generic_nodes:
        position = node.get("display_data", {}).get("position", {})
        assert position.get("x", 0) == 0, f"Node should have x=0, got {position.get('x')}"
        assert position.get("y", 0) == 0, f"Node should have y=0, got {position.get('y')}"


def test_serialize_module__chat_message_prompt_block_validation_error():
    """
    Tests that serialization returns a graceful error when a ChatMessagePromptBlock
    has a child block that raises a Pydantic ValidationError during serialization.
    """

    # GIVEN a workflow module with a ChatMessagePromptBlock containing an invalid child block
    module = "tests.workflows.test_chat_message_prompt_block_validation_error"

    # WHEN we serialize the module with dry_run=True (matching production behavior)
    result = BaseWorkflowDisplay.serialize_module(module, dry_run=True)

    # THEN the result should contain an error
    assert len(result.errors) > 0

    # AND the error message should indicate a validation error
    error_messages = [error.message for error in result.errors]
    assert any(
        "validation error" in msg.lower() for msg in error_messages
    ), f"Expected validation error in error messages, got: {error_messages}"


def test_parse_ml_models__skips_invalid_models_and_returns_valid_ones(caplog):
    """
    Tests that _parse_ml_models skips models with validation errors and returns valid ones.
    """

    # GIVEN a workflow class
    class ExampleWorkflow(BaseWorkflow):
        pass

    # AND a mix of valid and invalid ml_models data
    ml_models_raw = [
        {"name": "gpt-4", "hosted_by": "OPENAI"},
        {"name": "invalid-model", "hosted_by": "INVALID_PROVIDER"},
        {"name": "claude-3", "hosted_by": "ANTHROPIC"},
        {"name": "missing-hosted-by"},
        {"name": "gemini", "hosted_by": "GOOGLE"},
    ]

    # WHEN creating a display with the ml_models
    display = BaseWorkflowDisplay[ExampleWorkflow](ml_models=ml_models_raw)

    # THEN only the valid models should be parsed
    assert len(display._ml_models) == 3

    # AND the valid models should have the correct names
    model_names = [model.name for model in display._ml_models]
    assert "gpt-4" in model_names
    assert "claude-3" in model_names
    assert "gemini" in model_names

    # AND the invalid models should not be included
    assert "invalid-model" not in model_names
    assert "missing-hosted-by" not in model_names

    # AND warnings should be logged for the invalid models
    warning_messages = [record.message for record in caplog.records if record.levelname == "WARNING"]
    assert len(warning_messages) == 2
    assert any("invalid-model" in msg for msg in warning_messages)
    assert any("missing-hosted-by" in msg for msg in warning_messages)


def test_parse_ml_models__returns_empty_list_when_all_models_invalid(caplog):
    """
    Tests that _parse_ml_models returns an empty list when all models fail validation.
    """

    # GIVEN a workflow class
    class ExampleWorkflow(BaseWorkflow):
        pass

    # AND ml_models data where all models are invalid
    ml_models_raw = [
        {"name": "invalid-model", "hosted_by": "INVALID_PROVIDER"},
        {"name": "missing-hosted-by"},
        {"hosted_by": "OPENAI"},
    ]

    # WHEN creating a display with the ml_models
    display = BaseWorkflowDisplay[ExampleWorkflow](ml_models=ml_models_raw)

    # THEN no models should be parsed
    assert len(display._ml_models) == 0

    # AND warnings should be logged for all invalid models
    warning_messages = [record.message for record in caplog.records if record.levelname == "WARNING"]
    assert len(warning_messages) == 3


def test_parse_ml_models__returns_all_models_when_all_valid(caplog):
    """
    Tests that _parse_ml_models returns all models when all are valid.
    """

    # GIVEN a workflow class
    class ExampleWorkflow(BaseWorkflow):
        pass

    # AND ml_models data where all models are valid
    ml_models_raw = [
        {"name": "gpt-4", "hosted_by": "OPENAI"},
        {"name": "claude-3", "hosted_by": "ANTHROPIC"},
        {"name": "gemini", "hosted_by": "GOOGLE"},
    ]

    # WHEN creating a display with the ml_models
    display = BaseWorkflowDisplay[ExampleWorkflow](ml_models=ml_models_raw)

    # THEN all models should be parsed
    assert len(display._ml_models) == 3

    # AND the models should have the correct names and hosted_by values
    model_data = [(model.name, model.hosted_by.value) for model in display._ml_models]
    assert ("gpt-4", "OPENAI") in model_data
    assert ("claude-3", "ANTHROPIC") in model_data
    assert ("gemini", "GOOGLE") in model_data

    # AND no warnings should be logged
    warning_messages = [record.message for record in caplog.records if record.levelname == "WARNING"]
    assert len(warning_messages) == 0
