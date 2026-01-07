from vellum.workflows.nodes.displayable import InlineSubworkflowNode

from .workflow import MyNodeWorkflow


class MySubworkflowNode(InlineSubworkflowNode):
    """An inline subworkflow node."""

    subworkflow = MyNodeWorkflow

    class Display(InlineSubworkflowNode.Display):
        icon = "vellum:icon:diagram-sankey"
        color = "grass"
