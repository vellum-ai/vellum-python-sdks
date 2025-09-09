import pytest
from datetime import datetime
from uuid import UUID, uuid4
from typing import Type

from vellum import (
    AudioInputRequest,
    DocumentInputRequest,
    ImageInputRequest,
    VellumAudio,
    VellumAudioRequest,
    VellumDocument,
    VellumDocumentRequest,
    VellumImage,
    VellumImageRequest,
    VellumVideo,
    VellumVideoRequest,
    VideoInputRequest,
)
from vellum.workflows import BaseWorkflow
from vellum.workflows.nodes import PromptDeploymentNode
from vellum_ee.workflows.display.nodes.vellum.prompt_deployment_node import BasePromptDeploymentNodeDisplay
from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display


def _no_display_class(Node: Type[PromptDeploymentNode]):  # type: ignore
    return None


def _display_class_with_node_input_ids_by_name(Node: Type[PromptDeploymentNode]):
    class PromptDeploymentNodeDisplay(BasePromptDeploymentNodeDisplay[Node]):  # type: ignore[valid-type]
        node_input_ids_by_name = {"foo": UUID("6037747a-1d35-4094-b363-4369fc92c5d4")}

    return PromptDeploymentNodeDisplay


def _display_class_with_node_input_ids_by_name_with_inputs_prefix(Node: Type[PromptDeploymentNode]):
    class PromptDeploymentNodeDisplay(BasePromptDeploymentNodeDisplay[Node]):  # type: ignore[valid-type]
        node_input_ids_by_name = {"prompt_inputs.foo": UUID("6037747a-1d35-4094-b363-4369fc92c5d4")}

    return PromptDeploymentNodeDisplay


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
    mocker.patch("vellum.client.resources.deployments.client.DeploymentsClient.retrieve", return_value=mock_deployment)
    return mock_deployment


@pytest.mark.parametrize(
    ["GetDisplayClass", "expected_input_id"],
    [
        (_no_display_class, "016187d6-2830-4256-a61d-e52f9bf6355e"),
        (_display_class_with_node_input_ids_by_name, "6037747a-1d35-4094-b363-4369fc92c5d4"),
        (_display_class_with_node_input_ids_by_name_with_inputs_prefix, "6037747a-1d35-4094-b363-4369fc92c5d4"),
    ],
    ids=[
        "no_display_class",
        "display_class_with_node_input_ids_by_name",
        "display_class_with_node_input_ids_by_name_with_inputs_prefix",
    ],
)
def test_serialize_node__prompt_inputs(GetDisplayClass, expected_input_id, mock_fetch_deployment):
    # GIVEN a prompt node with inputs
    class MyPromptDeploymentNode(PromptDeploymentNode):
        deployment = "DEPLOYMENT"
        prompt_inputs = {"foo": "bar"}
        ml_model_fallbacks = None

    # AND a workflow with the prompt node
    class Workflow(BaseWorkflow):
        graph = MyPromptDeploymentNode

    # AND a display class
    GetDisplayClass(MyPromptDeploymentNode)

    # WHEN the workflow is serialized
    workflow_display = get_workflow_display(workflow_class=Workflow)
    serialized_workflow: dict = workflow_display.serialize()

    # THEN the node should properly serialize the inputs
    my_prompt_node = next(
        node
        for node in serialized_workflow["workflow_raw_data"]["nodes"]
        if node["id"] == str(MyPromptDeploymentNode.__id__)
    )

    assert my_prompt_node["inputs"] == [
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


@pytest.mark.parametrize(
    [
        "raw_input",
        "expected_compiled_inputs",
    ],
    [
        # Cast VellumX -> VellumXRequest
        (
            VellumAudio(src="data:audio/wav;base64,mockaudio"),
            [AudioInputRequest(name="file_input", value=VellumAudioRequest(src="data:audio/wav;base64,mockaudio"))],
        ),
        (
            VellumImage(src="data:image/png;base64,mockimage"),
            [ImageInputRequest(name="file_input", value=VellumImageRequest(src="data:image/png;base64,mockimage"))],
        ),
        (
            VellumVideo(src="data:video/mp4;base64,mockvideo"),
            [VideoInputRequest(name="file_input", value=VellumVideoRequest(src="data:video/mp4;base64,mockvideo"))],
        ),
        (
            VellumDocument(src="mockdocument"),
            [DocumentInputRequest(name="file_input", value=VellumDocumentRequest(src="mockdocument"))],
        ),
        # No casting required
        (
            VellumAudioRequest(src="data:audio/wav;base64,mockaudio"),
            [AudioInputRequest(name="file_input", value=VellumAudioRequest(src="data:audio/wav;base64,mockaudio"))],
        ),
        (
            VellumImageRequest(src="data:image/png;base64,mockimage"),
            [ImageInputRequest(name="file_input", value=VellumImageRequest(src="data:image/png;base64,mockimage"))],
        ),
        (
            VellumVideoRequest(src="data:video/mp4;base64,mockvideo"),
            [VideoInputRequest(name="file_input", value=VellumVideoRequest(src="data:video/mp4;base64,mockvideo"))],
        ),
        (
            VellumDocumentRequest(src="mockdocument"),
            [DocumentInputRequest(name="file_input", value=VellumDocumentRequest(src="mockdocument"))],
        ),
    ],
)
def test_file_input_compilation(raw_input, expected_compiled_inputs):
    # GIVEN a prompt node with file input
    class MyPromptDeploymentNode(PromptDeploymentNode):
        deployment = "DEPLOYMENT"
        prompt_inputs = {"file_input": raw_input}
        ml_model_fallbacks = None

    # WHEN we compile the inputs
    compiled_inputs = MyPromptDeploymentNode()._compile_prompt_inputs()

    # THEN we should get the correct input type
    assert compiled_inputs == expected_compiled_inputs
