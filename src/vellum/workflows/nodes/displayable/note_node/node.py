from typing import Generic

from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.types import MergeBehavior
from vellum.workflows.types.generics import StateType


class NoteNode(BaseNode[StateType], Generic[StateType]):
    """
    A no-op Node purely used to display a note in the Vellum UI.
    """

    class Trigger(BaseNode.Trigger):
        merge_behavior = MergeBehavior.AWAIT_ANY

    def run(self) -> BaseNode.Outputs:
        raise RuntimeError("NoteNode should never be run")
