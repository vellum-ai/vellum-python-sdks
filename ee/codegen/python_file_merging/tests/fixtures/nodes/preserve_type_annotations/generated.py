from vellum.workflows import BaseNode

from ..inputs import Inputs


class MyCustomNode(BaseNode):
    arg1 = Inputs.test
    arg2 = 42
    arg3 = "no_annotation"

    class Outputs(BaseNode.Outputs):
        result: str

    def run(self) -> Outputs:
        return self.Outputs(result="hello")
