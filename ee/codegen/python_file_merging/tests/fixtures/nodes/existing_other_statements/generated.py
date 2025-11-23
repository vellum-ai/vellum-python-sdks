from vellum.workflows import BaseNode


class MyCustomNode(BaseNode):
    class Outputs(BaseNode.Outputs):
        value: str

    def run(self) -> Outputs:
        return self.Outputs(value="hello")
