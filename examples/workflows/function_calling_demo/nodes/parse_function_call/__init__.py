from vellum.workflows.nodes.displayable import InlineSubworkflowNode

from .workflow import ParseFunctionCallWorkflow


class ParseFunctionCall(InlineSubworkflowNode):
    subworkflow = ParseFunctionCallWorkflow
