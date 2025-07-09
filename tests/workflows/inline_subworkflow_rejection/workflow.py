from vellum.workflows import BaseWorkflow
from vellum.workflows.errors.types import WorkflowErrorCode
from vellum.workflows.exceptions import NodeException
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.nodes.core.inline_subworkflow_node.node import InlineSubworkflowNode


class FailingNode(BaseNode):
    class Outputs(BaseNode.Outputs):
        pass

    def run(self) -> Outputs:
        raise NodeException(code=WorkflowErrorCode.USER_DEFINED_ERROR, message="Subworkflow node intentionally failed")


class FailingSubworkflow(BaseWorkflow):
    graph = FailingNode


class InlineSubworkflowRejectionNode(InlineSubworkflowNode):
    subworkflow = FailingSubworkflow


class InlineSubworkflowRejectionWorkflow(BaseWorkflow):
    graph = InlineSubworkflowRejectionNode
