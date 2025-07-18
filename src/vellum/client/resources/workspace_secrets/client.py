# This file was auto-generated by Fern from our API Definition.

import typing
from ...core.client_wrapper import SyncClientWrapper
from ...core.request_options import RequestOptions
from ...types.workspace_secret_read import WorkspaceSecretRead
from ...core.jsonable_encoder import jsonable_encoder
from ...core.pydantic_utilities import parse_obj_as
from json.decoder import JSONDecodeError
from ...core.api_error import ApiError
from ...core.client_wrapper import AsyncClientWrapper

# this is used as the default value for optional parameters
OMIT = typing.cast(typing.Any, ...)


class WorkspaceSecretsClient:
    def __init__(self, *, client_wrapper: SyncClientWrapper):
        self._client_wrapper = client_wrapper

    def retrieve(self, id: str, *, request_options: typing.Optional[RequestOptions] = None) -> WorkspaceSecretRead:
        """
        Used to retrieve a Workspace Secret given its ID or name.

        Parameters
        ----------
        id : str
            Either the Workspace Secret's ID or its unique name

        request_options : typing.Optional[RequestOptions]
            Request-specific configuration.

        Returns
        -------
        WorkspaceSecretRead


        Examples
        --------
        from vellum import Vellum

        client = Vellum(
            api_version="YOUR_API_VERSION",
            api_key="YOUR_API_KEY",
        )
        client.workspace_secrets.retrieve(
            id="id",
        )
        """
        _response = self._client_wrapper.httpx_client.request(
            f"v1/workspace-secrets/{jsonable_encoder(id)}",
            base_url=self._client_wrapper.get_environment().default,
            method="GET",
            request_options=request_options,
        )
        try:
            if 200 <= _response.status_code < 300:
                return typing.cast(
                    WorkspaceSecretRead,
                    parse_obj_as(
                        type_=WorkspaceSecretRead,  # type: ignore
                        object_=_response.json(),
                    ),
                )
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)

    def partial_update(
        self,
        id: str,
        *,
        label: typing.Optional[str] = OMIT,
        value: typing.Optional[str] = OMIT,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> WorkspaceSecretRead:
        """
        Used to update a Workspace Secret given its ID or name.

        Parameters
        ----------
        id : str
            Either the Workspace Secret's ID or its unique name

        label : typing.Optional[str]

        value : typing.Optional[str]

        request_options : typing.Optional[RequestOptions]
            Request-specific configuration.

        Returns
        -------
        WorkspaceSecretRead


        Examples
        --------
        from vellum import Vellum

        client = Vellum(
            api_version="YOUR_API_VERSION",
            api_key="YOUR_API_KEY",
        )
        client.workspace_secrets.partial_update(
            id="id",
        )
        """
        _response = self._client_wrapper.httpx_client.request(
            f"v1/workspace-secrets/{jsonable_encoder(id)}",
            base_url=self._client_wrapper.get_environment().default,
            method="PATCH",
            json={
                "label": label,
                "value": value,
            },
            headers={
                "content-type": "application/json",
            },
            request_options=request_options,
            omit=OMIT,
        )
        try:
            if 200 <= _response.status_code < 300:
                return typing.cast(
                    WorkspaceSecretRead,
                    parse_obj_as(
                        type_=WorkspaceSecretRead,  # type: ignore
                        object_=_response.json(),
                    ),
                )
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)


class AsyncWorkspaceSecretsClient:
    def __init__(self, *, client_wrapper: AsyncClientWrapper):
        self._client_wrapper = client_wrapper

    async def retrieve(
        self, id: str, *, request_options: typing.Optional[RequestOptions] = None
    ) -> WorkspaceSecretRead:
        """
        Used to retrieve a Workspace Secret given its ID or name.

        Parameters
        ----------
        id : str
            Either the Workspace Secret's ID or its unique name

        request_options : typing.Optional[RequestOptions]
            Request-specific configuration.

        Returns
        -------
        WorkspaceSecretRead


        Examples
        --------
        import asyncio

        from vellum import AsyncVellum

        client = AsyncVellum(
            api_version="YOUR_API_VERSION",
            api_key="YOUR_API_KEY",
        )


        async def main() -> None:
            await client.workspace_secrets.retrieve(
                id="id",
            )


        asyncio.run(main())
        """
        _response = await self._client_wrapper.httpx_client.request(
            f"v1/workspace-secrets/{jsonable_encoder(id)}",
            base_url=self._client_wrapper.get_environment().default,
            method="GET",
            request_options=request_options,
        )
        try:
            if 200 <= _response.status_code < 300:
                return typing.cast(
                    WorkspaceSecretRead,
                    parse_obj_as(
                        type_=WorkspaceSecretRead,  # type: ignore
                        object_=_response.json(),
                    ),
                )
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)

    async def partial_update(
        self,
        id: str,
        *,
        label: typing.Optional[str] = OMIT,
        value: typing.Optional[str] = OMIT,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> WorkspaceSecretRead:
        """
        Used to update a Workspace Secret given its ID or name.

        Parameters
        ----------
        id : str
            Either the Workspace Secret's ID or its unique name

        label : typing.Optional[str]

        value : typing.Optional[str]

        request_options : typing.Optional[RequestOptions]
            Request-specific configuration.

        Returns
        -------
        WorkspaceSecretRead


        Examples
        --------
        import asyncio

        from vellum import AsyncVellum

        client = AsyncVellum(
            api_version="YOUR_API_VERSION",
            api_key="YOUR_API_KEY",
        )


        async def main() -> None:
            await client.workspace_secrets.partial_update(
                id="id",
            )


        asyncio.run(main())
        """
        _response = await self._client_wrapper.httpx_client.request(
            f"v1/workspace-secrets/{jsonable_encoder(id)}",
            base_url=self._client_wrapper.get_environment().default,
            method="PATCH",
            json={
                "label": label,
                "value": value,
            },
            headers={
                "content-type": "application/json",
            },
            request_options=request_options,
            omit=OMIT,
        )
        try:
            if 200 <= _response.status_code < 300:
                return typing.cast(
                    WorkspaceSecretRead,
                    parse_obj_as(
                        type_=WorkspaceSecretRead,  # type: ignore
                        object_=_response.json(),
                    ),
                )
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)
