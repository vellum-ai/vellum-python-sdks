from vellum import (
    ChatMessagePromptBlock,
    PlainTextPromptBlock,
    PromptParameters,
    RichTextPromptBlock,
    VariablePromptBlock,
)
from vellum.workflows.nodes.displayable import InlinePromptNode


class ProblemSolverAgent(InlinePromptNode):
    """Here we use any context we have from an Evaluator Agent to answer a math problem for a user. If we haven't run the answer through the Evaluator Agent yet, then we initialize an empty Chat History as a "fallback value\" """

    ml_model = "gpt-4o-mini"
    blocks = [
        ChatMessagePromptBlock(
            chat_role="SYSTEM",
            blocks=[
                RichTextPromptBlock(
                    blocks=[
                        PlainTextPromptBlock(
                            text="""\
You are a problem solving agent helping answer a <problem> from a user. You will get feedback from an Evaluator Agent on the quality of your solution and you should use it to iterate upon your solution until you have a satisfactory answer. 

Answer the following math question step by step:

<problem>
\
"""
                        ),
                        VariablePromptBlock(input_variable="math_problem"),
                        PlainTextPromptBlock(
                            text="""\
 
</problem>\
"""
                        ),
                    ]
                )
            ],
        ),
        VariablePromptBlock(input_variable="chat_history"),
    ]
    prompt_inputs = {
        "math_problem": "If a train travels 120 miles in 2 hours, then accelerates and covers the next 180 miles in 2 hours, what is its average speed for the entire trip?",
        "chat_history": [],
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
