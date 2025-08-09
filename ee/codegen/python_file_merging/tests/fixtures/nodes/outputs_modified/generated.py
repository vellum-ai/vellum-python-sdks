from vellum.workflows.nodes import BaseNode


class MyCustomNode(BaseNode):
    class Outputs(BaseNode.Outputs):
        new_value: str

    def run(self) -> Outputs:
        return self.Outputs(value="hello")
