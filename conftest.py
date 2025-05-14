import pytest
import os
import sys
import threading
import time
import traceback
from uuid import UUID, uuid4
from typing import Any, Callable, Generator, List

from dotenv import dotenv_values
from pytest_mock import MockerFixture
import requests_mock

from vellum.client.environment import VellumEnvironment
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
    vellum_client._client_wrapper._environment = VellumEnvironment.PRODUCTION
    vellum_client._client_wrapper.api_key = ""
    return vellum_client


@pytest.fixture
def vellum_adhoc_prompt_client(vellum_client: Any) -> Any:
    return vellum_client.ad_hoc


@pytest.fixture
def mock_httpx_transport(mocker: MockerFixture) -> Any:
    return mocker.patch("httpx._client.HTTPTransport").return_value


@pytest.fixture
def mock_requests() -> Any:
    with requests_mock.Mocker() as m:
        yield m


@pytest.fixture
def debug_threads() -> Callable[[int], None]:
    """
    A useful fixture for debugging threads that are hung. Use this to print out the stacktrace of all running threads.
    Example usage:

    def test_workflow_hangs(debug_threads):
        # ...
        debug_threads(5)
        # ...

    This will print out the stacktrace of all running threads 5 seconds after the test has finished.
    """

    logger = load_logger()

    def _debug_threads(sleep_time: int = 5) -> None:
        time.sleep(sleep_time)
        for thread in threading.enumerate():
            logger.info(f"\nThread {thread.name} is still running")

            if not isinstance(thread.ident, int):
                logger.info(f"Invalid Thread {thread.name} has no ident")
                continue

            # Get stacktrace for this thread
            for frame in traceback.extract_stack(sys._current_frames()[thread.ident]):
                logger.info(f"  File {frame.filename}, line {frame.lineno}, in {frame.name}")
                if frame.line:
                    logger.info(f"    {frame.line}")

    return _debug_threads
