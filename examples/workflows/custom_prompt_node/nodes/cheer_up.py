from vellum import ChatMessagePromptBlock, PlainTextPromptBlock, RichTextPromptBlock, VariablePromptBlock

from ..inputs import Inputs
from .local_bedrock_node import LocalBedrockNode


class CheerUpPrompt(LocalBedrockNode):
    ml_model = "aws-bedrock//anthropic/claude-3-5-sonnet-20240620-v1:0/us-west-2"

    blocks = [
        ChatMessagePromptBlock(
            chat_role="SYSTEM",
            blocks=[
                RichTextPromptBlock(
                    blocks=[
                        PlainTextPromptBlock(
                            text="""\
You will be given a message from the user that is already categorized as sad.

Offer some words of encouragement and support.
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
