from vellum.workflows import BaseWorkflow
from vellum.workflows.nodes.bases import BaseNode


class InputNode(BaseNode):
    class ExternalInputs(BaseNode.ExternalInputs):
        message: str


class BasicInputNodeWorkflow(BaseWorkflow):
    """
    This Workflow has two nodes that accept `ExternalInputs` of the same shape to ensure that they
    could each receive external data separately.
    """

    graph = InputNode

    class Outputs(BaseWorkflow.Outputs):
        final_value = InputNode.ExternalInputs.message
