from vellum import (
    ChatMessagePromptBlock,
    PlainTextPromptBlock,
    PromptParameters,
    RichTextPromptBlock,
    VariablePromptBlock,
)
from vellum.workflows.nodes.displayable import InlinePromptNode

from ..inputs import Inputs


class SummarizeImageByChatHistory(InlinePromptNode):
    """You can use this approach if you want to drag-and-drop images in the UI, use them in Scenarios, or include them from your application code. This approach will also make it easier to view images directly in your Evaluations and Test Cases."""

    ml_model = "gpt-4o-mini"
    blocks = [
        ChatMessagePromptBlock(
            chat_role="SYSTEM",
            blocks=[
                RichTextPromptBlock(
                    blocks=[PlainTextPromptBlock(text="""Please describe what you see in the image. """)]
                )
            ],
        ),
        VariablePromptBlock(input_variable="chat_history"),
    ]
    prompt_inputs = {
        "chat_history": Inputs.workflow_input_chat_history,
    }
    parameters = PromptParameters(
        stop=[],
        temperature=0,
        max_tokens=1000,
        top_p=1,
        top_k=0,
        frequency_penalty=0,
        presence_penalty=0,
        logit_bias={},
        custom_parameters=None,
    )
