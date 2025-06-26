from vellum import (
    ChatMessagePromptBlock,
    PlainTextPromptBlock,
    PromptParameters,
    RichTextPromptBlock,
    VariablePromptBlock,
)
from vellum.workflows.nodes.core.try_node.node import TryNode
from vellum.workflows.nodes.displayable import InlinePromptNode


@TryNode.wrap()
class PromptNode(InlinePromptNode):
    ml_model = "gpt-4o-mini"
    blocks = [
        ChatMessagePromptBlock(
            chat_role="SYSTEM",
            blocks=[
                RichTextPromptBlock(
                    blocks=[
                        PlainTextPromptBlock(
                            text="""\
What is the origin of the following phrase

\
"""
                        ),
                        VariablePromptBlock(input_variable="text"),
                    ]
                )
            ],
        ),
    ]
    prompt_inputs = {
        "text": "Hello, World!",
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
