from vellum import ExecuteApiResponse, VellumSecret
from vellum.workflows.constants import APIRequestMethod
from vellum.workflows.nodes import APINode
from vellum.workflows.state import BaseState


def test_run_workflow__secrets(vellum_client):
    vellum_client.execute_api.return_value = ExecuteApiResponse(
        status_code=200,
        text='{"status": 200, "data": [1, 2, 3]}',
        json_={"data": [1, 2, 3]},
        headers={"X-Response-Header": "bar"},
    )

    class SimpleBaseAPINode(APINode):
        method = APIRequestMethod.POST
        url = "https://api.vellum.ai"
        body = {
            "key": "value",
        }
        headers = {
            "X-Test-Header": "foo",
        }
        bearer_token_value = VellumSecret(name="secret")

    node = SimpleBaseAPINode(state=BaseState())
    node.run()

    assert vellum_client.execute_api.call_count == 1
    bearer_token = vellum_client.execute_api.call_args.kwargs["bearer_token"]
    assert bearer_token == VellumSecret(name="secret")
