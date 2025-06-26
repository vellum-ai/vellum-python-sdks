from vellum import (
    ChatMessagePromptBlock,
    PlainTextPromptBlock,
    PromptParameters,
    RichTextPromptBlock,
    VariablePromptBlock,
)
from vellum.workflows.nodes.displayable import InlinePromptNode
from vellum.workflows.state import BaseState

from .formatted_search_results import FormattedSearchResults
from .most_recent_message import MostRecentMessage


class PromptNode9(InlinePromptNode[BaseState]):
    ml_model = "gpt-4o-mini"
    blocks = [
        ChatMessagePromptBlock(
            chat_role="SYSTEM",
            blocks=[
                RichTextPromptBlock(
                    blocks=[
                        PlainTextPromptBlock(
                            text="""\
 Question:
---------------
\
"""
                        ),
                        VariablePromptBlock(input_variable="question"),
                        PlainTextPromptBlock(
                            text="""\


Policy Quotes:
-----------------------
\
"""
                        ),
                        VariablePromptBlock(input_variable="context"),
                    ]
                ),
                RichTextPromptBlock(
                    blocks=[
                        PlainTextPromptBlock(
                            text="""\
You are an expert on FAA rules, guidelines, and safety. Answer the above question given the context. Provide citation of the policy you got it from at the end of the response. If you don\'t know the answer, say \"Sorry, I don\'t know\"

Limit your response to 250 words. Just use plain text, no special characters, no commas, no mathematical signs like + -\
"""
                        )
                    ]
                ),
            ],
        ),
    ]
    prompt_inputs = {
        "question": MostRecentMessage.Outputs.result,
        "context": FormattedSearchResults.Outputs.result,
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
