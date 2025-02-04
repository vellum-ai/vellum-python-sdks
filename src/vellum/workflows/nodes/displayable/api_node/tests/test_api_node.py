from vellum import ExecuteApiResponse, VellumSecret as ClientVellumSecret
from vellum.workflows.constants import APIRequestMethod, AuthorizationType
from vellum.workflows.nodes import APINode
from vellum.workflows.state import BaseState
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
        body = {
            "key": "value",
        }
        headers = {
            "X-Test-Header": "foo",
        }
        bearer_token_value = VellumSecret(name="secret")

    node = SimpleBaseAPINode(state=BaseState())
    terminal = node.run()

    assert vellum_client.execute_api.call_count == 1
    bearer_token = vellum_client.execute_api.call_args.kwargs["bearer_token"]
    assert bearer_token == ClientVellumSecret(name="secret")
    assert terminal.headers == {"X-Response-Header": "bar"}
