import random

from vellum.workflows import BaseWorkflow
from vellum.workflows.errors.types import WorkflowErrorCode
from vellum.workflows.exceptions import NodeException
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.nodes.core.try_node.node import TryNode


@TryNode.wrap()
class StartNode(BaseNode):
    __legacy_id__ = True

    class Outputs(BaseNode.Outputs):
        value: int

    def run(self) -> Outputs:
        arg = random.randint(0, 10)
        if arg < 5:
            raise NodeException(message="This is a flaky node", code=WorkflowErrorCode.NODE_EXECUTION)
        return self.Outputs(value=arg)


class SimpleTryExample(BaseWorkflow):
    graph = StartNode

    class Outputs(BaseWorkflow.Outputs):
        final_value = StartNode.Outputs.value
        error = StartNode.Outputs.error


class StandaloneStartNode(BaseNode):
    class Outputs(BaseNode.Outputs):
        value: int

    def run(self) -> Outputs:
        arg = random.randint(0, 10)
        if arg < 5:
            raise Exception("This is a flaky node")
        return self.Outputs(value=arg)


class StandaloneSubworkflow(BaseWorkflow):
    graph = StandaloneStartNode

    class Outputs(StandaloneStartNode.Outputs):
        pass


class StandaloneTryableNode(TryNode):
    subworkflow = StandaloneSubworkflow


class StandaloneTryExample(BaseWorkflow):
    graph = StandaloneTryableNode

    class Outputs(BaseWorkflow.Outputs):
        final_value = StandaloneTryableNode.Outputs.value
        error = StandaloneTryableNode.Outputs.error
