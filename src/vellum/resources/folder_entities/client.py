# This file was auto-generated by Fern from our API Definition.

import typing
import urllib.parse
from json.decoder import JSONDecodeError

from ...core.api_error import ApiError
from ...core.client_wrapper import AsyncClientWrapper, SyncClientWrapper
from ...core.jsonable_encoder import jsonable_encoder

# this is used as the default value for optional parameters
OMIT = typing.cast(typing.Any, ...)


class FolderEntitiesClient:
    def __init__(self, *, client_wrapper: SyncClientWrapper):
        self._client_wrapper = client_wrapper

    def add_entity_to_folder(self, folder_id: str, *, entity_id: str) -> None:
        """
        Add an entity to a specific folder or root directory.

        Adding an entity to a folder will remove it from any other folders it might have been a member of.

        Parameters:
            - folder_id: str. The ID of the folder to which the entity should be added. This can be a UUID of a folder, or the name of a root directory (e.g. "PROMPT_SANDBOX").

            - entity_id: str. The ID of the entity you would like to move.
        ---
        from vellum.client import Vellum

        client = Vellum(
            api_key="YOUR_API_KEY",
        )
        client.folder_entities.add_entity_to_folder(
            folder_id="folder_id",
            entity_id="entity_id",
        )
        """
        _response = self._client_wrapper.httpx_client.request(
            "POST",
            urllib.parse.urljoin(
                f"{self._client_wrapper.get_environment().default}/", f"v1/folders/{folder_id}/add-entity"
            ),
            json=jsonable_encoder({"entity_id": entity_id}),
            headers=self._client_wrapper.get_headers(),
            timeout=None,
        )
        if 200 <= _response.status_code < 300:
            return
        try:
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)


class AsyncFolderEntitiesClient:
    def __init__(self, *, client_wrapper: AsyncClientWrapper):
        self._client_wrapper = client_wrapper

    async def add_entity_to_folder(self, folder_id: str, *, entity_id: str) -> None:
        """
        Add an entity to a specific folder or root directory.

        Adding an entity to a folder will remove it from any other folders it might have been a member of.

        Parameters:
            - folder_id: str. The ID of the folder to which the entity should be added. This can be a UUID of a folder, or the name of a root directory (e.g. "PROMPT_SANDBOX").

            - entity_id: str. The ID of the entity you would like to move.
        ---
        from vellum.client import AsyncVellum

        client = AsyncVellum(
            api_key="YOUR_API_KEY",
        )
        await client.folder_entities.add_entity_to_folder(
            folder_id="folder_id",
            entity_id="entity_id",
        )
        """
        _response = await self._client_wrapper.httpx_client.request(
            "POST",
            urllib.parse.urljoin(
                f"{self._client_wrapper.get_environment().default}/", f"v1/folders/{folder_id}/add-entity"
            ),
            json=jsonable_encoder({"entity_id": entity_id}),
            headers=self._client_wrapper.get_headers(),
            timeout=None,
        )
        if 200 <= _response.status_code < 300:
            return
        try:
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)
