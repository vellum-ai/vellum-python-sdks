from vellum.workflows.nodes import BaseNode
from vellum.workflows.references.lazy import LazyReference


class FirstNode(BaseNode):
    second = LazyReference[str]("SecondNode.Outputs.value").coalesce("Start")

    class Outputs(BaseNode.Outputs):
        value: str

    def run(self) -> Outputs:
        return self.Outputs(value="Hello " + self.second)
