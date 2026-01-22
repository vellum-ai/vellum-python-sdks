import pytest

from deepdiff import DeepDiff

from vellum_ee.workflows.display.utils.exceptions import WorkflowValidationError
from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display

from tests.workflows.complex_final_output_node.missing_final_output_node import MissingFinalOutputNodeWorkflow
from tests.workflows.complex_final_output_node.missing_workflow_output import MissingWorkflowOutputWorkflow


def test_serialize_workflow__missing_final_output_node():
    # GIVEN a Workflow that is missing a Terminal Node
    workflow_display = get_workflow_display(workflow_class=MissingFinalOutputNodeWorkflow)

    # WHEN we serialize it
    serialized_workflow: dict = workflow_display.serialize()

    # THEN we should get a serialized representation its output variables to be what we expect
    output_variables = serialized_workflow["output_variables"]
    assert len(output_variables) == 2
    assert not DeepDiff(
        [
            {"id": "a360aef6-3bb4-4c56-b407-478042ef224d", "key": "alpha", "type": "STRING"},
            {"id": "5e6d3ea6-ef91-4937-8fff-f33e07446e6a", "key": "beta", "type": "STRING"},
        ],
        output_variables,
        ignore_order=True,
    )

    # AND each node should be serialized correctly
    workflow_raw_data = serialized_workflow["workflow_raw_data"]
    assert isinstance(workflow_raw_data, dict)

    # AND we should NOT create synthetic terminal nodes for each output variable
    final_output_nodes = [node for node in workflow_raw_data["nodes"] if node["type"] == "TERMINAL"]
    assert not DeepDiff(
        [
            {
                "id": "8683c087-4372-4357-bdd4-e13a50447d5e",
                "type": "TERMINAL",
                "data": {
                    "label": "First Final Output Node",
                    "name": "alpha",
                    "target_handle_id": "438edefd-131d-4d00-8645-d0a7ea07029e",
                    "output_id": "1d261e4b-4d77-4ace-9349-972129583519",
                    "output_type": "STRING",
                    "node_input_id": "ec1a9df2-a809-49fa-971b-8718df47e456",
                },
                "inputs": [
                    {
                        "id": "ec1a9df2-a809-49fa-971b-8718df47e456",
                        "key": "node_input",
                        "value": {
                            "rules": [
                                {
                                    "type": "INPUT_VARIABLE",
                                    "data": {"input_variable_id": "da086239-d743-4246-b666-5c91e22fb88c"},
                                }
                            ],
                            "combinator": "OR",
                        },
                    }
                ],
                "display_data": {"position": {"x": 0.0, "y": 0.0}},
                "base": {
                    "name": "FinalOutputNode",
                    "module": ["vellum", "workflows", "nodes", "displayable", "final_output_node", "node"],
                },
                "definition": {
                    "name": "FirstFinalOutputNode",
                    "module": ["tests", "workflows", "complex_final_output_node", "missing_final_output_node"],
                },
                "outputs": [
                    {
                        "id": "1d261e4b-4d77-4ace-9349-972129583519",
                        "name": "value",
                        "type": "STRING",
                        "value": {
                            "type": "WORKFLOW_INPUT",
                            "input_variable_id": "da086239-d743-4246-b666-5c91e22fb88c",
                        },
                        "schema": {"type": "string"},
                    }
                ],
                "trigger": {
                    "id": "438edefd-131d-4d00-8645-d0a7ea07029e",
                    "merge_behavior": "AWAIT_ANY",
                },
                "ports": [],
            },
        ],
        final_output_nodes,
    )


def test_serialize_workflow__missing_workflow_output():
    # GIVEN a Workflow that contains a terminal node that is unreferenced by the Workflow's Outputs
    workflow_display = get_workflow_display(workflow_class=MissingWorkflowOutputWorkflow)

    # WHEN we serialize it, it should throw a WorkflowValidationError
    with pytest.raises(WorkflowValidationError) as exc_info:
        workflow_display.serialize()

    # THEN the error message should indicate the terminal node is not referenced
    error_message = str(exc_info.value)
    assert "MissingWorkflowOutputWorkflow" in error_message
    assert "terminal nodes that are not referenced by workflow outputs" in error_message
