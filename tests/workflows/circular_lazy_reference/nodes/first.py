from vellum.workflows.nodes import BaseNode
from vellum.workflows.references.lazy import LazyReference


class FirstNode(BaseNode):
    second = LazyReference("SecondNode.Outputs.value")

    class Outputs(BaseNode.Outputs):
        value: str

    def run(self) -> Outputs:
        return "Hello " + self.second
