from vellum.workflows.nodes.displayable import MergeNode as BaseMergeNode
from vellum.workflows.types import MergeBehavior


class MergeNode(BaseMergeNode):
    class Trigger(BaseMergeNode.Trigger):
        merge_behavior = MergeBehavior.AWAIT_ALL
