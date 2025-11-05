from typing import Generic

from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.types import MergeBehavior
from vellum.workflows.types.generics import StateType


class MergeNode(BaseNode[StateType], Generic[StateType]):
    """
    Used to merge the control flow of multiple nodes into a single node. This node exists to be backwards compatible
    with Vellum's Merge Node, and for most cases, you should extend from `BaseNode.Trigger` directly.
    """

    class Trigger(BaseNode.Trigger):
        merge_behavior = MergeBehavior.AWAIT_ANY
