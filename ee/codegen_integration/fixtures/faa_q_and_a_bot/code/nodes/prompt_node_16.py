from vellum import (
    ChatMessagePromptBlock,
    PlainTextPromptBlock,
    PromptParameters,
    RichTextPromptBlock,
    VariablePromptBlock,
)
from vellum.workflows.nodes.displayable import InlinePromptNode

from .most_recent_message import MostRecentMessage


class PromptNode16(InlinePromptNode):
    ml_model = "gpt-4o"
    blocks = [
        ChatMessagePromptBlock(
            chat_role="SYSTEM",
            blocks=[
                RichTextPromptBlock(
                    blocks=[
                        PlainTextPromptBlock(
                            text="""\
Respond with the IATA airport name this incoming message is about. For example, respond only with \"SJC\", \"SFO\", \"EWR\" or \"JFK\"

\
"""
                        ),
                        VariablePromptBlock(input_variable="most_recent_message"),
                    ]
                )
            ],
        ),
    ]
    prompt_inputs = {
        "most_recent_message": MostRecentMessage.Outputs.result,
    }
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
