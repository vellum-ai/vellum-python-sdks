from vellum.workflows.inputs import BaseInputs
from vellum.workflows.nodes import BaseNode


class MyCustomNode(BaseNode):
    arg1: str = BaseInputs.test
    arg2: int = 42
    arg3 = "no_annotation"
    _private_attr: str = "keep_this"

    class Outputs(BaseNode.Outputs):
        result: str

    def run(self) -> Outputs:
        return self.Outputs(result="hello")
