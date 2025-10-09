from .email_getter import email_getter
from .function_1 import function_1
from typing import List

from vellum import (
    ChatMessage,
    ChatMessagePromptBlock,
    PlainTextPromptBlock,
    PromptParameters,
    RichTextPromptBlock,
    VariablePromptBlock,
)
from vellum.workflows.nodes.displayable.tool_calling_node.node import ToolCallingNode
from vellum.workflows.references import LazyReference


class EmailSender(ToolCallingNode):
    ml_model = "gemini-2.5-flash"
    prompt_inputs = {
        "chat_history": LazyReference("ToolCallingNode.Outputs.text"),
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
                        VariablePromptBlock(input_variable="chat_history"),
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
    functions = [email_getter, function_1]

    class Outputs(ToolCallingNode.Outputs):
        text: str
        chat_history: List[ChatMessage]
