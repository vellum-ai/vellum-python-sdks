from vellum.workflows import BaseNode

from ..inputs import Inputs


class TransformNode(BaseNode):
    text = Inputs.text

    class Outputs(BaseNode.Outputs):
        result: str

    class Display(BaseNode.Display):
        x = 200
        y = -50

    def run(self) -> Outputs:
        transformed = self.text[::-1].upper()
        return self.Outputs(result=transformed)
