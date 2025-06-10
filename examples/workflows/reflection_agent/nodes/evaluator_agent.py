from vellum import (
    ChatMessagePromptBlock,
    PlainTextPromptBlock,
    PromptParameters,
    RichTextPromptBlock,
    VariablePromptBlock,
)
from vellum.workflows.nodes.displayable import InlinePromptNode

from ..inputs import Inputs
from .problem_solver_agent import ProblemSolverAgent


class EvaluatorAgent(InlinePromptNode):
    """Here we use GPT's Structured Outputs to return "status" and "feedback" of whether or not the proposed solution is acceptable, along with feedback about what isn't correct in the proposed solution.

    Notably, we are not including the full conversation context here. This is a use-case dependent decision. By doing this, we are effectively grading the quality of the current solution in isolation, reducing some variability, reducing the tokens in our context window, and reducing  cost.
    """

    ml_model = "gpt-4o-mini"
    blocks = [
        ChatMessagePromptBlock(
            chat_role="SYSTEM",
            blocks=[
                RichTextPromptBlock(
                    blocks=[
                        PlainTextPromptBlock(
                            text="""\
You are reviewing a Problem Solving Agent’s <proposed_solution> to solve a math <problem> step-by-step. Clearly identify any logical or calculation errors. If errors are found, briefly suggest corrections and instruct the agent to try again, incorporating your feedback.

<problem>
\
"""
                        ),
                        VariablePromptBlock(input_variable="math_problem"),
                        PlainTextPromptBlock(
                            text="""\

</problem>

<proposed_solution>
\
"""
                        ),
                        VariablePromptBlock(input_variable="proposed_solution"),
                        PlainTextPromptBlock(
                            text="""\

</proposed_solution>\
"""
                        ),
                    ]
                )
            ],
        ),
    ]
    prompt_inputs = {
        "math_problem": Inputs.math_problem,
        "proposed_solution": ProblemSolverAgent.Outputs.text,
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
                "name": "reasoning_schema",
                "schema": {
                    "type": "object",
                    "required": [
                        "status",
                        "feedback",
                    ],
                    "properties": {
                        "status": {
                            "enum": [
                                "needs_revision",
                                "acceptable",
                            ],
                            "type": "string",
                            "description": "Denotes whether the <proposed_solution> is acceptable or needs revision. ",
                        },
                        "feedback": {
                            "type": "string",
                            "description": "Feedback about the <proposed_solution> for the Problem Solving Agent to use in a subsequent attempt. ",
                        },
                    },
                },
                "strict": True,
            },
        },
    )
