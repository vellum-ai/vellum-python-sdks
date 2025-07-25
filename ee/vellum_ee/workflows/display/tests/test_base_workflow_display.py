from uuid import UUID
from typing import Dict

from vellum.workflows.inputs import BaseInputs
from vellum.workflows.nodes import BaseNode
from vellum.workflows.ports.port import Port
from vellum.workflows.references.lazy import LazyReference
from vellum.workflows.state import BaseState
from vellum.workflows.workflows.base import BaseWorkflow
from vellum_ee.workflows.display.base import WorkflowInputsDisplay
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
                    "display_data": {"position": {"x": 0.0, "y": -50.0}},
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

    for node in nodes:
        assert isinstance(node, dict)

        if node["type"] in {"ENTRYPOINT", "TERMINAL"}:
            continue

        ports = node.get("ports")
        assert isinstance(ports, list)
        for port in ports:
            assert isinstance(port, dict)
            assert (
                port["id"] in edge_source_handle_ids
            ), f"Port {port['id']} from node {node['label']} not found in edge source handle ids"

        assert isinstance(node["trigger"], dict)
        assert (
            node["trigger"]["id"] in edge_target_handle_ids
        ), f"Trigger {node['trigger']['id']} from node {node['label']} not found in edge target handle ids"


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
        "id": "44c7d94c-a76a-4151-9b95-85a31764f18f",
        "name": "json_result",
        "type": "JSON",
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
            "id": "6c26bc2b-6469-47c1-b858-d63f0d311ea6",
            "name": "foo",
            "type": "IF",
            "expression": {
                "type": "NODE_OUTPUT",
                "node_id": str(MyNode.__id__),
                "node_output_id": str(MyNode.__output_ids__["bar"]),
            },
        }
    ]
