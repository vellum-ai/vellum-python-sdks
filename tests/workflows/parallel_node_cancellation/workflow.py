import time

from vellum.workflows import BaseWorkflow
from vellum.workflows.errors.types import WorkflowErrorCode
from vellum.workflows.exceptions import NodeException
from vellum.workflows.nodes.bases import BaseNode


class TopNode(BaseNode):
    class Outputs(BaseNode.Outputs):
        value: str

    def run(self) -> Outputs:
        time.sleep(0.1)
        raise NodeException(code=WorkflowErrorCode.USER_DEFINED_ERROR, message="Top node failed")


class BottomNode(BaseNode):
    class Outputs(BaseNode.Outputs):
        value: str

    def run(self) -> Outputs:
        time.sleep(0.5)
        return self.Outputs(value="bottom complete")


class ParallelNodeCancellationWorkflow(BaseWorkflow):
    graph = {TopNode, BottomNode}

    class Outputs(BaseWorkflow.Outputs):
        pass
