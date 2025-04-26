import pytest
from datetime import datetime
from uuid import UUID, uuid4
from typing import Type

from vellum.workflows import BaseWorkflow
from vellum.workflows.nodes.displayable.subworkflow_deployment_node.node import SubworkflowDeploymentNode
from vellum_ee.workflows.display.nodes.vellum.subworkflow_deployment_node import BaseSubworkflowDeploymentNodeDisplay
from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display


def _no_display_class(Node: Type[SubworkflowDeploymentNode]):  # type: ignore
    return None


def _display_class_with_node_input_ids_by_name(Node: Type[SubworkflowDeploymentNode]):
    class SubworkflowNodeDisplay(BaseSubworkflowDeploymentNodeDisplay[Node]):  # type: ignore[valid-type]
        node_input_ids_by_name = {"foo": UUID("aff4f838-577e-44b9-ac5c-6d8213abbb9c")}

    return SubworkflowNodeDisplay


def _display_class_with_node_input_ids_by_name_with_inputs_prefix(Node: Type[SubworkflowDeploymentNode]):
    class SubworkflowNodeDisplay(BaseSubworkflowDeploymentNodeDisplay[Node]):  # type: ignore[valid-type]
        node_input_ids_by_name = {"subworkflow_inputs.foo": UUID("aff4f838-577e-44b9-ac5c-6d8213abbb9c")}

    return SubworkflowNodeDisplay


@pytest.fixture
def mock_fetch_deployment(mocker):
    # Create a mock deployment response
    mock_deployment = mocker.Mock(
        id="test-id",
        name="test-deployment",
        label="Test Deployment",
        status="ACTIVE",
        environment="DEVELOPMENT",
        created=datetime.now(),
        last_deployed_on=datetime.now(),
        last_deployed_history_item_id=str(uuid4()),
        input_variables=[],
        output_variables=[],
        description="Test deployment description",
    )

    # Patch the create_vellum_client function to return our mock client
    mocker.patch(
        "vellum.client.resources.workflow_deployments.client.WorkflowDeploymentsClient.retrieve",
        return_value=mock_deployment,
    )

    return mock_deployment


@pytest.mark.parametrize(
    ["GetDisplayClass", "expected_input_id"],
    [
        (_no_display_class, "394132c2-1817-455e-9f3f-b7073eb63a2b"),
        (_display_class_with_node_input_ids_by_name, "aff4f838-577e-44b9-ac5c-6d8213abbb9c"),
        (_display_class_with_node_input_ids_by_name_with_inputs_prefix, "aff4f838-577e-44b9-ac5c-6d8213abbb9c"),
    ],
    ids=[
        "no_display_class",
        "display_class_with_node_input_ids_by_name",
        "display_class_with_node_input_ids_by_name_with_inputs_prefix",
    ],
)
def test_serialize_node__subworkflow_inputs(GetDisplayClass, expected_input_id, mock_fetch_deployment):
    # GIVEN a deployment subworkflow node with inputs
    class MySubworkflowDeploymentNode(SubworkflowDeploymentNode):
        deployment = "DEPLOYMENT"
        subworkflow_inputs = {"foo": "bar"}

    # AND a workflow with the subworkflow node
    class Workflow(BaseWorkflow):
        graph = MySubworkflowDeploymentNode

    # AND a display class
    GetDisplayClass(MySubworkflowDeploymentNode)

    # WHEN the workflow is serialized
    workflow_display = get_workflow_display(workflow_class=Workflow)
    serialized_workflow: dict = workflow_display.serialize()

    # THEN the node should properly serialize the inputs
    my_subworkflow_node = next(
        node
        for node in serialized_workflow["workflow_raw_data"]["nodes"]
        if node["id"] == str(MySubworkflowDeploymentNode.__id__)
    )

    assert my_subworkflow_node["inputs"] == [
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
