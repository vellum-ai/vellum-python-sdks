from vellum.workflows import BaseWorkflow
from vellum.workflows.constants import APIRequestMethod, AuthorizationType
from vellum.workflows.nodes.displayable import APINode
from vellum.workflows.references.vellum_secret import VellumSecretReference


class SimpleAPINode(APINode):
    method = APIRequestMethod.POST
    url = "https://api.vellum.ai"
    authorization_type = AuthorizationType.API_KEY
    api_key_header_key = "CUSTOM_API_KEY"
    api_key_header_value = VellumSecretReference("MY_SECRET")
    body = {
        "key": "value",
    }
    headers = {
        "additional_header": "additional header value",
    }


class SimpleAPIWorkflow(BaseWorkflow):
    graph = SimpleAPINode

    class Outputs(BaseWorkflow.Outputs):
        json = SimpleAPINode.Outputs.json
        headers = SimpleAPINode.Outputs.headers
        status_code = SimpleAPINode.Outputs.status_code
