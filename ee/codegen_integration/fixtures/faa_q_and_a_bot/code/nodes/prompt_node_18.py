from vellum import (
    ChatMessagePromptBlock,
    PlainTextPromptBlock,
    PromptParameters,
    RichTextPromptBlock,
    VariablePromptBlock,
)
from vellum.workflows.nodes.displayable import InlinePromptNode

from .api_node import APINode


class PromptNode18(InlinePromptNode):
    ml_model = "claude-3-5-sonnet-20241022"
    blocks = [
        ChatMessagePromptBlock(
            state="ENABLED",
            cache_config=None,
            chat_role="USER",
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
                            text="Based on the below JSON response from an airline flight status tracker API, which flights are on the ground? And which airports are they going from and to? Where are they right now?\n\n",
                        ),
                        VariablePromptBlock(
                            state="ENABLED", cache_config=None, input_variable="text"
                        ),
                    ],
                )
            ],
        ),
        ChatMessagePromptBlock(
            state="ENABLED",
            cache_config=None,
            chat_role="USER",
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
                            text=" Respond in the following format\n\nThe flights that are on the ground are:\n\n1. **Flight Number:** WN597\n   - **Departure Airport:** LAS (Las Vegas McCarran International Airport)\n   - **Arrival Airport:** SJC (San Jose International Airport)\n   - **Current Location:** Latitude 37.3664, Longitude -121.929 (San Jose International Airport)\n",
                        )
                    ],
                )
            ],
        ),
        ChatMessagePromptBlock(
            state="ENABLED",
            cache_config=None,
            chat_role="USER",
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
                            text=" Just use plain text and no special characters",
                        )
                    ],
                )
            ],
        ),
    ]
    parameters = PromptParameters(
        stop=None,
        temperature=0,
        max_tokens=1000,
        top_p=1,
        top_k=None,
        frequency_penalty=None,
        presence_penalty=None,
        logit_bias=None,
        custom_parameters=None,
    )
    prompt_inputs = {"text": APINode.Outputs.json}