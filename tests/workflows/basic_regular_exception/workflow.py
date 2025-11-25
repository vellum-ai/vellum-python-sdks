from vellum.workflows import BaseWorkflow
from vellum.workflows.nodes.bases import BaseNode


class RegularExceptionNode(BaseNode):
    class Outputs(BaseNode.Outputs):
        pass

    def run(self) -> Outputs:
        raise Exception("Regular exception occurred")


class BasicRegularExceptionWorkflow(BaseWorkflow):
    graph = RegularExceptionNode
