from vellum.workflows.constants import APIRequestMethod, AuthorizationType
from vellum.workflows.nodes.displayable import APINode
from vellum.workflows.references import VellumSecretReference


class ApiNode(APINode):
    """This is my API Node"""

    url = "https://www.testing.com"
    method = APIRequestMethod.POST
    json = '"hii"'
    headers = {
        "test": VellumSecretReference("cecd16a2-4de5-444d-acff-37a5c400600c"),
        "nom": VellumSecretReference("cecd16a2-4de5-444d-acff-37a5c400600c"),
    }
    api_key_header_key = "nice-key"
    authorization_type = AuthorizationType.API_KEY
    api_key_header_value = None
    bearer_token_value = None
