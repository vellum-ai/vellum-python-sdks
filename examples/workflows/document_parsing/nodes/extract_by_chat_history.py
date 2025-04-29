from vellum import (
    ChatMessagePromptBlock,
    PlainTextPromptBlock,
    PromptParameters,
    RichTextPromptBlock,
    VariablePromptBlock,
)
from vellum.workflows.nodes.displayable import InlinePromptNode

from ..inputs import Inputs


class ExtractByChatHistory(InlinePromptNode):
    """You can use this approach if you want to drag-and-drop documents in the UI / use them in Scenarios, or include them from your application code. This approach will also make it easier to view documents directly in your Evaluations and Test Cases."""

    ml_model = "claude-3-7-sonnet-latest"
    blocks = [
        ChatMessagePromptBlock(
            chat_role="SYSTEM",
            blocks=[
                RichTextPromptBlock(
                    blocks=[PlainTextPromptBlock(text="""What is the small top pressure rating of the 1.5\" valve?""")]
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
        frequency_penalty=None,
        presence_penalty=None,
        logit_bias={},
        custom_parameters=None,
    )
