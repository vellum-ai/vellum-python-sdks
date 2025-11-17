import threading
import time

from vellum.workflows import BaseWorkflow
from vellum.workflows.errors.types import WorkflowErrorCode
from vellum.workflows.exceptions import NodeException
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.nodes.core.inline_subworkflow_node.node import InlineSubworkflowNode


class FastFailingNode(BaseNode):
    """Node that sleeps for 0.01s before raising an error."""

    class Outputs(BaseNode.Outputs):
        value: str

    def run(self) -> Outputs:
        time.sleep(0.1)
        raise NodeException(code=WorkflowErrorCode.USER_DEFINED_ERROR, message="Fast node failed")


class SlowNode(BaseNode):
    """Node that sleeps for 0.5s."""

    class Outputs(BaseNode.Outputs):
        value: str

    def run(self) -> Outputs:
        self._cancelled = threading.Event()
        if self._cancelled.wait(timeout=0.5):
            raise NodeException(code=WorkflowErrorCode.NODE_CANCELLED, message="Slow node cancelled")

        return self.Outputs(value="slow complete")

    def __cancel__(self, message: str) -> None:
        self._cancelled.set()


class SlowSubworkflow(BaseWorkflow):
    """Subworkflow containing a slow node."""

    graph = SlowNode

    class Outputs(BaseWorkflow.Outputs):
        value = SlowNode.Outputs.value


class SlowInlineSubworkflowNode(InlineSubworkflowNode):
    """Inline subworkflow node wrapping the slow subworkflow."""

    subworkflow = SlowSubworkflow


class ParallelInlineSubworkflowCancellationWorkflow(BaseWorkflow):
    """Workflow with a fast failing node and a slow inline subworkflow running in parallel."""

    graph = {FastFailingNode, SlowInlineSubworkflowNode}
