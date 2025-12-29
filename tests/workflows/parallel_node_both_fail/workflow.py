import time

from vellum.workflows import BaseWorkflow
from vellum.workflows.errors.types import WorkflowErrorCode
from vellum.workflows.exceptions import NodeException
from vellum.workflows.nodes.bases import BaseNode


class LeftNode(BaseNode):
    class Outputs(BaseNode.Outputs):
        value: str

    def run(self) -> Outputs:
        time.sleep(0.1)
        raise NodeException(code=WorkflowErrorCode.INTERNAL_ERROR, message="Left node failed")


class RightNode(BaseNode):
    class Outputs(BaseNode.Outputs):
        value: str

    def run(self) -> Outputs:
        time.sleep(0.1)
        raise NodeException(code=WorkflowErrorCode.INTERNAL_ERROR, message="Right node failed")


class ParallelNodeBothFailWorkflow(BaseWorkflow):
    graph = {LeftNode, RightNode}

    class Outputs(BaseWorkflow.Outputs):
        left_value = LeftNode.Outputs.value
        right_value = RightNode.Outputs.value
