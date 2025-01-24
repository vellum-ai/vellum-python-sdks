import pytest
import os
from uuid import UUID, uuid4
from typing import Any, Callable, Generator, List

from dotenv import dotenv_values
from pytest_mock import MockerFixture
import requests_mock

from vellum.workflows.logging import load_logger


@pytest.fixture(scope="session", autouse=True)
def configure_logging() -> Generator[None, None, None]:
    """Used to output logs when running tests"""

    env_vars = dotenv_values()
    dotenv_log_level = env_vars.get("LOG_LEVEL")
    if dotenv_log_level and not os.environ.get("LOG_LEVEL"):
        os.environ["LOG_LEVEL"] = dotenv_log_level

    # Set the package's logger
    logger = load_logger()

    yield

    # Clean up after tests
    logger.handlers.clear()


UUIDGenerator = Callable[[], UUID]


@pytest.fixture
def mock_uuid4_generator(mocker: MockerFixture) -> Callable[[str], UUIDGenerator]:
    def _get_uuid_generator(path_to_uuid_import: str) -> UUIDGenerator:
        generated_uuids: List[UUID] = []
        mock_uuid4 = mocker.patch(path_to_uuid_import)

        def _generate_uuid() -> UUID:
            new_uuid = uuid4()
            generated_uuids.append(new_uuid)
            return new_uuid

        mock_uuid4.side_effect = generated_uuids
        return _generate_uuid

    return _get_uuid_generator


@pytest.fixture
def vellum_client_class(mocker: MockerFixture) -> Any:
    vellum_client_class = mocker.patch("vellum.workflows.vellum_client.Vellum")
    return vellum_client_class


@pytest.fixture
def vellum_client(vellum_client_class) -> Any:
    vellum_client = vellum_client_class.return_value
    return vellum_client


@pytest.fixture
def vellum_adhoc_prompt_client(vellum_client: Any) -> Any:
    return vellum_client.ad_hoc


@pytest.fixture
def mock_requests() -> Any:
    with requests_mock.Mocker() as m:
        yield m
