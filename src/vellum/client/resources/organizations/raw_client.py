# This file was auto-generated by Fern from our API Definition.

from ...core.client_wrapper import SyncClientWrapper
import typing
from ...core.request_options import RequestOptions
from ...core.http_response import HttpResponse
from ...types.organization_read import OrganizationRead
from ...core.pydantic_utilities import parse_obj_as
from json.decoder import JSONDecodeError
from ...core.api_error import ApiError
from ...core.client_wrapper import AsyncClientWrapper
from ...core.http_response import AsyncHttpResponse


class RawOrganizationsClient:
    def __init__(self, *, client_wrapper: SyncClientWrapper):
        self._client_wrapper = client_wrapper

    def organization_identity(
        self, *, request_options: typing.Optional[RequestOptions] = None
    ) -> HttpResponse[OrganizationRead]:
        """
        Retrieves information about the active Organization

        Parameters
        ----------
        request_options : typing.Optional[RequestOptions]
            Request-specific configuration.

        Returns
        -------
        HttpResponse[OrganizationRead]

        """
        _response = self._client_wrapper.httpx_client.request(
            "v1/organizations/identity",
            base_url=self._client_wrapper.get_environment().base,
            method="GET",
            request_options=request_options,
        )
        try:
            if 200 <= _response.status_code < 300:
                _data = typing.cast(
                    OrganizationRead,
                    parse_obj_as(
                        type_=OrganizationRead,  # type: ignore
                        object_=_response.json(),
                    ),
                )
                return HttpResponse(response=_response, data=_data)
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)


class AsyncRawOrganizationsClient:
    def __init__(self, *, client_wrapper: AsyncClientWrapper):
        self._client_wrapper = client_wrapper

    async def organization_identity(
        self, *, request_options: typing.Optional[RequestOptions] = None
    ) -> AsyncHttpResponse[OrganizationRead]:
        """
        Retrieves information about the active Organization

        Parameters
        ----------
        request_options : typing.Optional[RequestOptions]
            Request-specific configuration.

        Returns
        -------
        AsyncHttpResponse[OrganizationRead]

        """
        _response = await self._client_wrapper.httpx_client.request(
            "v1/organizations/identity",
            base_url=self._client_wrapper.get_environment().base,
            method="GET",
            request_options=request_options,
        )
        try:
            if 200 <= _response.status_code < 300:
                _data = typing.cast(
                    OrganizationRead,
                    parse_obj_as(
                        type_=OrganizationRead,  # type: ignore
                        object_=_response.json(),
                    ),
                )
                return AsyncHttpResponse(response=_response, data=_data)
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)
