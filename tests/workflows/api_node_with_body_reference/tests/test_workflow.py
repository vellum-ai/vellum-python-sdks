import requests_mock
import requests_mock.mocker

from tests.workflows.api_node_with_body_reference.workflow import APINodeWithBodyReferenceWorkflow


def test_run_workflow__happy_path(requests_mock: requests_mock.mocker.Mocker):
    # GIVEN an API request that will return a 200 OK response
    response_mock = requests_mock.post(
        "https://testing.vellum.ai/api",
        json={"output": "body"},
        status_code=200,
    )

    # AND a simple workflow that has an API node targeting this request
    workflow = APINodeWithBodyReferenceWorkflow()

    # WHEN we run the workflow
    terminal_event = workflow.run()

    # THEN we should see the expected outputs
    assert terminal_event.name == "workflow.execution.fulfilled"
    assert terminal_event.outputs == {
        "json": {"output": "body"},
    }

    # AND the mock should have been called with the expected body
    assert response_mock.last_request
    assert response_mock.last_request.json() == {"key": "value"}

    # AND the User-Agent header should be included to prevent 429 status codes
    assert response_mock.last_request.headers.get("User-Agent") == "vellum-ai/1.0.5"
