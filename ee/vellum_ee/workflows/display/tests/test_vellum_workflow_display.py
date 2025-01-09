from vellum.workflows.workflows.base import BaseWorkflow
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
