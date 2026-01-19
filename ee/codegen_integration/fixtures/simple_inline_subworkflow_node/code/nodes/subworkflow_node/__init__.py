from vellum.workflows.nodes.displayable import InlineSubworkflowNode

from .workflow import SubworkflowNodeWorkflow


class SubworkflowNode(InlineSubworkflowNode):
    subworkflow = SubworkflowNodeWorkflow

    class Display(InlineSubworkflowNode.Display):
        x = 1991.684833859175
        y = 178.94753425793772
