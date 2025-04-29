from vellum import (
    ChatMessagePromptBlock,
    FunctionDefinition,
    PlainTextPromptBlock,
    PromptParameters,
    RichTextPromptBlock,
    VariablePromptBlock,
)
from vellum.workflows.nodes.displayable import InlinePromptNode

from ..inputs import Inputs
from ..state import State


class MyPrompt(InlinePromptNode):
    ml_model = "gpt-4o-mini"
    blocks = [
        ChatMessagePromptBlock(
            chat_role="SYSTEM",
            blocks=[
                RichTextPromptBlock(
                    blocks=[
                        PlainTextPromptBlock(
                            text="""You are a helpful assistant that can answer questions and help with tasks."""
                        )
                    ]
                )
            ],
        ),
        ChatMessagePromptBlock(chat_role="USER", blocks=[VariablePromptBlock(input_variable="query")]),
        VariablePromptBlock(input_variable="chat_history"),
    ]
    prompt_inputs = {
        "query": Inputs.query,
        "chat_history": State.chat_history,
    }
    functions = [
        FunctionDefinition(name="get_temperature", description="Use this tool for any questions about the weather."),
        FunctionDefinition(name="echo_request", description="Use this tool for any questions about job searching."),
        FunctionDefinition(
            name="fibonacci", description="Use this tool for any questions about topics outside of work."
        ),
    ]
    parameters = PromptParameters(
        stop=[],
        temperature=0,
        max_tokens=4096,
        top_p=1,
        top_k=0,
        frequency_penalty=0,
        presence_penalty=0,
        logit_bias=None,
        custom_parameters=None,
    )
