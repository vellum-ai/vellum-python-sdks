from vellum import (
    ChatMessagePromptBlock,
    PlainTextPromptBlock,
    PromptParameters,
    RichTextPromptBlock,
    VariablePromptBlock,
)
from vellum.workflows.nodes.displayable import InlinePromptNode

from .add_image_to_chat_history import AddImageToChatHistory


class ExtractByDocumentURL(InlinePromptNode):
    ml_model = "claude-3-7-sonnet-latest"
    blocks = [
        ChatMessagePromptBlock(
            chat_role="SYSTEM",
            blocks=[
                RichTextPromptBlock(
                    blocks=[
                        PlainTextPromptBlock(
                            state="ENABLED",
                            cache_config=None,
                            text="""What is the small top pressure rating of the 1.5\" valve?""",
                        )
                    ]
                )
            ],
        ),
        VariablePromptBlock(input_variable="chat_history"),
    ]
    prompt_inputs = {
        "chat_history": AddImageToChatHistory.Outputs.result,
    }
    parameters = PromptParameters(
        stop=[],
        temperature=0,
        max_tokens=1000,
        top_p=1,
        top_k=None,
        frequency_penalty=None,
        presence_penalty=None,
        logit_bias={},
        custom_parameters=None,
    )
