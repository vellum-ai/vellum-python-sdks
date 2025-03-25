import requests_mock
import requests_mock.mocker

from tests.workflows.basic_api_node.workflow import SimpleAPIWorkflow


def test_run_workflow__happy_path(requests_mock: requests_mock.mocker.Mocker):
    # GIVEN an API request that will return a 200 OK response
    response_mock = requests_mock.post(
        "https://api.vellum.ai",
        json={"data": [1, 2, 3]},
        headers={"X-Response-Header": "bar"},
        status_code=200,
    )

    # AND a simple workflow that has an API node targeting this request
    workflow = SimpleAPIWorkflow()

    # WHEN we run the workflow
    terminal_event = workflow.run()

    # THEN we should see the expected outputs
    assert terminal_event.name == "workflow.execution.fulfilled"
    assert terminal_event.outputs == {
        "json": {"data": [1, 2, 3]},
        "headers": {"X-Response-Header": "bar"},
        "status_code": 200,
    }

    # AND the mock should have been called with the expected body
    assert response_mock.last_request
    assert response_mock.last_request.json() == {"key": "value"}
