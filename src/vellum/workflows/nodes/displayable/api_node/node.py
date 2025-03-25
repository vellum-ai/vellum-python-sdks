from typing import Optional, Union

from vellum.workflows.constants import AuthorizationType
from vellum.workflows.nodes.displayable.bases.api_node import BaseAPINode
from vellum.workflows.types.core import MergeBehavior, VellumSecret


class APINode(BaseAPINode):
    """
    Used to execute an API call. This node exists to be backwards compatible with Vellum's API Node, and for most cases,
    you should extend from `BaseAPINode` directly.

    url: str - The URL to send the request to.
    method: APIRequestMethod - The HTTP method to use for the request.
    data: Optional[str] - The data to send in the request body.
    json: Optional["JsonObject"] - The JSON data to send in the request body.
    headers: Optional[Dict[str, Union[str, VellumSecret]]] - The headers to send in the request.

    authorization_type: Optional[AuthorizationType] = None - The type of authorization to use for the API call.
    api_key_header_key: Optional[str] = None - The header key to use for the API key authorization.
    bearer_token_value: Optional[Union[str, VellumSecretReference]] = None - The bearer token value to use
    for the bearer token authorization.
    """

    authorization_type: Optional[AuthorizationType] = None
    api_key_header_key: Optional[str] = None
    api_key_header_value: Optional[Union[str, VellumSecret]] = None
    bearer_token_value: Optional[Union[str, VellumSecret]] = None

    class Trigger(BaseAPINode.Trigger):
        merge_behavior = MergeBehavior.AWAIT_ANY

    def run(self) -> BaseAPINode.Outputs:
        headers = self.headers or {}
        header_overrides = {}
        bearer_token = None

        if (
            self.authorization_type == AuthorizationType.API_KEY
            and self.api_key_header_key
            and self.api_key_header_value
        ):
            header_overrides[self.api_key_header_key] = self.api_key_header_value
        elif self.authorization_type == AuthorizationType.BEARER_TOKEN and isinstance(self.bearer_token_value, str):
            header_overrides["Authorization"] = f"Bearer {self.bearer_token_value}"
        elif self.authorization_type == AuthorizationType.BEARER_TOKEN and isinstance(
            self.bearer_token_value, VellumSecret
        ):
            bearer_token = self.bearer_token_value
        return self._run(
            method=self.method,
            url=self.url,
            data=self.data,
            json=self.json,
            headers={**headers, **header_overrides},
            bearer_token=bearer_token,
        )
