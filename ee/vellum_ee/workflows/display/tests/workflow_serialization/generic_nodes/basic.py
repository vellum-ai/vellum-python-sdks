from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases.base import BaseNode


class Inputs(BaseInputs):
    input: str


class BasicGenericNode(BaseNode):
    class Outputs(BaseNode.Outputs):
        output = Inputs.input
