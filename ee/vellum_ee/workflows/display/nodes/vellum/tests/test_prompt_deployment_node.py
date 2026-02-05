import pytest
from datetime import datetime
from unittest.mock import MagicMock
from uuid import UUID, uuid4
from typing import Type

from vellum import (
    AudioInputRequest,
    DeploymentRead,
    DocumentInputRequest,
    ImageInputRequest,
    PromptDeploymentRelease,
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
from vellum.client.types.prompt_deployment_release_prompt_deployment import PromptDeploymentReleasePromptDeployment
from vellum.client.types.prompt_deployment_release_prompt_version import PromptDeploymentReleasePromptVersion
from vellum.client.types.release_environment import ReleaseEnvironment as ReleaseEnvironmentType
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
def mock_client():
    """Create a mock Vellum client with mocked deployment methods."""
    # Create a mock deployment response
    mock_deployment = DeploymentRead(
        id=str(uuid4()),
        created=datetime.now(),
        label="Test Deployment",
        name="test-deployment",
        last_deployed_on=datetime.now(),
        active_model_version_ids=[],
        input_variables=[],
        last_deployed_history_item_id=str(uuid4()),
    )

    # Create a mock prompt deployment release
    prompt_version = PromptDeploymentReleasePromptVersion.model_validate(
        {
            "id": str(uuid4()),
            "ml_model_to_workspace_id": str(uuid4()),
            "build_config": {
                "source": "SANDBOX",
                "sandbox_id": str(uuid4()),
                "sandbox_snapshot_id": str(uuid4()),
                "prompt_id": str(uuid4()),
            },
        }
    )

    deployment_release = PromptDeploymentRelease(
        id=str(uuid4()),
        created=datetime.now(),
        environment=ReleaseEnvironmentType(id=str(uuid4()), name="DEVELOPMENT", label="Development"),
        prompt_version=prompt_version,
        deployment=PromptDeploymentReleasePromptDeployment(
            id=mock_deployment.id,
            name="test-deployment",
        ),
        release_tags=[],
        reviews=[],
    )

    # Create a mock client
    mock_client = MagicMock()
    mock_client.deployments.retrieve.return_value = mock_deployment
    mock_client.deployments.retrieve_prompt_deployment_release.return_value = deployment_release

    return mock_client


@pytest.mark.parametrize(
    ["GetDisplayClass", "expected_input_id"],
    [
        (_no_display_class, "1eb8e95c-3659-4225-a1ee-3b23a2193888"),
        (_display_class_with_node_input_ids_by_name, "6037747a-1d35-4094-b363-4369fc92c5d4"),
        (_display_class_with_node_input_ids_by_name_with_inputs_prefix, "6037747a-1d35-4094-b363-4369fc92c5d4"),
    ],
    ids=[
        "no_display_class",
        "display_class_with_node_input_ids_by_name",
        "display_class_with_node_input_ids_by_name_with_inputs_prefix",
    ],
)
def test_serialize_node__prompt_inputs(GetDisplayClass, expected_input_id, mock_client):
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
    workflow_display = get_workflow_display(workflow_class=Workflow, client=mock_client)
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
