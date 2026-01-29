import pytest
from datetime import datetime
from uuid import UUID, uuid4
from typing import Type

from vellum import (
    ReleaseEnvironment,
    WorkflowDeploymentRelease,
    WorkflowDeploymentReleaseWorkflowDeployment,
    WorkflowDeploymentReleaseWorkflowVersion,
)
from vellum.workflows import BaseWorkflow
from vellum.workflows.nodes import MapNode
from vellum.workflows.nodes.displayable.subworkflow_deployment_node.node import SubworkflowDeploymentNode
from vellum.workflows.state.base import BaseState
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
    # Create a mock deployment release response
    deployment_release = WorkflowDeploymentRelease(
        id=str(uuid4()),
        created=datetime.now(),
        environment=ReleaseEnvironment(id=str(uuid4()), name="DEVELOPMENT", label="Development"),
        workflow_version=WorkflowDeploymentReleaseWorkflowVersion(
            id=str(uuid4()),
            input_variables=[],
            output_variables=[],
        ),
        deployment=WorkflowDeploymentReleaseWorkflowDeployment(
            id="test-id",
            name="test-deployment",
        ),
        release_tags=[],
        reviews=[],
    )

    # Patch the retrieve_workflow_deployment_release method
    patch_path = (
        "vellum.client.resources.workflow_deployments.client."
        "WorkflowDeploymentsClient.retrieve_workflow_deployment_release"
    )
    mocker.patch(patch_path, return_value=deployment_release)

    return deployment_release


@pytest.mark.parametrize(
    ["GetDisplayClass", "expected_input_id"],
    [
        (_no_display_class, "b35e4da6-7810-4d93-ab84-3ad1cbd71251"),
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


def test_serialize_node__subworkflow_inputs_with_accessor_expression(mock_fetch_deployment):
    """
    Tests that accessor expressions in subworkflow_inputs are serialized as a DICTIONARY_REFERENCE attribute.
    """

    # GIVEN a deployment subworkflow node with an accessor expression input
    class MySubworkflowDeploymentNode(SubworkflowDeploymentNode):
        deployment = "DEPLOYMENT"
        subworkflow_inputs = {"user_name": MapNode.SubworkflowInputs.item["name"]}

    # AND a workflow with the subworkflow node parameterized with MapNode.SubworkflowInputs
    class Workflow(BaseWorkflow[MapNode.SubworkflowInputs, BaseState]):
        graph = MySubworkflowDeploymentNode

    # WHEN the workflow is serialized
    workflow_display = get_workflow_display(workflow_class=Workflow)
    serialized_workflow: dict = workflow_display.serialize()

    # THEN the subworkflow node should have the accessor expression in attributes
    subworkflow_node = next(
        node
        for node in serialized_workflow["workflow_raw_data"]["nodes"]
        if node["id"] == str(MySubworkflowDeploymentNode.__id__)
    )

    # AND the subworkflow_inputs should be serialized as a DICTIONARY_REFERENCE attribute
    assert "attributes" in subworkflow_node
    subworkflow_inputs_attr = next(
        attr for attr in subworkflow_node["attributes"] if attr["name"] == "subworkflow_inputs"
    )

    # AND the attribute value should be a DICTIONARY_REFERENCE with the accessor expression
    attr_value = subworkflow_inputs_attr["value"]
    assert attr_value["type"] == "DICTIONARY_REFERENCE"
    assert len(attr_value["entries"]) == 1

    entry = attr_value["entries"][0]
    assert entry["key"] == "user_name"

    entry_value = entry["value"]
    assert entry_value["type"] == "BINARY_EXPRESSION"
    assert entry_value["operator"] == "accessField"
    assert entry_value["lhs"]["type"] == "WORKFLOW_INPUT"
    assert entry_value["rhs"]["type"] == "CONSTANT_VALUE"
    assert entry_value["rhs"]["value"]["value"] == "name"
