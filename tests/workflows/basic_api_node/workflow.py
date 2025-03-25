from vellum.workflows import BaseWorkflow
from vellum.workflows.constants import APIRequestMethod
from vellum.workflows.nodes import APINode


class SimpleBaseAPINode(APINode):
    method = APIRequestMethod.POST
    url = "https://api.vellum.ai"
    json = {
        "key": "value",
    }
    headers = {
        "X-Test-Header": "foo",
    }


class SimpleAPIWorkflow(BaseWorkflow):
    graph = SimpleBaseAPINode

    class Outputs(BaseWorkflow.Outputs):
        json = SimpleBaseAPINode.Outputs.json
        headers = SimpleBaseAPINode.Outputs.headers
        status_code = SimpleBaseAPINode.Outputs.status_code
