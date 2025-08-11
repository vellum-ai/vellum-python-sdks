from vellum import ChatMessagePromptBlock, PlainTextPromptBlock, PromptParameters, RichTextPromptBlock
from vellum.workflows.nodes.displayable import InlinePromptNode
from vellum.workflows.types.core import MergeBehavior


class PromptNode19(InlinePromptNode):
    ml_model = "gpt-4o-2024-05-13"
    blocks = [
        ChatMessagePromptBlock(
            chat_role="SYSTEM",
            blocks=[
                RichTextPromptBlock(blocks=[PlainTextPromptBlock(text="""Respond with \"Sorry I don\'t know\"""")])
            ],
        ),
    ]
    prompt_inputs = {}
    parameters = PromptParameters(
        stop=[],
        temperature=0,
        max_tokens=1000,
        top_p=1,
        top_k=None,
        frequency_penalty=0,
        presence_penalty=0,
        logit_bias={},
        custom_parameters=None,
    )

    class Trigger(InlinePromptNode.Trigger):
        merge_behavior = MergeBehavior.AWAIT_ANY
