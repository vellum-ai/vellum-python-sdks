from vellum.client.types.chat_message_prompt_block import ChatMessagePromptBlock
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


def format_answer(answer: str) -> str:
    return f"The answer is {answer}"


class GetCurrentWeatherNode(ToolCallingNode):
    """
    A tool calling node that calls the get_current_weather and format_answer functions.
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
    functions = [get_current_weather, format_answer]
    prompt_inputs = {
        "question": "What's the weather like in San Francisco?",
    }


class BasicToolCallingNodeMultiToolWorkflow(BaseWorkflow):
    """
    A workflow that uses the GetCurrentWeatherNode.
    """

    graph = GetCurrentWeatherNode

    class Outputs(BaseWorkflow.Outputs):
        text = GetCurrentWeatherNode.Outputs.text
        chat_history = GetCurrentWeatherNode.Outputs.chat_history
