import pytest

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
