from vellum.workflows.nodes.bases import BaseNode

from ..inputs import Inputs


class SimpleNode(BaseNode):
    class Outputs(BaseNode.Outputs):
        result = Inputs.message
