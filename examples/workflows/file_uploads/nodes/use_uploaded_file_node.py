from vellum import ChatMessagePromptBlock, PlainTextPromptBlock, RichTextPromptBlock, VariablePromptBlock
from vellum.workflows.nodes.displayable import InlinePromptNode

from .upload_file_node import UploadFileNode


class UseUploadedFileNode(InlinePromptNode):
    """
    Uses uploaded image files in a prompt.

    This node receives VellumImages with vellum:uploaded-file:* URIs
    and uses them in a vision prompt. The files are automatically resolved
    by Vellum's infrastructure.
    """

    ml_model = "gpt-5-responses"
    blocks = [
        ChatMessagePromptBlock(
            chat_role="SYSTEM",
            blocks=[
                RichTextPromptBlock(
                    blocks=[
                        PlainTextPromptBlock(text="Analyze the images provided and describe what you see in detail.")
                    ]
                ),
                VariablePromptBlock(input_variable="receipt"),
                VariablePromptBlock(input_variable="four_pillars"),
            ],
        ),
    ]
    prompt_inputs = {
        "receipt": UploadFileNode.Outputs.receipt,
        "four_pillars": UploadFileNode.Outputs.four_pillars,
    }
