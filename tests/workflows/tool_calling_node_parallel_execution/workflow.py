import time
from typing import Iterator, List

from vellum import ChatMessage
from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs import BaseInputs
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.nodes.displayable.tool_calling_node import ToolCallingNode
from vellum.workflows.outputs.base import BaseOutput
from vellum.workflows.state import BaseState


def slow_tool_one() -> str:
    """A slow tool that takes 0.25 seconds to execute."""
    time.sleep(0.25)
    return "Tool one result"


def slow_tool_two() -> str:
    """A slow tool that takes 0.25 seconds to execute."""
    time.sleep(0.25)
    return "Tool two result"


class SlowToolThreeNode(BaseNode):
    """A node that takes 0.25 seconds to execute."""

    class Outputs(BaseNode.Outputs):
        result: str

    def run(self) -> Iterator[BaseOutput]:
        time.sleep(0.25)
        yield BaseOutput(name="result", value="Tool three workflow result")


class SlowToolThreeWorkflow(BaseWorkflow):
    """A workflow tool that takes 0.25 seconds to execute."""

    graph = SlowToolThreeNode

    class Outputs(BaseWorkflow.Outputs):
        result: str = SlowToolThreeNode.Outputs.result


def slow_tool_four() -> str:
    """A slow tool that should NOT be called in the test."""
    time.sleep(0.25)
    return "Tool four result - should not be called"


class ParallelToolCallingNode(ToolCallingNode):
    """Tool calling node with parallel execution enabled."""

    ml_model = "gpt-4o-mini"
    blocks = [
        {
            "block_type": "JINJA",
            "template": "You are a helpful assistant. Call the tools as requested.",
        },
    ]
    functions = [slow_tool_one, slow_tool_two, SlowToolThreeWorkflow, slow_tool_four]
    parallel_tool_calls = True


class ParallelToolCallingWorkflow(BaseWorkflow[BaseInputs, BaseState]):
    """Workflow that uses parallel tool calling."""

    graph = ParallelToolCallingNode

    class Outputs(BaseWorkflow.Outputs):
        text: str = ParallelToolCallingNode.Outputs.text
        chat_history: List[ChatMessage] = ParallelToolCallingNode.Outputs.chat_history
