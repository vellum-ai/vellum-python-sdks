from vellum.client.types.chat_message_prompt_block import ChatMessagePromptBlock
from vellum.client.types.plain_text_prompt_block import PlainTextPromptBlock
from vellum.client.types.rich_text_prompt_block import RichTextPromptBlock
from vellum.client.types.variable_prompt_block import VariablePromptBlock
from vellum.workflows.nodes.displayable.tool_calling_node import ToolCallingNode
from vellum.workflows.workflows.base import BaseWorkflow


def add_numbers(a: int, b: int) -> int:
    return a + b


def multiply_numbers(a: int, b: int) -> int:
    return a * b


class BasicToolCallingNodeMaxPromptIterations(ToolCallingNode):
    ml_model = "gpt-4o-mini"
    blocks = [
        ChatMessagePromptBlock(
            chat_role="SYSTEM",
            blocks=[
                RichTextPromptBlock(
                    blocks=[
                        PlainTextPromptBlock(
                            text="You are a math assistant. Use the tools to solve math problems.",
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
    functions = [add_numbers, multiply_numbers]
    prompt_inputs = {
        "question": "What is 5 + 3 and then multiply the result by 2?",
    }
    max_prompt_iterations = 1  # Allow exactly 1 prompt iteration


class BasicToolCallingNodeMaxPromptIterationsWorkflow(BaseWorkflow):
    graph = BasicToolCallingNodeMaxPromptIterations

    class Outputs(BaseWorkflow.Outputs):
        text = BasicToolCallingNodeMaxPromptIterations.Outputs.text
        chat_history = BasicToolCallingNodeMaxPromptIterations.Outputs.chat_history
