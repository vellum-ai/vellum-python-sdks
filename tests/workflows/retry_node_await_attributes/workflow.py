import time

from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.nodes.core.retry_node import RetryNode
from vellum.workflows.state.base import BaseState
from vellum.workflows.types.core import MergeBehavior


class SlowNode(BaseNode):
    def run(self) -> BaseNode.Outputs:
        # Sleep for 1 second
        time.sleep(1.0)
        return self.Outputs()


class FastNode(BaseNode):
    pass


@RetryNode.wrap(max_attempts=1)
class RetryWrappedPromptNode(BaseNode):
    class Trigger(BaseNode.Trigger):
        merge_behavior = MergeBehavior.AWAIT_ALL

    def run(self) -> BaseNode.Outputs:
        print("returning from retry wrapped prompt node")
        return self.Outputs()


class RetryWrappedAwaitAttributesWorkflow(BaseWorkflow[BaseInputs, BaseState]):
    """Workflow that tests if RetryNode-wrapped node properly respects AWAIT_ALL merge behavior."""

    graph = {SlowNode, FastNode} >> RetryWrappedPromptNode

    class Outputs(BaseWorkflow.Outputs):
        slow_execution_count = SlowNode.Execution.count
        fast_execution_count = FastNode.Execution.count
        prompt_execution_count = RetryWrappedPromptNode.Execution.count
