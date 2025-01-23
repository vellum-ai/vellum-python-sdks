from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.types import MergeBehavior


class NoteNode(BaseNode):
    """
    A no-op Node purely used to display a note in the Vellum UI.
    """

    class Trigger(BaseNode.Trigger):
        merge_behavior = MergeBehavior.AWAIT_ANY

    def run(self) -> BaseNode.Outputs:
        raise RuntimeError("NoteNode should never be run")
