from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.outputs.base import BaseOutputs

from ..inputs import ToolInputs


class TransformNode(BaseNode):
    """
    A custom node with a custom run method that transforms text.
    This is the key component being tested for zero-diff preservation.
    """

    text = ToolInputs.text

    class Outputs(BaseOutputs):
        result: str

    def run(self) -> Outputs:
        # Custom run method that transforms text by reversing and uppercasing
        # This implementation must be preserved through the codegen -> serialization -> codegen cycle
        transformed = self.text[::-1].upper()
        return self.Outputs(result=transformed)
