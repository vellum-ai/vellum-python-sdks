from vellum import (
    ChatMessagePromptBlock,
    PlainTextPromptBlock,
    PromptParameters,
    RichTextPromptBlock,
    VariablePromptBlock,
)
from vellum.workflows.nodes.displayable import InlinePromptNode

from .evaluate_resume import EvaluateResume


class WriteNextRoundEmail(InlinePromptNode):
    """In your application, this could be an Agent, implemented & tested via Subworkflows, which calls APIs to actually send the email, move the candidate in an Applicant Tracking System (ATS), etc."""

    ml_model = "gpt-4o-mini"
    blocks = [
        ChatMessagePromptBlock(
            chat_role="SYSTEM",
            blocks=[
                RichTextPromptBlock(
                    blocks=[
                        PlainTextPromptBlock(
                            text="""\
Please write an email to the following candidate that congratulates them on moving to the next round interview for a role for which they applied. Use the following <resume_evaluation> to give the candidate feedback that is brief, polite, and respectful.

<resume_evaluation>
\
"""
                        ),
                        VariablePromptBlock(input_variable="resume_evaluation"),
                        PlainTextPromptBlock(
                            text="""\

</resume_evaluation>\
"""
                        ),
                    ]
                )
            ],
        ),
    ]
    prompt_inputs = {
        "resume_evaluation": EvaluateResume.Outputs.text,
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
