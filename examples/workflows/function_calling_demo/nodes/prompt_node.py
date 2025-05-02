from vellum import ChatMessagePromptBlock, FunctionDefinition, JinjaPromptBlock, PromptParameters, VariablePromptBlock
from vellum.workflows.nodes.displayable import InlinePromptNode

from ..inputs import Inputs
from .accumulate_chat_history import AccumulateChatHistory


class PromptNode(InlinePromptNode):
    ml_model = "gpt-3.5-turbo"
    blocks = [
        ChatMessagePromptBlock(
            chat_role="SYSTEM",
            blocks=[
                JinjaPromptBlock(
                    template="""You are an expert meteorologist that helps correctly answer questions about the weather. Answer questions factually based  the information that you\'re provided and ask clarifying questions when needed"""
                )
            ],
        ),
        VariablePromptBlock(input_variable="chat_history"),
    ]
    prompt_inputs = {
        "chat_history": AccumulateChatHistory.Outputs.result.coalesce(Inputs.chat_history),
    }
    functions = [
        FunctionDefinition(
            name="get_current_weather",
            description="Get the current weather in a given location",
            parameters={
                "type": "object",
                "required": [
                    "location",
                ],
                "properties": {
                    "unit": {
                        "enum": [
                            "celsius",
                            "fahrenheit",
                        ],
                        "type": "string",
                    },
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA",
                    },
                },
            },
            function_forced=False,
            function_strict=False,
        ),
    ]
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
