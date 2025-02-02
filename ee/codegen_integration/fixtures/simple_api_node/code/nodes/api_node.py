from vellum.workflows.constants import APIRequestMethod, AuthorizationType
from vellum.workflows.nodes.displayable import APINode


class ApiNode(APINode):
    """This is my API Node"""

    url = "https://www.testing.com"
    method = APIRequestMethod.POST
    json = '"hii"'
    headers = {
        "test": "test-value",
        "nom": "nom-value",
    }
    api_key_header_key = "nice-key"
    authorization_type = AuthorizationType.API_KEY
    api_key_header_value = None
    bearer_token_value = None
