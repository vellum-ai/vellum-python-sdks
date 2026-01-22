from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.outputs.base import BaseOutputs

from ..inputs import Inputs


class TransformNode(BaseNode):
    text = Inputs.text

    class Outputs(BaseOutputs):
        result: str

    def run(self) -> Outputs:
        transformed = self.text[::-1].upper()
        return self.Outputs(result=transformed)
