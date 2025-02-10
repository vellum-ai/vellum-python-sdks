from uuid import UUID

from vellum.workflows.inputs import BaseInputs
from vellum.workflows.nodes import BaseNode
from vellum.workflows.state import BaseState
from vellum.workflows.workflows.base import BaseWorkflow
from vellum_ee.workflows.display.vellum import WorkflowInputsVellumDisplayOverrides
from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display
from vellum_ee.workflows.display.workflows.vellum_workflow_display import VellumWorkflowDisplay


def test_vellum_workflow_display__serialize_empty_workflow():
    # GIVEN an empty workflow
    class ExampleWorkflow(BaseWorkflow):
        pass

    display = get_workflow_display(
        base_display_class=VellumWorkflowDisplay,
        workflow_class=ExampleWorkflow,
    )

    # WHEN serializing the workflow
    exec_config = display.serialize()

    # THEN it should return the expected config
    assert exec_config == {
        "input_variables": [],
        "state_variables": [],
        "output_variables": [],
        "workflow_raw_data": {
            "definition": {
                "module": ["vellum_ee", "workflows", "display", "tests", "test_vellum_workflow_display"],
                "name": "ExampleWorkflow",
            },
            "display_data": {"viewport": {"x": 0.0, "y": 0.0, "zoom": 1.0}},
            "edges": [],
            "nodes": [
                {
                    "data": {"label": "Entrypoint Node", "source_handle_id": "508b8b82-3517-4672-a155-18c9c7b9c545"},
                    "base": None,
                    "definition": None,
                    "display_data": {"position": {"x": 0.0, "y": 0.0}},
                    "id": "9eef0c18-f322-4d56-aa89-f088d3e53f6a",
                    "inputs": [],
                    "type": "ENTRYPOINT",
                }
            ],
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

    class ExampleWorkflowDisplay(VellumWorkflowDisplay[ExampleWorkflow]):
        inputs_display = {
            Inputs.foo: WorkflowInputsVellumDisplayOverrides(
                id=UUID("97b63d71-5413-417f-9cf5-49e1b4fd56e4"), name="Foo", required=True
            )
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
    workflow_display = get_workflow_display(
        base_display_class=VellumWorkflowDisplay,
        workflow_class=Workflow,
    )

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
