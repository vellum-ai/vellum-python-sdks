from typing import List

from vellum import (
    ChatMessage,
    ChatMessagePromptBlock,
    PlainTextPromptBlock,
    PromptParameters,
    RichTextPromptBlock,
    VariablePromptBlock,
)
from vellum.workflows.nodes.displayable.tool_calling_node.node import ToolCallingNode as BaseToolCallingNode


class ToolCallingNode(BaseToolCallingNode):
    ml_model = "gpt-4o-mini"
    prompt_inputs = {
        "text": None,
    }
    blocks = [
        ChatMessagePromptBlock(
            chat_role="SYSTEM",
            blocks=[
                RichTextPromptBlock(
                    blocks=[
                        PlainTextPromptBlock(
                            text="""\
Summarize the following text:

\
"""
                        ),
                        VariablePromptBlock(input_variable="text"),
                    ]
                )
            ],
        ),
    ]
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
    settings = {
        "stream_enabled": True,
    }
    max_prompt_iterations = 5

    class Outputs(BaseToolCallingNode.Outputs):
        text: str
        chat_history: List[ChatMessage]
