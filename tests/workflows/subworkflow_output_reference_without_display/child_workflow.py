from vellum.workflows import BaseWorkflow
from vellum.workflows.nodes import BaseNode
from vellum.workflows.outputs.base import BaseOutputs


class ChildNode(BaseNode):
    class Outputs(BaseOutputs):
        value: int

    def run(self) -> Outputs:
        return self.Outputs(value=42)


class ChildWorkflow(BaseWorkflow):
    graph = ChildNode

    class Outputs(BaseOutputs):
        result = ChildNode.Outputs.value
