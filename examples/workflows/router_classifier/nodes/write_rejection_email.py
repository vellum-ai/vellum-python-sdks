from vellum import (
    ChatMessagePromptBlock,
    PlainTextPromptBlock,
    PromptParameters,
    RichTextPromptBlock,
    VariablePromptBlock,
)
from vellum.workflows.nodes.displayable import InlinePromptNode

from .evaluate_resume import EvaluateResume


class WriteRejectionEmail(InlinePromptNode):
    """In your application, this could be an Agent, implemented & tested via Subworkflows, which calls APIs to actually send the email, move the candidate in an Applicant Tracking System (ATS), etc."""

    ml_model = "gpt-4o-mini"
    blocks = [
        ChatMessagePromptBlock(
            chat_role="SYSTEM",
            blocks=[
                RichTextPromptBlock(
                    blocks=[
                        PlainTextPromptBlock(
                            state="ENABLED",
                            cache_config=None,
                            text="""\
Please write a rejection email to the following candidate. Use the following <resume_evaluation> to give the candidate feedback that is brief, polite, and respectful. 

<resume_evaluation>
\
""",
                        ),
                        VariablePromptBlock(input_variable="resume_evaluation"),
                        PlainTextPromptBlock(
                            state="ENABLED",
                            cache_config=None,
                            text="""\

</resume_evaluation>\
""",
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
