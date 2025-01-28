from vellum.workflows import BaseWorkflow
from vellum.workflows.nodes.bases import BaseNode


class InputNode(BaseNode):
    class ExternalInputs(BaseNode.ExternalInputs):
        message: str


class BasicInputNodeWorkflow(BaseWorkflow):
    """
    This Workflow has a single node that defines an `ExternalInputs` to ensure that it
    could receive external data as the first node.
    """

    graph = InputNode

    class Outputs(BaseWorkflow.Outputs):
        final_value = InputNode.ExternalInputs.message
