# This file was auto-generated by Fern from our API Definition.

import typing
from ...core.client_wrapper import SyncClientWrapper
from .types.folder_entities_list_request_entity_status import FolderEntitiesListRequestEntityStatus
from ...core.request_options import RequestOptions
from ...types.paginated_folder_entity_list import PaginatedFolderEntityList
from ...core.pydantic_utilities import parse_obj_as
from json.decoder import JSONDecodeError
from ...core.api_error import ApiError
from ...core.jsonable_encoder import jsonable_encoder
from ...core.client_wrapper import AsyncClientWrapper

# this is used as the default value for optional parameters
OMIT = typing.cast(typing.Any, ...)


class FolderEntitiesClient:
    def __init__(self, *, client_wrapper: SyncClientWrapper):
        self._client_wrapper = client_wrapper

    def list(
        self,
        *,
        parent_folder_id: str,
        entity_status: typing.Optional[FolderEntitiesListRequestEntityStatus] = None,
        limit: typing.Optional[int] = None,
        offset: typing.Optional[int] = None,
        ordering: typing.Optional[str] = None,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> PaginatedFolderEntityList:
        """
        List all folder entities within a specified folder.

        Parameters
        ----------
        parent_folder_id : str
            Filter down to only those entities whose parent folder has the specified ID.

            To filter by an entity's parent folder, provide the ID of the parent folder. To filter by the root directory, provide
            a string representing the entity type of the root directory. Supported root directories include:
            - PROMPT_SANDBOX
            - WORKFLOW_SANDBOX
            - DOCUMENT_INDEX
            - TEST_SUITE

        entity_status : typing.Optional[FolderEntitiesListRequestEntityStatus]
            Filter down to only those objects whose entities have a status matching the status specified.

            * `ACTIVE` - Active
            * `ARCHIVED` - Archived

        limit : typing.Optional[int]
            Number of results to return per page.

        offset : typing.Optional[int]
            The initial index from which to return the results.

        ordering : typing.Optional[str]
            Which field to use when ordering the results.

        request_options : typing.Optional[RequestOptions]
            Request-specific configuration.

        Returns
        -------
        PaginatedFolderEntityList


        Examples
        --------
        from vellum import Vellum

        client = Vellum(
            x_api_key="YOUR_X_API_KEY",
            api_key="YOUR_API_KEY",
        )
        client.folder_entities.list(
            parent_folder_id="parent_folder_id",
        )
        """
        _response = self._client_wrapper.httpx_client.request(
            "v1/folder-entities",
            base_url=self._client_wrapper.get_environment().default,
            method="GET",
            params={
                "entity_status": entity_status,
                "limit": limit,
                "offset": offset,
                "ordering": ordering,
                "parent_folder_id": parent_folder_id,
            },
            request_options=request_options,
        )
        try:
            if 200 <= _response.status_code < 300:
                return typing.cast(
                    PaginatedFolderEntityList,
                    parse_obj_as(
                        type_=PaginatedFolderEntityList,  # type: ignore
                        object_=_response.json(),
                    ),
                )
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)

    def add_entity_to_folder(
        self, folder_id: str, *, entity_id: str, request_options: typing.Optional[RequestOptions] = None
    ) -> None:
        """
        Add an entity to a specific folder or root directory.

        Adding an entity to a folder will remove it from any other folders it might have been a member of.

        Parameters
        ----------
        folder_id : str
            The ID of the folder to which the entity should be added. This can be a UUID of a folder, or the name of a root
            directory. Supported root directories include:
            - PROMPT_SANDBOX
            - WORKFLOW_SANDBOX
            - DOCUMENT_INDEX
            - TEST_SUITE

        entity_id : str
            The ID of the entity you would like to move.

        request_options : typing.Optional[RequestOptions]
            Request-specific configuration.

        Returns
        -------
        None

        Examples
        --------
        from vellum import Vellum

        client = Vellum(
            x_api_key="YOUR_X_API_KEY",
            api_key="YOUR_API_KEY",
        )
        client.folder_entities.add_entity_to_folder(
            folder_id="folder_id",
            entity_id="entity_id",
        )
        """
        _response = self._client_wrapper.httpx_client.request(
            f"v1/folders/{jsonable_encoder(folder_id)}/add-entity",
            base_url=self._client_wrapper.get_environment().default,
            method="POST",
            json={
                "entity_id": entity_id,
            },
            request_options=request_options,
            omit=OMIT,
        )
        try:
            if 200 <= _response.status_code < 300:
                return
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)


class AsyncFolderEntitiesClient:
    def __init__(self, *, client_wrapper: AsyncClientWrapper):
        self._client_wrapper = client_wrapper

    async def list(
        self,
        *,
        parent_folder_id: str,
        entity_status: typing.Optional[FolderEntitiesListRequestEntityStatus] = None,
        limit: typing.Optional[int] = None,
        offset: typing.Optional[int] = None,
        ordering: typing.Optional[str] = None,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> PaginatedFolderEntityList:
        """
        List all folder entities within a specified folder.

        Parameters
        ----------
        parent_folder_id : str
            Filter down to only those entities whose parent folder has the specified ID.

            To filter by an entity's parent folder, provide the ID of the parent folder. To filter by the root directory, provide
            a string representing the entity type of the root directory. Supported root directories include:
            - PROMPT_SANDBOX
            - WORKFLOW_SANDBOX
            - DOCUMENT_INDEX
            - TEST_SUITE

        entity_status : typing.Optional[FolderEntitiesListRequestEntityStatus]
            Filter down to only those objects whose entities have a status matching the status specified.

            * `ACTIVE` - Active
            * `ARCHIVED` - Archived

        limit : typing.Optional[int]
            Number of results to return per page.

        offset : typing.Optional[int]
            The initial index from which to return the results.

        ordering : typing.Optional[str]
            Which field to use when ordering the results.

        request_options : typing.Optional[RequestOptions]
            Request-specific configuration.

        Returns
        -------
        PaginatedFolderEntityList


        Examples
        --------
        import asyncio

        from vellum import AsyncVellum

        client = AsyncVellum(
            x_api_key="YOUR_X_API_KEY",
            api_key="YOUR_API_KEY",
        )


        async def main() -> None:
            await client.folder_entities.list(
                parent_folder_id="parent_folder_id",
            )


        asyncio.run(main())
        """
        _response = await self._client_wrapper.httpx_client.request(
            "v1/folder-entities",
            base_url=self._client_wrapper.get_environment().default,
            method="GET",
            params={
                "entity_status": entity_status,
                "limit": limit,
                "offset": offset,
                "ordering": ordering,
                "parent_folder_id": parent_folder_id,
            },
            request_options=request_options,
        )
        try:
            if 200 <= _response.status_code < 300:
                return typing.cast(
                    PaginatedFolderEntityList,
                    parse_obj_as(
                        type_=PaginatedFolderEntityList,  # type: ignore
                        object_=_response.json(),
                    ),
                )
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)

    async def add_entity_to_folder(
        self, folder_id: str, *, entity_id: str, request_options: typing.Optional[RequestOptions] = None
    ) -> None:
        """
        Add an entity to a specific folder or root directory.

        Adding an entity to a folder will remove it from any other folders it might have been a member of.

        Parameters
        ----------
        folder_id : str
            The ID of the folder to which the entity should be added. This can be a UUID of a folder, or the name of a root
            directory. Supported root directories include:
            - PROMPT_SANDBOX
            - WORKFLOW_SANDBOX
            - DOCUMENT_INDEX
            - TEST_SUITE

        entity_id : str
            The ID of the entity you would like to move.

        request_options : typing.Optional[RequestOptions]
            Request-specific configuration.

        Returns
        -------
        None

        Examples
        --------
        import asyncio

        from vellum import AsyncVellum

        client = AsyncVellum(
            x_api_key="YOUR_X_API_KEY",
            api_key="YOUR_API_KEY",
        )


        async def main() -> None:
            await client.folder_entities.add_entity_to_folder(
                folder_id="folder_id",
                entity_id="entity_id",
            )


        asyncio.run(main())
        """
        _response = await self._client_wrapper.httpx_client.request(
            f"v1/folders/{jsonable_encoder(folder_id)}/add-entity",
            base_url=self._client_wrapper.get_environment().default,
            method="POST",
            json={
                "entity_id": entity_id,
            },
            request_options=request_options,
            omit=OMIT,
        )
        try:
            if 200 <= _response.status_code < 300:
                return
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)
