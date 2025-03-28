from vellum import ChatMessagePromptBlock, JinjaPromptBlock, PromptParameters
from vellum.workflows.nodes.displayable import InlinePromptNode

from ..inputs import Inputs


class EvaluateResume(InlinePromptNode):
    """Here we use GPT Structured Outputs to create consistent JSON. From there, we can parse and extract a "score"

    With that score, we can then route to different Prompts or Agents"""

    ml_model = "gpt-4o-mini"
    blocks = [
        ChatMessagePromptBlock(
            chat_role="SYSTEM",
            blocks=[
                JinjaPromptBlock(
                    template="""\
Compare the following resume to the job description and evaluate it based on the provided schema.

{#- The schema is provided in the Model tab -#}
{#- You can leave comments in Jinja Prompt Blocks like this -#}\
"""
                )
            ],
        ),
        ChatMessagePromptBlock(
            chat_role="USER",
            blocks=[
                JinjaPromptBlock(
                    template="""\
<resume>
{{ resume }}
</resume>

<job_description>
{{ job_description }}
</job_description>\
"""
                )
            ],
        ),
    ]
    prompt_inputs = {
        "resume": Inputs.resume,
        "job_description": Inputs.job_requirements,
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
        custom_parameters={
            "json_schema": {
                "name": "match_scorer_schema",
                "schema": {
                    "type": "object",
                    "title": "MatchScorerSchema",
                    "required": [
                        "recommendation",
                        "score",
                        "remarks",
                    ],
                    "properties": {
                        "score": {
                            "type": "integer",
                            "title": "Match Score",
                            "description": "Match score out of 10",
                        },
                        "remarks": {
                            "type": "string",
                            "title": "Remarks",
                            "description": "Remarks about the match",
                        },
                        "recommendation": {
                            "enum": [
                                "Advance",
                                "Defer",
                                "Reject",
                            ],
                            "type": "string",
                            "title": "Status",
                            "description": "Recommendation for the candidate. Denotes whether they should move forward, get deferred, or rejected from the process. ",
                        },
                    },
                },
            },
        },
    )
