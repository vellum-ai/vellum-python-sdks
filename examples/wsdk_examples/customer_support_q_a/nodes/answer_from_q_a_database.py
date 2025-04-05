from vellum import ChatMessagePromptBlock, JinjaPromptBlock, PromptParameters
from vellum.workflows.nodes.displayable import InlinePromptNode

from ..inputs import Inputs
from .q_a_bank_lookup import QABankLookup


class AnswerFromQADatabase(InlinePromptNode):
    ml_model = "gpt-4o-mini"
    blocks = [
        ChatMessagePromptBlock(
            chat_role="SYSTEM",
            blocks=[
                JinjaPromptBlock(
                    template="""\
You are a Customer Support bot that helps answer questions from customers based on context from previous Q&A that our staff have already answered. 

The context will be a few examples of questions and answers that we found from previous questions we\'ve answered for customers.

Your task is to answer questions based on the context provided without using any other knowledge. If the customer\'s question can\'t be answered using the provided context, say \"Sorry, I don\'t know.\" You should start by acknowledging the user\'s question.

The context and customer question will be provided to you in the following format. 

<context>
...
</context>

<question>
...
</question>\
"""
                )
            ],
        ),
        ChatMessagePromptBlock(
            chat_role="USER",
            blocks=[
                JinjaPromptBlock(
                    template="""\
<context>
{{ context_str }}
</context>

<question>
{{ customer_question }}  
</question>\
"""
                )
            ],
        ),
    ]
    prompt_inputs = {
        "context_str": QABankLookup.Outputs.text,
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
