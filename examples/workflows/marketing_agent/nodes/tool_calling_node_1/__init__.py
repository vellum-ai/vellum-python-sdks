from .context_collector import context_collector
from .email_getter import email_getter
from .post_linkedin import post_linkedin
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

from ...inputs import Inputs


class ToolCallingNode(BaseToolCallingNode):
    ml_model = "gpt-4.1-mini"
    prompt_inputs = {
        "chat_history": Inputs.chat_history,
    }
    blocks = [
        ChatMessagePromptBlock(
            chat_role="SYSTEM",
            blocks=[
                RichTextPromptBlock(
                    blocks=[
                        PlainTextPromptBlock(
                            text="""AI-powered marketing agent that collects product information, uploads media to Vellum, stores data in MongoDB, and provides strategic marketing recommendations for product promotion and campaign optimization."""
                        )
                    ]
                )
            ],
        ),
        VariablePromptBlock(input_variable="chat_history"),
    ]
    parameters = PromptParameters(
        stop=[],
        temperature=0,
        max_tokens=8192,
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
    functions = [context_collector, email_getter, post_linkedin]

    class Outputs(BaseToolCallingNode.Outputs):
        text: str
        chat_history: List[ChatMessage]
