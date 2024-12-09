# This file was auto-generated by Fern from our API Definition.

from vellum import Vellum
from vellum import AsyncVellum
import typing
from .utilities import validate_response


async def test_list_(client: Vellum, async_client: AsyncVellum) -> None:
    expected_response: typing.Any = {
        "count": 123,
        "next": "http://api.example.org/accounts/?offset=400&limit=100",
        "previous": "http://api.example.org/accounts/?offset=200&limit=100",
        "results": [
            {
                "id": "id",
                "type": "FOLDER",
                "data": {
                    "id": "id",
                    "label": "label",
                    "created": "2024-01-15T09:30:00Z",
                    "modified": "2024-01-15T09:30:00Z",
                    "has_contents": True,
                },
            }
        ],
    }
    expected_types: typing.Any = {
        "count": "integer",
        "next": None,
        "previous": None,
        "results": (
            "list",
            {
                0: {
                    "id": None,
                    "type": None,
                    "data": {
                        "id": None,
                        "label": None,
                        "created": "datetime",
                        "modified": "datetime",
                        "has_contents": None,
                    },
                }
            },
        ),
    }
    response = client.folder_entities.list(parent_folder_id="parent_folder_id")
    validate_response(response, expected_response, expected_types)

    async_response = await async_client.folder_entities.list(parent_folder_id="parent_folder_id")
    validate_response(async_response, expected_response, expected_types)


async def test_add_entity_to_folder(client: Vellum, async_client: AsyncVellum) -> None:
    # Type ignore to avoid mypy complaining about the function not being meant to return a value
    assert (
        client.folder_entities.add_entity_to_folder(folder_id="folder_id", entity_id="entity_id")  # type: ignore[func-returns-value]
        is None
    )

    assert (
        await async_client.folder_entities.add_entity_to_folder(folder_id="folder_id", entity_id="entity_id")  # type: ignore[func-returns-value]
        is None
    )