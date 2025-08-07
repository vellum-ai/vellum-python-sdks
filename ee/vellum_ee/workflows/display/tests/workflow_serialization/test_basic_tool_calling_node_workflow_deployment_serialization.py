from datetime import datetime

from deepdiff import DeepDiff

from vellum.client.types.release_environment import ReleaseEnvironment
from vellum.client.types.release_release_tag import ReleaseReleaseTag
from vellum.client.types.release_review_reviewer import ReleaseReviewReviewer
from vellum.client.types.slim_release_review import SlimReleaseReview
from vellum.client.types.workflow_deployment_release import WorkflowDeploymentRelease
from vellum.client.types.workflow_deployment_release_workflow_deployment import (
    WorkflowDeploymentReleaseWorkflowDeployment,
)
from vellum.client.types.workflow_deployment_release_workflow_version import WorkflowDeploymentReleaseWorkflowVersion
from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display

from tests.workflows.basic_tool_calling_node_workflow_deployment.workflow import (
    BasicToolCallingNodeWorkflowDeploymentWorkflow,
)


def test_serialize_workflow(vellum_client):
    vellum_client.workflow_deployments.retrieve_workflow_deployment_release.return_value = WorkflowDeploymentRelease(
        id="test-id",
        created=datetime.now(),
        environment=ReleaseEnvironment(
            id="test-id",
            name="test-name",
            label="test-label",
        ),
        created_by=None,
        workflow_version=WorkflowDeploymentReleaseWorkflowVersion(
            id="test-id",
            input_variables=[],
            output_variables=[],
        ),
        deployment=WorkflowDeploymentReleaseWorkflowDeployment(name="test-name"),
        description="test-description",  # main mock
        release_tags=[
            ReleaseReleaseTag(
                name="test-name",
                source="USER",
            )
        ],
        reviews=[
            SlimReleaseReview(
                id="test-id",
                created=datetime.now(),
                reviewer=ReleaseReviewReviewer(
                    id="test-id",
                    full_name="test-name",
                ),
                state="APPROVED",
            )
        ],
    )
    # GIVEN a Workflow that uses a generic node
    # WHEN we serialize it
    workflow_display = get_workflow_display(workflow_class=BasicToolCallingNodeWorkflowDeploymentWorkflow)

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
            {"id": "3626cfa6-76f8-465e-b156-c809e3a2cee9", "key": "text", "type": "STRING"},
            {"id": "cb82117a-d649-4c3e-9342-c552028fa2ad", "key": "chat_history", "type": "CHAT_HISTORY"},
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
                "value": [
                    {
                        "type": "WORKFLOW_DEPLOYMENT",
                        "name": "test-name",
                        "description": "test-description",
                        "deployment": "deployment_1",
                        "release_tag": "LATEST",
                    }
                ],
            },
        },
    }
