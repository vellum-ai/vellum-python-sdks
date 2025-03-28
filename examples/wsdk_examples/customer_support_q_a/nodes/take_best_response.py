from vellum import ChatMessagePromptBlock, JinjaPromptBlock, PromptParameters
from vellum.workflows.nodes.displayable import InlinePromptNode

from ..inputs import Inputs
from .answer_from_help_docs import AnswerFromHelpDocs
from .answer_from_q_a_database import AnswerFromQADatabase


class TakeBestResponse(InlinePromptNode):
    ml_model = "gpt-4o-mini"
    blocks = [
        ChatMessagePromptBlock(
            chat_role="SYSTEM",
            blocks=[
                JinjaPromptBlock(
                    template="""\
You are an expert Customer Support Agent. You are using information provided by two other customer support agents each with different sources of information to help answer customers questions. One agent will use a question and answer bank from previous customer inquiries. The other agent will use the Help Docs and API Docs. 

You will review the customer\'s initial question, and the responses proposed by the two customer support agents. Your task is to decide how to respond based on what each support agent suggested. Talk directly to the user and don\'t reveal that you have two agents supporting you behind the scenes. If you don\'t have a good response based on the information provided by the other support agents, say \"I\'m sorry, I don\'t know the answer to that. I\'ll loop in the Vellum team to help!\"

If one doesn\'t know the answer, use the answer provided by the other agent!

The relevant information will be provided to you in the following format:

<user_question>
...
</user_question>

<support_bot_response_1>
...
</support_bot_response_1>

<support_bot_response_2>
...
</support_bot_response_2>\
"""
                )
            ],
        ),
        ChatMessagePromptBlock(
            chat_role="USER",
            blocks=[
                JinjaPromptBlock(
                    template="""\
<user_question>
{{ user_question }}
</user_question>

<support_bot_response_1>
{{ support_bot_response_1 }}
</support_bot_response_1>

<support_bot_response_2>
{{ support_bot_response_2 }}
</support_bot_response_2>\
"""
                )
            ],
        ),
    ]
    prompt_inputs = {
        "question": Inputs.question,
        "support_bot_response_1": AnswerFromQADatabase.Outputs.text,
        "support_bot_response_2": AnswerFromHelpDocs.Outputs.text,
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
