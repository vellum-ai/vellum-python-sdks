from vellum import ChatMessagePromptBlock, JinjaPromptBlock, PromptParameters, VariablePromptBlock
from vellum.workflows.nodes.displayable import InlinePromptNode

from ..inputs import Inputs
from .formatted_search_results import FormattedSearchResults


class AnswerQuestion(InlinePromptNode):
    """Here we use an LLM to answer the user's question. We give it the search results and previous messages in the conversation as context."""

    ml_model = "gpt-4o-mini"
    blocks = [
        ChatMessagePromptBlock(
            chat_role="SYSTEM",
            blocks=[
                JinjaPromptBlock(
                    template="""\
Answer the user\'s question based on the context provided below. If you don\'t know the answer say \"Sorry, I don\'t know.\"

**Context**
``
{{ context }}
``

Limit your answer to 250 words and provide a citation at the end of your answer\
"""
                )
            ],
        ),
        VariablePromptBlock(input_variable="chat_history"),
    ]
    prompt_inputs = {
        "chat_history": Inputs.chat_history,
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
