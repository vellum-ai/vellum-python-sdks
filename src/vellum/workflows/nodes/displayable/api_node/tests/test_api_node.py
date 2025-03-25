import pytest

from vellum import ExecuteApiResponse, VellumSecret as ClientVellumSecret
from vellum.client.core.api_error import ApiError
from vellum.workflows.constants import APIRequestMethod, AuthorizationType
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

    class SimpleBaseAPINode(APINode):
        method = APIRequestMethod.POST
        authorization_type = AuthorizationType.BEARER_TOKEN
        url = "https://api.vellum.ai"
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
    assert vellum_client.execute_api.call_args.kwargs["body"] == {"key": "value"}
    bearer_token = vellum_client.execute_api.call_args.kwargs["bearer_token"]
    assert bearer_token == ClientVellumSecret(name="secret")
    assert terminal.headers == {"X-Response-Header": "bar"}


def test_api_node_raises_error_when_api_call_fails(vellum_client):
    # GIVEN an API call that fails
    vellum_client.execute_api.side_effect = ApiError(status_code=400, body="API Error")

    class SimpleAPINode(APINode):
        method = APIRequestMethod.GET
        authorization_type = AuthorizationType.BEARER_TOKEN
        url = "https://api.vellum.ai"
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
    assert vellum_client.execute_api.call_args.kwargs["body"] == {"key": "value"}


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
        url = "https://api.vellum.ai"
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
