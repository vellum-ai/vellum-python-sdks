from vellum.workflows.nodes import BaseNode

from tests.workflows.circular_lazy_reference.nodes.first import FirstNode


class SecondNode(BaseNode):
    first = FirstNode.Outputs.value

    class Outputs(BaseNode.Outputs):
        value: str

    def run(self) -> Outputs:
        return self.Outputs(value="World " + self.first)
