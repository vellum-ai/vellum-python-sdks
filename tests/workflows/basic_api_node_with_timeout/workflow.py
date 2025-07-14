from vellum.workflows import BaseWorkflow
from vellum.workflows.constants import APIRequestMethod
from vellum.workflows.nodes.displayable import APINode


class APINodeWithTimeout(APINode):
    method = APIRequestMethod.POST
    url = "https://api.vellum.ai"
    timeout = 30
    json = {
        "key": "value",
    }


class APINodeWithTimeoutWorkflow(BaseWorkflow):
    graph = APINodeWithTimeout

    class Outputs(BaseWorkflow.Outputs):
        json = APINodeWithTimeout.Outputs.json
        status_code = APINodeWithTimeout.Outputs.status_code
        text = APINodeWithTimeout.Outputs.text


class APINodeWithoutTimeout(APINode):
    method = APIRequestMethod.GET
    url = "https://api.vellum.ai"
    # No timeout attribute - should use default behavior


class APINodeWithoutTimeoutWorkflow(BaseWorkflow):
    graph = APINodeWithoutTimeout

    class Outputs(BaseWorkflow.Outputs):
        json = APINodeWithoutTimeout.Outputs.json
        status_code = APINodeWithoutTimeout.Outputs.status_code
        text = APINodeWithoutTimeout.Outputs.text
