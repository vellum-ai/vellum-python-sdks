from vellum import (
    ChatMessagePromptBlock,
    PlainTextPromptBlock,
    PromptParameters,
    RichTextPromptBlock,
    VariablePromptBlock,
)
from vellum.workflows.nodes.displayable import InlinePromptNode
from vellum.workflows.state import BaseState

from .subworkflow_node import SubworkflowNode


class PromptNode14(InlinePromptNode[BaseState]):
    ml_model = "gpt-4o-mini"
    blocks = [
        ChatMessagePromptBlock(
            chat_role="SYSTEM",
            blocks=[
                RichTextPromptBlock(
                    blocks=[
                        PlainTextPromptBlock(
                            text="""Summarize the weather. Just use plain text, no special characters, no commas, no mathematical signs like + -"""
                        )
                    ]
                )
            ],
        ),
        VariablePromptBlock(input_variable="chat_history"),
    ]
    prompt_inputs = {
        "chat_history": SubworkflowNode.Outputs.chat_history,
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
