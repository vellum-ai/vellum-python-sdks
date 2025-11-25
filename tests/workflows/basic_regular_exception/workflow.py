from vellum.client import ApiError
from vellum.workflows import BaseWorkflow
from vellum.workflows.nodes.bases import BaseNode


class RegularExceptionNode(BaseNode):
    class Outputs(BaseNode.Outputs):
        pass

    def run(self) -> Outputs:
        raise ApiError(status_code=500, body="Regular exception occurred")


class BasicRegularExceptionWorkflow(BaseWorkflow):
    graph = RegularExceptionNode
