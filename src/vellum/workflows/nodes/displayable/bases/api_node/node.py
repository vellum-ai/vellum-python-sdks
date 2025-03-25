from typing import Any, Dict, Generic, Optional, Union

from requests import Request, RequestException, Session
from requests.exceptions import JSONDecodeError

from vellum.client import ApiError
from vellum.client.types.vellum_secret import VellumSecret as ClientVellumSecret
from vellum.workflows.constants import APIRequestMethod
from vellum.workflows.errors.types import WorkflowErrorCode
from vellum.workflows.exceptions import NodeException
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.outputs import BaseOutputs
from vellum.workflows.types.core import Json, MergeBehavior, VellumSecret
from vellum.workflows.types.generics import StateType


class BaseAPINode(BaseNode, Generic[StateType]):
    """
    Used to execute an API call.

    url: str - The URL to send the request to.
    method: APIRequestMethod - The HTTP method to use for the request.
    data: Optional[str] - The data to send in the request body.
    json: Optional["JsonObject"] - The JSON data to send in the request body.
    headers: Optional[Dict[str, Union[str, VellumSecret]]] - The headers to send in the request.
    """

    class Trigger(BaseNode.Trigger):
        merge_behavior = MergeBehavior.AWAIT_ANY

    url: str = ""
    method: Optional[APIRequestMethod] = APIRequestMethod.GET
    data: Optional[str] = None
    json: Optional[Json] = None
    headers: Optional[Dict[str, Union[str, VellumSecret]]] = None

    class Outputs(BaseOutputs):
        json: Optional[Json]
        headers: Dict[str, str]
        status_code: int
        text: str

    def run(self) -> Outputs:
        return self._run(method=self.method, url=self.url, data=self.data, json=self.json, headers=self.headers)

    def _run(
        self,
        url: str,
        method: Optional[APIRequestMethod] = APIRequestMethod.GET,
        data: Optional[Union[str, Any]] = None,
        json: Any = None,
        headers: Any = None,
        bearer_token: Optional[VellumSecret] = None,
    ) -> Outputs:
        vellum_instance = False
        for header in headers or {}:
            if isinstance(headers[header], VellumSecret):
                vellum_instance = True
        if vellum_instance or bearer_token:
            return self._vellum_execute_api(bearer_token, json, headers, method, url)
        else:
            return self._local_execute_api(data, headers, json, method, url)

    def _local_execute_api(self, data, headers, json, method, url):
        try:
            if data is not None:
                prepped = Request(method=method.value, url=url, data=data, headers=headers).prepare()
            elif json is not None:
                prepped = Request(method=method.value, url=url, json=json, headers=headers).prepare()
            else:
                prepped = Request(method=method.value, url=url, headers=headers).prepare()
        except Exception as e:
            raise NodeException(f"Failed to prepare HTTP request: {e}", code=WorkflowErrorCode.PROVIDER_ERROR)
        try:
            with Session() as session:
                response = session.send(prepped)
        except RequestException as e:
            raise NodeException(f"HTTP request failed: {e}", code=WorkflowErrorCode.PROVIDER_ERROR)
        try:
            json = response.json()
        except JSONDecodeError:
            json = None
        return self.Outputs(
            json=json,
            headers={header: value for header, value in response.headers.items()},
            status_code=response.status_code,
            text=response.text,
        )

    def _vellum_execute_api(self, bearer_token, data, headers, method, url):
        client_vellum_secret = ClientVellumSecret(name=bearer_token.name) if bearer_token else None
        try:
            vellum_response = self._context.vellum_client.execute_api(
                url=url, method=method.value, body=data, headers=headers, bearer_token=client_vellum_secret
            )
        except ApiError as e:
            raise NodeException(f"Failed to prepare HTTP request: {e}", code=WorkflowErrorCode.NODE_EXECUTION)

        return self.Outputs(
            json=vellum_response.json_,
            headers={header: value for header, value in vellum_response.headers.items()},
            status_code=vellum_response.status_code,
            text=vellum_response.text,
        )
