from vellum.client.types.chat_message_prompt_block import ChatMessagePromptBlock
from vellum.client.types.code_execution_package import CodeExecutionPackage
from vellum.client.types.plain_text_prompt_block import PlainTextPromptBlock
from vellum.client.types.rich_text_prompt_block import RichTextPromptBlock
from vellum.client.types.variable_prompt_block import VariablePromptBlock
from vellum.workflows.nodes.experimental.tool_calling_node import ToolCallingNode
from vellum.workflows.state.base import BaseState
from vellum.workflows.workflows.base import BaseInputs, BaseWorkflow


def get_current_weather(location: str, unit: str) -> str:
    """
    Get the current weather in a given location.
    """
    return f"The current weather in {location} is sunny with a temperature of 70 degrees {unit}."


class Inputs(BaseInputs):
    query: str


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
    functions = [get_current_weather]
    # For testing purposes
    function_configs = {
        "get_current_weather": {
            "runtime": "PYTHON_3_11_6",
            "packages": [
                CodeExecutionPackage(
                    name="requests",
                    version="2.26.0",
                )
            ],
        },
    }
    prompt_inputs = {
        "question": Inputs.query,
    }


class BasicToolCallingNodeWorkflow(BaseWorkflow[Inputs, BaseState]):
    """
    A workflow that uses the GetCurrentWeatherNode.
    """

    graph = GetCurrentWeatherNode

    class Outputs(BaseWorkflow.Outputs):
        text = GetCurrentWeatherNode.Outputs.text
        chat_history = GetCurrentWeatherNode.Outputs.chat_history
