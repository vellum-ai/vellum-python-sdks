import time
from typing import Iterator

from vellum.client.types.chat_message_prompt_block import ChatMessagePromptBlock
from vellum.client.types.plain_text_prompt_block import PlainTextPromptBlock
from vellum.client.types.rich_text_prompt_block import RichTextPromptBlock
from vellum.client.types.variable_prompt_block import VariablePromptBlock
from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.nodes.displayable.tool_calling_node import ToolCallingNode
from vellum.workflows.outputs.base import BaseOutput
from vellum.workflows.workflows.base import BaseWorkflow


def slow_tool_one() -> str:
    """A tool that takes 0.5 seconds to execute."""
    time.sleep(0.5)
    return "slow_tool_one_result"


def slow_tool_two() -> str:
    """A tool that takes 0.5 seconds to execute."""
    time.sleep(0.5)
    return "slow_tool_two_result"


class SlowToolThreeNode(BaseNode):
    """A node that takes 0.5 seconds to execute."""

    class Outputs(BaseNode.Outputs):
        result: str

    def run(self) -> Iterator[BaseOutput]:
        time.sleep(0.5)
        yield BaseOutput(name="result", value="slow_tool_three_result")


class SlowToolThreeWorkflow(BaseWorkflow):
    """A subworkflow that takes 0.5 seconds to execute."""

    graph = SlowToolThreeNode

    class Outputs(BaseWorkflow.Outputs):
        result = SlowToolThreeNode.Outputs.result


def slow_tool_four() -> str:
    """A tool that should NOT be called in the test."""
    raise AssertionError("slow_tool_four should not be called!")


class ToolCallingNodeParallelExecution(ToolCallingNode):
    """
    A tool calling node with three slow tools to test parallel execution.
    With parallel_tool_calls=True, should execute in parallel (~0.5s total).
    """

    ml_model = "gpt-4o-mini"
    blocks = [
        ChatMessagePromptBlock(
            chat_role="SYSTEM",
            blocks=[
                RichTextPromptBlock(
                    blocks=[
                        PlainTextPromptBlock(
                            text="You are a helpful assistant with access to slow tools.",
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
    functions = [slow_tool_one, slow_tool_two, SlowToolThreeWorkflow, slow_tool_four]
    prompt_inputs = {
        "question": "Execute all three slow tools and summarize the results.",
    }


class ToolCallingNodeParallelExecutionWorkflow(BaseWorkflow):
    """
    A workflow that uses ToolCallingNodeParallelExecution to test parallel tool execution.
    """

    graph = ToolCallingNodeParallelExecution

    class Outputs(BaseWorkflow.Outputs):
        text = ToolCallingNodeParallelExecution.Outputs.text
        chat_history = ToolCallingNodeParallelExecution.Outputs.chat_history
