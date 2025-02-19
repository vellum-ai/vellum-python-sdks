from vellum import ChatMessagePromptBlock, PlainTextPromptBlock, PromptParameters, RichTextPromptBlock
from vellum.workflows.nodes.displayable import InlinePromptNode


class PromptNode19(InlinePromptNode):
    ml_model = "gpt-4o-2024-05-13"
    blocks = [
        ChatMessagePromptBlock(
            state="ENABLED",
            cache_config=None,
            chat_role="SYSTEM",
            chat_source=None,
            chat_message_unterminated=False,
            blocks=[
                RichTextPromptBlock(
                    state="ENABLED",
                    cache_config=None,
                    blocks=[
                        PlainTextPromptBlock(
                            state="ENABLED",
                            cache_config=None,
                            text='Respond with "Sorry I don\'t know"',
                        )
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
