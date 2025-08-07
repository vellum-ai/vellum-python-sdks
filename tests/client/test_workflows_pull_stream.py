import io
import typing
import zipfile

import httpx
import pytest

from vellum.client.resources.workflows.raw_client import RawWorkflowsClient
from vellum.client.core.client_wrapper import SyncClientWrapper
from vellum.client.environment import VellumEnvironment
from vellum.client.core.http_client import HttpClient
from typing import cast


class _FakeResponse:
    def __init__(self, chunks: typing.List[bytes]) -> None:
        self._chunks = chunks
        self.status_code = 200
        self._closed = False
        self._read_called = False
        self.text = ""
        self._json: typing.Dict[str, typing.Any] = {}

    def iter_bytes(self, chunk_size: typing.Optional[int] = None):
        if self._closed:
            raise httpx.StreamClosed()
        yield from self._chunks

    def read(self) -> None:
        self._read_called = True

    def json(self):
        return self._json


class _FakeStreamCtx:
    def __init__(self, resp: _FakeResponse) -> None:
        self._resp = resp

    def __enter__(self):
        return self._resp

    def __exit__(self, exc_type, exc, tb):
        self._resp._closed = True
        return False


class _FakeHttpxClient:
    def __init__(self, resp: _FakeResponse) -> None:
        self._resp = resp

    def stream(self, *args, **kwargs):
        return _FakeStreamCtx(self._resp)


class _FakeClientWrapper(SyncClientWrapper):
    def __init__(self, httpx_client: _FakeHttpxClient) -> None:
        # Provide types expected by RawWorkflowsClient
        self.httpx_client = cast(HttpClient, httpx_client)
        self._environment: VellumEnvironment = VellumEnvironment(
            default="https://example.test",
            predict="https://predict.example.test",
            documents="https://docs.example.test",
        )

    def get_environment(self) -> VellumEnvironment:
        return self._environment


def _zip_bytes(file_map: typing.Dict[str, str]) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as zf:
        for name, content in file_map.items():
            zf.writestr(name, content)
    return buffer.getvalue()


def test_raw_workflows_pull_buffers_stream_to_avoid_streamclosed():
    """
    Ensures RawWorkflowsClient.pull buffers the httpx stream inside the context so that
    iterating the returned iterator after the context closes does not raise httpx.StreamClosed.
    """

    payload = _zip_bytes({"workflow.py": "print('hello')"})
    chunks = [payload]
    fake_resp = _FakeResponse(chunks)
    fake_httpx = _FakeHttpxClient(fake_resp)
    wrapper = _FakeClientWrapper(fake_httpx)
    client = RawWorkflowsClient(client_wrapper=wrapper)

    response = client.pull("wf-123")
    result = b"".join(response.data)

    assert result == payload
