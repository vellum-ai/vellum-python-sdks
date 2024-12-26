from vellum import (
    ChatMessagePromptBlock,
    PlainTextPromptBlock,
    PromptParameters,
    RichTextPromptBlock,
    VariablePromptBlock,
)
from vellum.workflows.nodes.displayable import InlinePromptNode

from ..inputs import Inputs


class PromptNode(InlinePromptNode):
    ml_model = "gpt-4o-mini"
    blocks = [
        ChatMessagePromptBlock(
            state="ENABLED",
            chat_role="SYSTEM",
            chat_source=None,
            chat_message_unterminated=False,
            blocks=[
                RichTextPromptBlock(
                    state="ENABLED",
                    blocks=[
                        PlainTextPromptBlock(
                            state="ENABLED",
                            cache_config=None,
                            text="""\
Summarize the following text:

\
""",
                        ),
                        VariablePromptBlock(state="ENABLED", input_variable="text"),
                    ],
                )
            ],
        )
    ]
    parameters = PromptParameters(
        stop=None,
        temperature=0,
        max_tokens=1000,
        top_p=1,
        top_k=0,
        frequency_penalty=0,
        presence_penalty=0,
        logit_bias={},
        custom_parameters=None,
    )
    prompt_inputs = {"text": Inputs.text}
