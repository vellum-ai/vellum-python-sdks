from unittest import mock
from uuid import uuid4
from typing import Any, Iterator, List

from vellum import (
    AdHocExecutePromptEvent,
    AdHocExpandMeta,
    AudioPromptBlock,
    ChatMessagePromptBlock,
    DocumentPromptBlock,
    FulfilledAdHocExecutePromptEvent,
    ImagePromptBlock,
    InitiatedAdHocExecutePromptEvent,
    JinjaPromptBlock,
    PromptOutput,
    PromptRequestAudioInput,
    PromptRequestDocumentInput,
    PromptRequestImageInput,
    PromptRequestVideoInput,
    PromptSettings,
    StringVellumValue,
    VariablePromptBlock,
    VellumAudio,
    VellumDocument,
    VellumImage,
    VellumVariable,
    VellumVideo,
    VideoPromptBlock,
)
from vellum.prompts.constants import DEFAULT_PROMPT_PARAMETERS

from tests.workflows.basic_inline_prompt_node_file_inputs.workflow import FileInputInlinePromptWorkflow, WorkflowInputs


def test_run_workflow__happy_path(vellum_adhoc_prompt_client, mock_uuid4_generator):
    """Confirm that we can successfully invoke a Workflow with a single Inline Prompt Node"""

    # GIVEN a workflow that's set up to hit a Prompt
    workflow = FileInputInlinePromptWorkflow()

    # AND we know what the Prompt will respond with
    expected_outputs: List[PromptOutput] = [
        StringVellumValue(value="I'm looking up the weather for you now."),
    ]

    def generate_prompt_events(*args: Any, **kwargs: Any) -> Iterator[AdHocExecutePromptEvent]:
        execution_id = str(uuid4())
        events: List[AdHocExecutePromptEvent] = [
            InitiatedAdHocExecutePromptEvent(execution_id=execution_id),
            FulfilledAdHocExecutePromptEvent(
                execution_id=execution_id,
                outputs=expected_outputs,
            ),
        ]
        yield from events

    vellum_adhoc_prompt_client.adhoc_execute_prompt_stream.side_effect = generate_prompt_events

    uuid4_generator = mock_uuid4_generator("vellum.workflows.nodes.displayable.bases.inline_prompt_node.node.uuid4")
    (
        expected_audio_input_variable_id,
        expected_video_input_variable_id,
        expected_image_input_variable_id,
        expected_document_input_variable_id,
    ) = (uuid4_generator(), uuid4_generator(), uuid4_generator(), uuid4_generator())

    # WHEN we run the workflow
    terminal_event = workflow.run(
        inputs=WorkflowInputs(
            audio_variable=VellumAudio(src="https://example.com/audio-variable.mp3"),
            video_variable=VellumVideo(src="https://example.com/video-variable.mp4"),
            image_variable=VellumImage(src="https://example.com/image-variable.png"),
            document_variable=VellumDocument(src="https://example.com/document-variable.pdf"),
        )
    )

    # THEN the workflow should have completed successfully
    assert terminal_event.name == "workflow.execution.fulfilled"

    # AND the outputs should be as expected
    assert terminal_event.outputs == {
        "results": expected_outputs,
    }

    # AND we should have invoked the Prompt with the expected inputs
    vellum_adhoc_prompt_client.adhoc_execute_prompt_stream.assert_called_once_with(
        ml_model="gpt-4o",
        input_values=[
            PromptRequestAudioInput(
                key="audio_variable",
                type="AUDIO",
                value=VellumAudio(src="https://example.com/audio-variable.mp3"),
            ),
            PromptRequestVideoInput(
                key="video_variable",
                type="VIDEO",
                value=VellumVideo(src="https://example.com/video-variable.mp4"),
            ),
            PromptRequestImageInput(
                key="image_variable",
                type="IMAGE",
                value=VellumImage(src="https://example.com/image-variable.png"),
            ),
            PromptRequestDocumentInput(
                key="document_variable",
                type="DOCUMENT",
                value=VellumDocument(src="https://example.com/document-variable.pdf"),
            ),
        ],
        input_variables=[
            VellumVariable(
                id=str(expected_audio_input_variable_id),
                key="audio_variable",
                type="AUDIO",
            ),
            VellumVariable(
                id=str(expected_video_input_variable_id),
                key="video_variable",
                type="VIDEO",
            ),
            VellumVariable(
                id=str(expected_image_input_variable_id),
                key="image_variable",
                type="IMAGE",
            ),
            VellumVariable(
                id=str(expected_document_input_variable_id),
                key="document_variable",
                type="DOCUMENT",
            ),
        ],
        parameters=DEFAULT_PROMPT_PARAMETERS,
        blocks=[
            ChatMessagePromptBlock(
                chat_role="SYSTEM",
                blocks=[
                    JinjaPromptBlock(
                        block_type="JINJA",
                        template="Describe the attached files.",
                    ),
                    AudioPromptBlock(
                        block_type="AUDIO",
                        state=None,
                        cache_config=None,
                        src="https://example.com/audio.mp3",
                        metadata=None,
                    ),
                    VideoPromptBlock(
                        block_type="VIDEO",
                        state=None,
                        cache_config=None,
                        src="https://example.com/video.mp4",
                        metadata=None,
                    ),
                    ImagePromptBlock(
                        block_type="IMAGE",
                        state=None,
                        cache_config=None,
                        src="https://example.com/image.png",
                        metadata=None,
                    ),
                    DocumentPromptBlock(
                        block_type="DOCUMENT",
                        state=None,
                        cache_config=None,
                        src="https://example.com/document.pdf",
                        metadata=None,
                    ),
                    VariablePromptBlock(
                        block_type="VARIABLE", state=None, cache_config=None, input_variable="audio_variable"
                    ),
                    VariablePromptBlock(
                        block_type="VARIABLE", state=None, cache_config=None, input_variable="video_variable"
                    ),
                    VariablePromptBlock(
                        block_type="VARIABLE", state=None, cache_config=None, input_variable="image_variable"
                    ),
                    VariablePromptBlock(
                        block_type="VARIABLE", state=None, cache_config=None, input_variable="document_variable"
                    ),
                ],
            ),
        ],
        expand_meta=AdHocExpandMeta(cost=None, model_name=None, usage=None, finish_reason=True),
        functions=None,
        request_options=mock.ANY,
        settings=PromptSettings(timeout=1, stream_enabled=True),
    )
