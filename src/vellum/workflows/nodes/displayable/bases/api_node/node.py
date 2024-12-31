from typing import Any, Dict, Generic, Optional, Union

from requests import Request, RequestException, Session
from requests.exceptions import JSONDecodeError

from vellum.workflows.constants import APIRequestMethod
from vellum.workflows.errors.types import WorkflowErrorCode
from vellum.workflows.exceptions import NodeException
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.outputs import BaseOutputs
from vellum.workflows.types.core import Json, VellumSecret
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

    url: str
    method: APIRequestMethod
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
        method: APIRequestMethod,
        url: str,
        data: Optional[str] = None,
        json: Any = None,
        headers: Any = None,
    ) -> Outputs:
        try:
            prepped = Request(method=method.value, url=url, data=data, json=json, headers=headers).prepare()
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
