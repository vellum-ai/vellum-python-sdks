from deepdiff import DeepDiff

from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display

from tests.workflows.basic_tool_calling_node_deployment_workflow.workflow import (
    BasicToolCallingNodeDeploymentWorkflowWorkflow,
)


def test_serialize_workflow():
    # GIVEN a Workflow that uses a generic node
    # WHEN we serialize it
    workflow_display = get_workflow_display(workflow_class=BasicToolCallingNodeDeploymentWorkflowWorkflow)

    serialized_workflow: dict = workflow_display.serialize()
    # THEN we should get a serialized representation of the Workflow
    assert serialized_workflow.keys() == {
        "workflow_raw_data",
        "input_variables",
        "state_variables",
        "output_variables",
    }

    # AND its input variables should be what we expect
    input_variables = serialized_workflow["input_variables"]
    assert len(input_variables) == 1

    # AND its output variables should be what we expect
    output_variables = serialized_workflow["output_variables"]
    assert len(output_variables) == 2
    assert not DeepDiff(
        [
            {"id": "5c740646-7866-447f-b68d-833f3e198c30", "key": "text", "type": "STRING"},
            {"id": "7bd47b06-0481-48a7-a51e-6a998385ee9a", "key": "chat_history", "type": "CHAT_HISTORY"},
        ],
        output_variables,
        ignore_order=True,
    )

    # AND its raw data should be what we expect
    workflow_raw_data = serialized_workflow["workflow_raw_data"]
    tool_calling_node = workflow_raw_data["nodes"][1]
    function_attributes = next(attr for attr in tool_calling_node["attributes"] if attr["name"] == "functions")
    assert function_attributes == {
        "id": "73a94e3c-1935-4308-a68a-ecd5441804b7",
        "name": "functions",
        "value": {
            "type": "CONSTANT_VALUE",
            "value": {
                "type": "JSON",
                "value": [{"type": "WORKFLOW_DEPLOYMENT", "deployment": "deployment_1", "release_tag": "LATEST"}],
            },
        },
    }
