from vellum.workflows.nodes.displayable import FinalOutputNode

from ..inputs import Inputs


class FinalOutput(FinalOutputNode[str]):
    class Outputs(FinalOutputNode.Outputs):
        value = Inputs.test
