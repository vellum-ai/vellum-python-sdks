from vellum.workflows.nodes import BaseNode


class MyCustomNode(BaseNode):
    class Outputs(BaseNode.Outputs):
        pass

    def run(self) -> Outputs:
        pass
