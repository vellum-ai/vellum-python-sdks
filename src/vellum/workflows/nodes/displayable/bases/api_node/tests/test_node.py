import pytest
import os
from unittest.mock import patch

from vellum.client.types.execute_api_response import ExecuteApiResponse
from vellum.workflows.constants import APIRequestMethod
from vellum.workflows.errors.types import WorkflowErrorCode
from vellum.workflows.exceptions import NodeException
from vellum.workflows.nodes.displayable.bases.api_node.node import BaseAPINode
from vellum.workflows.types.core import VellumSecret


@pytest.mark.parametrize("method_value", ["GET", "get", APIRequestMethod.GET])
def test_api_node_with_string_method(method_value, vellum_client):
    class TestAPINode(BaseAPINode):
        method = method_value
        url = "https://example.com"
        headers = {"Authorization": VellumSecret(name="API_KEY")}

    mock_response = ExecuteApiResponse(
        json_={"status": "success"},
        headers={"content-type": "application/json"},
        status_code=200,
        text='{"status": "success"}',
    )
    vellum_client.execute_api.return_value = mock_response

    node = TestAPINode()
    result = node.run()

    assert result.status_code == 200

    vellum_client.execute_api.assert_called_once()
    call_args = vellum_client.execute_api.call_args
    assert call_args[1]["method"] == "GET"


def test_api_node_with_invalid_method():
    class TestAPINode(BaseAPINode):
        method = "INVALID_METHOD"
        url = "https://example.com"

    node = TestAPINode()

    with pytest.raises(NodeException) as exc_info:
        node.run()

    assert exc_info.value.code == WorkflowErrorCode.INVALID_INPUTS
    assert "Invalid HTTP method 'INVALID_METHOD'" == str(exc_info.value)


def test_api_node_adds_user_agent_header_when_none_provided(requests_mock):
    """
    Tests that the API node adds User-Agent header when no headers are provided.
    """

    class TestAPINode(BaseAPINode):
        method = APIRequestMethod.GET
        url = "https://example.com/test"

    response_mock = requests_mock.get(
        "https://example.com/test",
        json={"result": "success"},
        status_code=200,
    )

    node = TestAPINode()
    result = node.run()

    assert response_mock.last_request
    assert "vellum-ai" in response_mock.last_request.headers.get("User-Agent", "")

    assert result.status_code == 200


def test_api_node_adds_user_agent_header_when_headers_provided_without_user_agent(requests_mock):
    """
    Tests that the API node adds User-Agent header when headers are provided but don't include User-Agent.
    """

    class TestAPINode(BaseAPINode):
        method = APIRequestMethod.POST
        url = "https://example.com/test"
        headers = {"Content-Type": "application/json", "Custom-Header": "value"}
        json = {"test": "data"}

    response_mock = requests_mock.post(
        "https://example.com/test",
        json={"result": "success"},
        status_code=200,
    )

    node = TestAPINode()
    result = node.run()

    assert response_mock.last_request
    assert "vellum-ai" in response_mock.last_request.headers.get("User-Agent", "")
    assert response_mock.last_request.headers.get("Content-Type") == "application/json"
    assert response_mock.last_request.headers.get("Custom-Header") == "value"

    assert result.status_code == 200


def test_api_node_preserves_custom_user_agent_header(requests_mock):
    """
    Tests that the API node preserves a custom User-Agent header if provided.
    """

    class TestAPINode(BaseAPINode):
        method = APIRequestMethod.GET
        url = "https://example.com/test"
        headers = {"User-Agent": "Custom-Agent/1.0"}

    response_mock = requests_mock.get(
        "https://example.com/test",
        json={"result": "success"},
        status_code=200,
    )

    node = TestAPINode()
    result = node.run()

    assert response_mock.last_request
    assert response_mock.last_request.headers.get("User-Agent") == "Custom-Agent/1.0"

    assert result.status_code == 200


def test_local_execute_api_with_hmac_secret(requests_mock):
    """Test that _local_execute_api adds HMAC headers when VELLUM_HMAC_SECRET is set."""

    class TestAPINode(BaseAPINode):
        method = APIRequestMethod.POST
        url = "https://example.com/test"
        json = {"test": "data"}

    response_mock = requests_mock.post(
        "https://example.com/test",
        json={"result": "success"},
        status_code=200,
    )

    with patch.dict(os.environ, {"VELLUM_HMAC_SECRET": "test-secret"}):
        node = TestAPINode()
        result = node.run()

    assert response_mock.last_request
    assert "X-Vellum-Timestamp" in response_mock.last_request.headers
    assert "X-Vellum-Signature" in response_mock.last_request.headers
    assert result.status_code == 200
