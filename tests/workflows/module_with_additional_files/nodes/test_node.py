from vellum.workflows.nodes import BaseNode


class TestNode(BaseNode):
    class Outputs(BaseNode.Outputs):
        value: str

    def run(self) -> Outputs:
        return self.Outputs(value="test")
