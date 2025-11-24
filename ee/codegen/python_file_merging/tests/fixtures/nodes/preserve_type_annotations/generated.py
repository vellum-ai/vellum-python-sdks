from vellum.workflows.inputs import BaseInputs
from vellum.workflows.nodes import BaseNode


class MyCustomNode(BaseNode):
    arg1 = BaseInputs.test
    arg2 = 42
    arg3 = "no_annotation"

    class Outputs(BaseNode.Outputs):
        result: str

    def run(self) -> Outputs:
        return self.Outputs(result="hello")
