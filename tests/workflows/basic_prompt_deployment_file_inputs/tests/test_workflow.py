from uuid import uuid4
from typing import Any, Iterator, List

from vellum import (
    ExecutePromptEvent,
    FulfilledExecutePromptEvent,
    FunctionCall,
    FunctionCallVellumValue,
    InitiatedExecutePromptEvent,
    PromptOutput,
    StringVellumValue,
)
from vellum.client.types import VellumAudio, VellumDocument, VellumImage, VellumVideo
from vellum.client.types.audio_input_request import AudioInputRequest
from vellum.client.types.document_input_request import DocumentInputRequest
from vellum.client.types.image_input_request import ImageInputRequest
from vellum.client.types.vellum_audio_request import VellumAudioRequest
from vellum.client.types.vellum_document_request import VellumDocumentRequest
from vellum.client.types.vellum_image_request import VellumImageRequest
from vellum.client.types.vellum_video_request import VellumVideoRequest
from vellum.client.types.video_input_request import VideoInputRequest
from vellum.workflows.constants import LATEST_RELEASE_TAG
from vellum.workflows.events.types import VellumCodeResourceDefinition

from tests.workflows.basic_prompt_deployment_file_inputs.workflow import (
    BasicPromptDeploymentWorkflow,
    ExamplePromptDeploymentNode,
    Inputs,
)


def test_run_workflow__happy_path(vellum_client):
    """Confirm that we can successfully invoke a Workflow with a single Prompt Deployment Node"""

    # GIVEN a workflow that's set up to hit a Prompt Deployment
    workflow = BasicPromptDeploymentWorkflow()

    # AND we know what the Prompt Deployment will respond with
    expected_outputs: List[PromptOutput] = [
        StringVellumValue(value="I'm looking up the weather for you now."),
        FunctionCallVellumValue(value=FunctionCall(name="get_current_weather", arguments={"city": "San Francisco"})),
    ]

    def generate_prompt_events(*args: Any, **kwargs: Any) -> Iterator[ExecutePromptEvent]:
        execution_id = str(uuid4())
        events: List[ExecutePromptEvent] = [
            InitiatedExecutePromptEvent(execution_id=execution_id),
            FulfilledExecutePromptEvent(
                execution_id=execution_id,
                outputs=expected_outputs,
            ),
        ]
        yield from events

    vellum_client.execute_prompt_stream.side_effect = generate_prompt_events

    # WHEN we run the workflow
    terminal_event = workflow.run(
        inputs=Inputs(
            audio_variable=VellumAudio(src="https://example.com/audio-variable.mp3"),
            video_variable=VellumVideo(src="https://example.com/video-variable.mp4"),
            image_variable=VellumImage(src="https://example.com/image-variable.png"),
            document_variable=VellumDocument(src="Sample document content", metadata={"filename": "test.txt"}),
        )
    )

    # THEN the workflow should have completed successfully
    assert terminal_event.name == "workflow.execution.fulfilled"

    # AND the outputs should be as expected
    assert terminal_event.outputs.results == expected_outputs

    # AND we should have invoked the Prompt Deployment with the expected inputs
    call_kwargs = vellum_client.execute_prompt_stream.call_args.kwargs
    actual_inputs = call_kwargs["inputs"]

    # Verify we have the correct number of inputs
    assert actual_inputs == [
        AudioInputRequest(
            name="audio_variable",
            type="AUDIO",
            value=VellumAudioRequest(src="https://example.com/audio-variable.mp3", metadata=None),
        ),
        VideoInputRequest(
            name="video_variable",
            type="VIDEO",
            value=VellumVideoRequest(src="https://example.com/video-variable.mp4", metadata=None),
        ),
        ImageInputRequest(
            name="image_variable",
            type="IMAGE",
            value=VellumImageRequest(src="https://example.com/image-variable.png", metadata=None),
        ),
        DocumentInputRequest(
            name="document_variable",
            type="DOCUMENT",
            value=VellumDocumentRequest(src="Sample document content", metadata={"filename": "test.txt"}),
        ),
    ]

    # Verify other parameters
    assert call_kwargs["prompt_deployment_id"] is None
    assert call_kwargs["prompt_deployment_name"] == "example_prompt_deployment"
    assert call_kwargs["release_tag"] == LATEST_RELEASE_TAG
    assert call_kwargs["external_id"] is None
    assert call_kwargs["expand_meta"] is None
    assert call_kwargs["raw_overrides"] is None
    assert call_kwargs["expand_raw"] is None
    assert call_kwargs["metadata"] is None
    assert call_kwargs["request_options"] is not None

    # Verify execution context
    parent_context = call_kwargs["request_options"]["additional_body_parameters"]["execution_context"].get(
        "parent_context"
    )
    trace_id = call_kwargs["request_options"]["additional_body_parameters"]["execution_context"]["trace_id"]
    assert trace_id is not None
    assert parent_context["node_definition"] == VellumCodeResourceDefinition.encode(
        ExamplePromptDeploymentNode
    ).model_dump(mode="json")
