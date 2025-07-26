import pytest

from vellum import ExecuteApiResponse, VellumSecret as ClientVellumSecret
from vellum.client.core.api_error import ApiError
from vellum.workflows.constants import APIRequestMethod, AuthorizationType
from vellum.workflows.errors.types import WorkflowErrorCode
from vellum.workflows.exceptions import NodeException
from vellum.workflows.nodes import APINode
from vellum.workflows.types.core import VellumSecret


def test_run_workflow__secrets(vellum_client):
    vellum_client.execute_api.return_value = ExecuteApiResponse(
        status_code=200,
        text='{"status": 200, "data": [1, 2, 3]}',
        json_={"data": [1, 2, 3]},
        headers={"X-Response-Header": "bar"},
    )
    vellum_client._client_wrapper.get_headers.return_value = {"User-Agent": "vellum-ai/1.0.6"}

    class SimpleBaseAPINode(APINode):
        method = APIRequestMethod.POST
        authorization_type = AuthorizationType.BEARER_TOKEN
        url = "https://example.vellum.ai"
        json = {
            "key": "value",
        }
        headers = {
            "X-Test-Header": "foo",
        }
        bearer_token_value = VellumSecret(name="secret")

    node = SimpleBaseAPINode()
    terminal = node.run()

    assert vellum_client.execute_api.call_count == 1
    assert vellum_client.execute_api.call_args.kwargs["url"] == "https://example.vellum.ai"
    assert vellum_client.execute_api.call_args.kwargs["body"] == {"key": "value"}
    headers = vellum_client.execute_api.call_args.kwargs["headers"]
    assert headers["X-Test-Header"] == "foo"
    assert "vellum-ai" in headers.get("User-Agent", "")
    bearer_token = vellum_client.execute_api.call_args.kwargs["bearer_token"]
    assert bearer_token == ClientVellumSecret(name="secret")
    assert terminal.headers == {"X-Response-Header": "bar"}


def test_api_node_raises_error_when_api_call_fails(vellum_client):
    # GIVEN an API call that fails
    vellum_client.execute_api.side_effect = ApiError(status_code=400, body="API Error")
    vellum_client._client_wrapper.get_headers.return_value = {"User-Agent": "vellum-ai/1.0.6"}

    class SimpleAPINode(APINode):
        method = APIRequestMethod.GET
        authorization_type = AuthorizationType.BEARER_TOKEN
        url = "https://example.vellum.ai"
        json = {
            "key": "value",
        }
        headers = {
            "X-Test-Header": "foo",
        }
        bearer_token_value = VellumSecret(name="api_key")

    node = SimpleAPINode()

    # WHEN we run the node
    with pytest.raises(NodeException) as excinfo:
        node.run()

    # THEN an exception should be raised
    assert "Failed to prepare HTTP request" in str(excinfo.value)

    # AND the API call should have been made
    assert vellum_client.execute_api.call_count == 1
    assert vellum_client.execute_api.call_args.kwargs["url"] == "https://example.vellum.ai"
    assert vellum_client.execute_api.call_args.kwargs["body"] == {"key": "value"}
    headers = vellum_client.execute_api.call_args.kwargs["headers"]
    assert headers["X-Test-Header"] == "foo"
    assert "vellum-ai" in headers.get("User-Agent", "")


def test_api_node_defaults_to_get_method(vellum_client):
    # GIVEN a successful API response
    vellum_client.execute_api.return_value = ExecuteApiResponse(
        status_code=200,
        text='{"status": 200, "data": [1, 2, 3]}',
        json_={"data": [1, 2, 3]},
        headers={"X-Response-Header": "bar"},
    )

    # AND an API node without a method specified
    class SimpleAPINodeWithoutMethod(APINode):
        authorization_type = AuthorizationType.BEARER_TOKEN
        url = "https://example.vellum.ai"
        headers = {
            "X-Test-Header": "foo",
        }
        bearer_token_value = VellumSecret(name="secret")

    node = SimpleAPINodeWithoutMethod()

    # WHEN we run the node
    node.run()

    # THEN the API call should be made with GET method
    assert vellum_client.execute_api.call_count == 1
    method = vellum_client.execute_api.call_args.kwargs["method"]
    assert method == APIRequestMethod.GET.value


def test_api_node__detects_client_environment_urls__adds_token(mock_httpx_transport, mock_requests, monkeypatch):
    # GIVEN an API node with a URL pointing back to Vellum
    class SimpleAPINodeToVellum(APINode):
        url = "https://api.vellum.ai"

    # AND a mock request sent to the Vellum API would return a 200
    mock_response = mock_requests.get(
        "https://api.vellum.ai",
        status_code=200,
        json={"data": [1, 2, 3]},
    )

    # AND an api key is set
    monkeypatch.setenv("VELLUM_API_KEY", "vellum-api-key-1234")

    # WHEN we run the node
    node = SimpleAPINodeToVellum()
    node.run()

    # THEN the execute_api method should not have been called
    mock_httpx_transport.handle_request.assert_not_called()

    # AND the vellum API should have been called with the correct headers
    assert mock_response.last_request
    assert mock_response.last_request.headers["X-API-Key"] == "vellum-api-key-1234"


def test_api_node__detects_client_environment_urls__does_not_override_headers(
    mock_httpx_transport, mock_requests, monkeypatch
):
    # GIVEN an API node with a URL pointing back to Vellum
    class SimpleAPINodeToVellum(APINode):
        url = "https://api.vellum.ai"
        headers = {
            "X-API-Key": "vellum-api-key-5678",
        }

    # AND a mock request sent to the Vellum API would return a 200
    mock_response = mock_requests.get(
        "https://api.vellum.ai",
        status_code=200,
        json={"data": [1, 2, 3]},
    )

    # AND an api key is set
    monkeypatch.setenv("VELLUM_API_KEY", "vellum-api-key-1234")

    # WHEN we run the node
    node = SimpleAPINodeToVellum()
    node.run()

    # THEN the execute_api method should not have been called
    mock_httpx_transport.handle_request.assert_not_called()

    # AND the vellum API should have been called with the correct headers
    assert mock_response.last_request
    assert mock_response.last_request.headers["X-API-Key"] == "vellum-api-key-5678"


def test_api_node__detects_client_environment_urls__legacy_does_not_override_headers(
    mock_httpx_transport, mock_requests, monkeypatch
):
    # GIVEN an API node with a URL pointing back to Vellum
    class SimpleAPINodeToVellum(APINode):
        url = "https://api.vellum.ai"
        headers = {
            "X_API_KEY": "vellum-api-key-5678",
        }

    # AND a mock request sent to the Vellum API would return a 200
    mock_response = mock_requests.get(
        "https://api.vellum.ai",
        status_code=200,
        json={"data": [1, 2, 3]},
    )

    # AND an api key is set
    monkeypatch.setenv("VELLUM_API_KEY", "vellum-api-key-1234")

    # WHEN we run the node
    node = SimpleAPINodeToVellum()
    node.run()

    # THEN the execute_api method should not have been called
    mock_httpx_transport.handle_request.assert_not_called()

    # AND the vellum API should have been called with the correct headers
    assert mock_response.last_request
    assert mock_response.last_request.headers["X_API_KEY"] == "vellum-api-key-5678"


def test_api_node_raises_error_for_empty_url():
    class APINodeWithEmptyURL(APINode):
        method = APIRequestMethod.GET
        url = ""

    node = APINodeWithEmptyURL()

    with pytest.raises(NodeException) as excinfo:
        node.run()

    assert excinfo.value.code == WorkflowErrorCode.INVALID_INPUTS
    assert "URL is required and must be a non-empty string" in str(excinfo.value)


def test_api_node_raises_error_for_none_url():
    class APINodeWithNoneURL(APINode):
        method = APIRequestMethod.GET
        url = None  # type: ignore

    node = APINodeWithNoneURL()

    with pytest.raises(NodeException) as excinfo:
        node.run()

    assert excinfo.value.code == WorkflowErrorCode.INVALID_INPUTS
    assert "URL is required and must be a non-empty string" in str(excinfo.value)


def test_api_node_raises_error_for_whitespace_url():
    class APINodeWithWhitespaceURL(APINode):
        method = APIRequestMethod.GET
        url = "   "

    node = APINodeWithWhitespaceURL()

    with pytest.raises(NodeException) as excinfo:
        node.run()

    assert excinfo.value.code == WorkflowErrorCode.INVALID_INPUTS
    assert "URL is required and must be a non-empty string" in str(excinfo.value)


def test_api_node_passes_timeout_to_vellum_client(vellum_client):
    """Test that timeout is passed to vellum client as RequestOptions."""
    vellum_client.execute_api.return_value = ExecuteApiResponse(
        status_code=200,
        text='{"result": "success"}',
        json_={"result": "success"},
        headers={"content-type": "application/json"},
    )

    # GIVEN an API node configured with a timeout value of 25 seconds
    class APINodeWithTimeout(APINode):
        method = APIRequestMethod.GET
        authorization_type = AuthorizationType.BEARER_TOKEN
        url = "https://example.com"
        timeout = 25
        bearer_token_value = VellumSecret(name="secret")

    # WHEN the API node is executed
    node = APINodeWithTimeout()
    node.run()

    # THEN the vellum client should be called exactly once
    assert vellum_client.execute_api.call_count == 1
    call_args = vellum_client.execute_api.call_args
    request_options = call_args.kwargs["request_options"]
    # AND the call should include RequestOptions with the correct timeout
    assert request_options is not None
    assert request_options["timeout_in_seconds"] == 25
