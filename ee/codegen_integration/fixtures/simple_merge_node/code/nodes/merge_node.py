from vellum.workflows.nodes.displayable import MergeNode as BaseMergeNode
from vellum.workflows.types import MergeBehavior


class MergeNode(BaseMergeNode):
    class Trigger(BaseMergeNode.Trigger):
        merge_behavior = MergeBehavior.AWAIT_ALL

    class Display(BaseMergeNode.Display):
        x = 2374.2549861495845
        y = 205.20096952908594
