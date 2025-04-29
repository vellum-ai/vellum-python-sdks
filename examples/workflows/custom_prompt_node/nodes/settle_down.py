from vellum import ChatMessagePromptBlock, PlainTextPromptBlock, RichTextPromptBlock, VariablePromptBlock

from ..inputs import Inputs
from .local_bedrock_node import LocalBedrockNode


class SettleDownPrompt(LocalBedrockNode):
    ml_model = "aws-bedrock//anthropic/claude-3-5-sonnet-20240620-v1:0/us-west-2"

    blocks = [
        ChatMessagePromptBlock(
            chat_role="SYSTEM",
            blocks=[
                RichTextPromptBlock(
                    blocks=[
                        PlainTextPromptBlock(
                            text="""\
You will be given a message from the user that is already categorized as angry.

Give a short, concise response that helps the user calm down.
"""
                        )
                    ]
                )
            ],
        ),
        ChatMessagePromptBlock(
            chat_role="USER",
            blocks=[
                RichTextPromptBlock(
                    blocks=[
                        VariablePromptBlock(input_variable="message"),
                    ]
                )
            ],
        ),
    ]

    prompt_inputs = {
        "message": Inputs.message,
    }
