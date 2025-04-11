"""
Basic Tool Calling Node Example

This module demonstrates how to use the new ToolCallingNode in a workflow.

To run the tests with a timeout (to prevent hangs), use:
    poetry run pytest -xvs tests/workflows/basic_tool_calling_node/tests/test_workflow.py --timeout=30
"""

from vellum.client.types.chat_message_prompt_block import ChatMessagePromptBlock
from vellum.client.types.function_definition import FunctionDefinition
from vellum.client.types.plain_text_prompt_block import PlainTextPromptBlock
from vellum.client.types.rich_text_prompt_block import RichTextPromptBlock
from vellum.client.types.variable_prompt_block import VariablePromptBlock
from vellum.workflows.nodes.experimental.tool_calling_node import ToolCallingNode
from vellum.workflows.workflows.base import BaseWorkflow


# A simple tool definition
def get_current_weather():
    """
    Get the current weather in a given location.
    """
    return {
        "name": "get_current_weather",
        "description": "Get the current weather in a given location",
        "parameters": {
            "type": "object",
            "properties": {"location": {"type": "string", "description": "The city and state, e.g. San Francisco, CA"}},
            "required": ["location"],
        },
    }


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
    function_callables = [get_current_weather]
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
    }


class GetCurrentWeatherWorkflow(BaseWorkflow):
    """
    A workflow that uses the GetCurrentWeatherNode.
    """

    graph = GetCurrentWeatherNode

    class Outputs(BaseWorkflow.Outputs):
        text = GetCurrentWeatherNode.Outputs.text
        chat_history = GetCurrentWeatherNode.Outputs.chat_history
