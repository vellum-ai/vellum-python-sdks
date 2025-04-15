from vellum.client.types.chat_message import ChatMessage
from vellum.client.types.chat_message_prompt_block import ChatMessagePromptBlock
from vellum.client.types.function_definition import FunctionDefinition
from vellum.client.types.plain_text_prompt_block import PlainTextPromptBlock
from vellum.client.types.rich_text_prompt_block import RichTextPromptBlock
from vellum.client.types.variable_prompt_block import VariablePromptBlock
from vellum.workflows.nodes.experimental.tool_calling_node import ToolCallingNode
from vellum.workflows.workflows.base import BaseWorkflow


def get_current_weather(location: str, unit: str) -> str:
    """
    Get the current weather in a given location.
    """
    return f"The current weather in {location} is sunny with a temperature of 70 degrees {unit}."


class GetCurrentWeatherNode(ToolCallingNode):
    """
    A tool calling node that calls the get_current_weather function.
    """

    ml_model = "gpt-4o-mini"
    blocks = [
        ChatMessagePromptBlock(
            chat_role="SYSTEM",
            blocks=[
                RichTextPromptBlock(
                    blocks=[
                        PlainTextPromptBlock(
                            text="You are a weather expert",
                        ),
                    ],
                ),
            ],
        ),
        ChatMessagePromptBlock(
            chat_role="USER",
            blocks=[
                RichTextPromptBlock(
                    blocks=[
                        VariablePromptBlock(
                            input_variable="question",
                        ),
                    ],
                ),
            ],
        ),
    ]
    function_callables = {"get_current_weather": get_current_weather}
    functions = [
        FunctionDefinition(
            name="get_current_weather",
            description="Get the current weather",
            parameters={
                "type": "object",
                "properties": {
                    "location": {"type": "string", "description": "City and state, e.g. San Francisco, CA"},
                    "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
                },
                "required": ["location"],
            },
            forced=False,
        ),
    ]
    prompt_inputs = {
        "question": "What's the weather like in San Francisco?",
        "chat_history": [
            ChatMessage(role="USER", text="Hello, how are you?"),
            ChatMessage(role="ASSISTANT", text="I'm good, thank you!"),
        ],
    }


class GetCurrentWeatherWorkflow(BaseWorkflow):
    """
    A workflow that uses the GetCurrentWeatherNode.
    """

    graph = GetCurrentWeatherNode

    class Outputs(BaseWorkflow.Outputs):
        text = GetCurrentWeatherNode.Outputs.text
        chat_history = GetCurrentWeatherNode.Outputs.chat_history
