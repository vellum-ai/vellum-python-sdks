from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.outputs.base import BaseOutputs

from ..inputs import ToolInputs


class TransformNode(BaseNode):
    text = ToolInputs.text

    class Outputs(BaseOutputs):
        result: str

    def run(self) -> Outputs:
        transformed = self.text[::-1].upper()
        return self.Outputs(result=transformed)
