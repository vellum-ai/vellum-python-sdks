from vellum.workflows.constants import AuthorizationType
from vellum.workflows.nodes.displayable import APINode as BaseAPINode
from vellum.workflows.references import VellumSecretReference

from .templating_node_15 import TemplatingNode15


class APINode(BaseAPINode):
    url = TemplatingNode15.Outputs.result
    api_key_header_key = "ab2f59-1004d1"
    authorization_type = AuthorizationType.API_KEY
    api_key_header_value = VellumSecretReference("TEST_SECRET")
    bearer_token_value = ""
