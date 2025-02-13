from vellum.workflows.nodes.displayable import InlineSubworkflowNode

from .workflow import SubworkflowNodeWorkflow


class SubworkflowNode(InlineSubworkflowNode):
    subworkflow = SubworkflowNodeWorkflow
