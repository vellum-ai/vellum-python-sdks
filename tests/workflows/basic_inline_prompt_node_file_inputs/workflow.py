from vellum import ChatMessagePromptBlock, JinjaPromptBlock
from vellum.client.types import VellumAudio, VellumDocument, VellumImage, VellumVideo
from vellum.client.types.audio_prompt_block import AudioPromptBlock
from vellum.client.types.document_prompt_block import DocumentPromptBlock
from vellum.client.types.image_prompt_block import ImagePromptBlock
from vellum.client.types.prompt_settings import PromptSettings
from vellum.client.types.variable_prompt_block import VariablePromptBlock
from vellum.client.types.video_prompt_block import VideoPromptBlock
from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs import BaseInputs
from vellum.workflows.nodes.displayable.bases.inline_prompt_node import BaseInlinePromptNode
from vellum.workflows.outputs import BaseOutputs
from vellum.workflows.state import BaseState


class WorkflowInputs(BaseInputs):
    audio_variable: VellumAudio
    video_variable: VellumVideo
    image_variable: VellumImage
    document_variable: VellumDocument


class ExampleInlinePromptNode(BaseInlinePromptNode):
    ml_model = "gpt-4o"
    blocks = [
        ChatMessagePromptBlock(
            chat_role="SYSTEM",
            blocks=[
                JinjaPromptBlock(
                    block_type="JINJA",
                    template="Describe the attached files.",
                ),
                AudioPromptBlock(
                    src="https://example.com/audio.mp3",
                ),
                VideoPromptBlock(
                    src="https://example.com/video.mp4",
                ),
                ImagePromptBlock(
                    src="https://example.com/image.png",
                ),
                DocumentPromptBlock(
                    src="https://example.com/document.pdf",
                ),
                VariablePromptBlock(
                    input_variable="audio_variable",
                ),
                VariablePromptBlock(
                    input_variable="video_variable",
                ),
                VariablePromptBlock(
                    input_variable="image_variable",
                ),
                VariablePromptBlock(
                    input_variable="document_variable",
                ),
            ],
        ),
    ]
    prompt_inputs = {
        "audio_variable": WorkflowInputs.audio_variable,
        "video_variable": WorkflowInputs.video_variable,
        "image_variable": WorkflowInputs.image_variable,
        "document_variable": WorkflowInputs.document_variable,
    }
    settings = PromptSettings(timeout=1, stream_enabled=True)


class FileInputInlinePromptWorkflow(BaseWorkflow[WorkflowInputs, BaseState]):
    graph = ExampleInlinePromptNode

    class Outputs(BaseOutputs):
        results = ExampleInlinePromptNode.Outputs.results
