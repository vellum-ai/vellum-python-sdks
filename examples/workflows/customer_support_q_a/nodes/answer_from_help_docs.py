from vellum import ChatMessagePromptBlock, PlainTextPromptBlock, PromptParameters, RichTextPromptBlock
from vellum.workflows.nodes.displayable import InlinePromptNode

from ..inputs import Inputs
from .get_search_results_with_metadata import GetSearchResultsWithMetadata


class AnswerFromHelpDocs(InlinePromptNode):
    ml_model = "gpt-4o-mini"
    blocks = [
        ChatMessagePromptBlock(
            chat_role="SYSTEM",
            blocks=[
                RichTextPromptBlock(
                    blocks=[
                        PlainTextPromptBlock(
                            text="""\
You are a Customer Support bot that helps answer questions from customers based on context provided to you from our Help Docs and API docs. If the context is insufficient, say \"Sorry, I don\'t know.\"

The context will include some metadata with more information about where the corresponding help doc exists on our site. Please include a link to the Help Doc URL somewhere in your response, and leverage other aspects of the metadata if it improves the quality of your response. You can be extremely concise and quickly link them to the Help Doc URL.

The context and customer question will be provided to you in the following format:

<context>
...
</context>

<question>
...
</question>\
"""
                        )
                    ]
                )
            ],
        ),
        ChatMessagePromptBlock(
            chat_role="USER",
            blocks=[
                RichTextPromptBlock(
                    blocks=[
                        PlainTextPromptBlock(
                            text="""\
<context>
{{ context_str }}
</context>

<question>
{{ customer_question }}  
</question>\
"""
                        )
                    ]
                )
            ],
        ),
    ]
    prompt_inputs = {
        "context_str": GetSearchResultsWithMetadata.Outputs.result,
        "customer_question": Inputs.question,
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
