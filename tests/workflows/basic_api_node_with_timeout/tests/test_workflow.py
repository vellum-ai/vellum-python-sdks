import requests_mock.mocker

from vellum.workflows.constants import APIRequestMethod
from vellum.workflows.nodes.displayable import APINode

from tests.workflows.basic_api_node_with_timeout.workflow import (
    APINodeWithoutTimeoutWorkflow,
    APINodeWithTimeoutWorkflow,
)


def test_api_node_with_timeout__happy_path(requests_mock: requests_mock.mocker.Mocker):
    """Test that APINode with timeout attribute works correctly."""
    # GIVEN an API request that will return a 200 OK response
    response_mock = requests_mock.post(
        "https://api.vellum.ai",
        json={"data": [1, 2, 3]},
        status_code=200,
    )

    # AND a workflow that has an API node with timeout configured
    workflow = APINodeWithTimeoutWorkflow()

    # WHEN we run the workflow
    terminal_event = workflow.run()

    # THEN we should see the expected outputs
    assert terminal_event.name == "workflow.execution.fulfilled"
    assert terminal_event.outputs == {
        "json": {"data": [1, 2, 3]},
        "status_code": 200,
        "text": '{"data": [1, 2, 3]}',
    }

    # AND the mock should have been called with the expected body
    assert response_mock.last_request
    assert response_mock.last_request.json() == {"key": "value"}


def test_api_node_without_timeout__happy_path(requests_mock: requests_mock.mocker.Mocker):
    """Test that APINode without timeout attribute works correctly (backward compatibility)."""
    # GIVEN an API request that will return a 200 OK response
    response_mock = requests_mock.get(
        "https://api.vellum.ai",
        json={"status": "ok"},
        status_code=200,
    )

    # AND a workflow that has an API node without timeout configured
    workflow = APINodeWithoutTimeoutWorkflow()

    # WHEN we run the workflow
    terminal_event = workflow.run()

    # THEN we should see the expected outputs
    assert terminal_event.name == "workflow.execution.fulfilled"
    assert terminal_event.outputs == {
        "json": {"status": "ok"},
        "status_code": 200,
        "text": '{"status": "ok"}',
    }

    # AND the mock should have been called
    assert response_mock.called


def test_api_node_with_timeout__timeout_respected():
    """Test that timeout attribute is properly set on the node class."""
    # GIVEN a workflow with timeout configured
    from tests.workflows.basic_api_node_with_timeout.workflow import APINodeWithTimeout

    # WHEN we check the node class's timeout attribute
    # THEN the timeout should be set correctly in the class definition
    assert hasattr(APINodeWithTimeout, "timeout")
    assert APINodeWithTimeout.timeout.instance == 30


def test_api_node_timeout_attribute_types():
    """Test that timeout attribute can handle different value types."""

    class APINodeWithIntTimeout(APINode):
        method = APIRequestMethod.POST
        url = "https://api.vellum.ai"
        timeout = 60  # integer
        json = {"test": "data"}

    class APINodeWithFloatTimeout(APINode):
        method = APIRequestMethod.POST
        url = "https://api.vellum.ai"
        timeout = 30.5  # float
        json = {"test": "data"}

    # Test integer timeout
    assert APINodeWithIntTimeout.timeout.instance == 60

    # Test float timeout
    assert APINodeWithFloatTimeout.timeout.instance == 30.5
