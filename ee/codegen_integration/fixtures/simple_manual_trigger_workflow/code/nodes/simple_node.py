from vellum.workflows.nodes.bases import BaseNode

from ..inputs import Inputs


class SimpleNode(BaseNode):
    __legacy_id__ = True

    class Outputs(BaseNode.Outputs):
        result = Inputs.message
