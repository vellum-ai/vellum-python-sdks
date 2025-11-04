from vellum.workflows.nodes.bases.base import BaseNode


class DummyNode(BaseNode):
    __legacy_id__ = True

    class Outputs:
        text = "dummy"
