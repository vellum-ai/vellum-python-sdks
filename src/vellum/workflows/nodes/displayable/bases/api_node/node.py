import base64
import hashlib
import hmac
import time
from typing import Any, Dict, Generic, Optional, Union

from requests import Request, RequestException, Session
from requests.exceptions import JSONDecodeError

from vellum.client import ApiError
from vellum.client.core.request_options import RequestOptions
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
    timeout: Optional[int] - The timeout in seconds for the API request.
    """

    class Trigger(BaseNode.Trigger):
        merge_behavior = MergeBehavior.AWAIT_ANY

    url: str = ""
    method: Optional[APIRequestMethod] = APIRequestMethod.GET
    data: Optional[str] = None
    json: Optional[Json] = None
    headers: Optional[Dict[str, Union[str, VellumSecret]]] = None
    timeout: Optional[int] = None

    class Outputs(BaseOutputs):
        json: Optional[Json]
        headers: Dict[str, str]
        status_code: int
        text: str

    def _validate(self) -> None:
        if not self.url or not isinstance(self.url, str) or not self.url.strip():
            raise NodeException("URL is required and must be a non-empty string", code=WorkflowErrorCode.INVALID_INPUTS)

    def run(self) -> Outputs:
        return self._run(
            method=self.method, url=self.url, data=self.data, json=self.json, headers=self.headers, timeout=self.timeout
        )

    def _run(
        self,
        url: str,
        method: Optional[APIRequestMethod] = APIRequestMethod.GET,
        data: Optional[Union[str, Any]] = None,
        json: Any = None,
        headers: Any = None,
        bearer_token: Optional[VellumSecret] = None,
        timeout: Optional[int] = None,
    ) -> Outputs:
        self._validate()

        vellum_instance = False
        for header in headers or {}:
            if isinstance(headers[header], VellumSecret):
                vellum_instance = True
        if vellum_instance or bearer_token:
            return self._vellum_execute_api(bearer_token, json, headers, method, url, timeout)
        else:
            return self._local_execute_api(data, headers, json, method, url, timeout)

    def _local_execute_api(self, data, headers, json, method, url, timeout):
        try:
            if data is not None:
                prepped = Request(method=method.value, url=url, data=data, headers=headers).prepare()
            elif json is not None:
                prepped = Request(method=method.value, url=url, json=json, headers=headers).prepare()
            else:
                prepped = Request(method=method.value, url=url, headers=headers).prepare()
        except Exception as e:
            raise NodeException(f"Failed to prepare HTTP request: {e}", code=WorkflowErrorCode.PROVIDER_ERROR)

        if hasattr(self._context, "workspace_hmac_secret") and self._context.workspace_hmac_secret:
            self._sign_request_with_hmac(prepped, self._context.workspace_hmac_secret)

        try:
            with Session() as session:
                response = session.send(prepped, timeout=timeout)
        except RequestException as e:
            raise NodeException(f"HTTP request failed: {e}", code=WorkflowErrorCode.PROVIDER_ERROR)
        try:
            json_response = response.json()
        except JSONDecodeError:
            json_response = None
        return self.Outputs(
            json=json_response,
            headers={header: value for header, value in response.headers.items()},
            status_code=response.status_code,
            text=response.text,
        )

    def _sign_request_with_hmac(self, request, hmac_secret: str) -> None:
        """Sign request using workspace HMAC secret"""
        timestamp = str(int(time.time()))

        body = request.body or b""
        if isinstance(body, str):
            body = body.encode()

        message = f"{timestamp}\n{request.method}\n{request.url}\n".encode() + body
        signature = hmac.new(hmac_secret.encode("utf-8"), message, hashlib.sha256)
        signature_b64 = base64.b64encode(signature.digest()).decode("utf-8")

        request.headers.update(
            {
                "X-Vellum-Timestamp": timestamp,
                "X-Vellum-Signature": signature_b64,
            }
        )

    def _vellum_execute_api(self, bearer_token, data, headers, method, url, timeout):
        client_vellum_secret = ClientVellumSecret(name=bearer_token.name) if bearer_token else None

        # Create request_options if timeout is specified
        request_options = None
        if timeout is not None:
            request_options = RequestOptions(timeout_in_seconds=timeout)

        try:
            vellum_response = self._context.vellum_client.execute_api(
                url=url,
                method=method.value,
                body=data,
                headers=headers,
                bearer_token=client_vellum_secret,
                request_options=request_options,
            )
        except ApiError as e:
            raise NodeException(f"Failed to prepare HTTP request: {e}", code=WorkflowErrorCode.NODE_EXECUTION)

        return self.Outputs(
            json=vellum_response.json_,
            headers={header: value for header, value in vellum_response.headers.items()},
            status_code=vellum_response.status_code,
            text=vellum_response.text,
        )
