from vellum.workflows.nodes.bases.base import BaseNode


class DummyNode(BaseNode):
    class Outputs:
        text = "dummy"
