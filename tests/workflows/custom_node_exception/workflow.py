from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.workflows.base import BaseWorkflow


class CustomNode(BaseNode):
    class Outputs(BaseNode.Outputs):
        err: str

    def run(self) -> Outputs:
        try:
            raise Exception("foo")
        except Exception as e:
            return self.Outputs(err=e)


class CustomNodeExceptionWorkflow(BaseWorkflow):
    """
    A workflow that demonstrates a custom node that catches an exception
    and returns it as an output.
    """

    graph = CustomNode

    class Outputs(BaseWorkflow.Outputs):
        error_message = CustomNode.Outputs.err
