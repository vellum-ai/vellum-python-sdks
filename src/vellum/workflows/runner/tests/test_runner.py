from vellum.client.core.api_error import ApiError
from vellum.workflows.errors.types import WorkflowErrorCode
from vellum.workflows.events.node import NodeExecutionInitiatedEvent, NodeExecutionRejectedEvent
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.state.base import BaseState
from vellum.workflows.workflows.base import BaseWorkflow


def test_workflow_runner__handles_400_api_error_with_integration_details():
    """
    Tests that WorkflowRunner handles 400 API errors with integration details
    as INVALID_INPUTS errors.
    """

    # GIVEN a node that raises an ApiError with status_code 400 and integration details
    class TestInputs(BaseInputs):
        pass

    class TestState(BaseState):
        pass

    class TestNode(BaseNode[TestState]):
        class Outputs(BaseNode.Outputs):
            result: str

        def run(self) -> "TestNode.Outputs":
            raise ApiError(
                status_code=400,
                body={
                    "message": "Invalid request to integration",
                    "integration": {
                        "name": "test_integration",
                        "provider": "test_provider",
                    },
                },
            )

    class TestWorkflow(BaseWorkflow[TestInputs, TestState]):
        graph = TestNode

        class Outputs(BaseWorkflow.Outputs):
            result: str

    workflow = TestWorkflow()

    # WHEN we run the node
    events = list(workflow.run_node(node=TestNode))

    # THEN we should get a rejected event with INVALID_INPUTS error code
    assert len(events) == 2
    assert isinstance(events[0], NodeExecutionInitiatedEvent)
    assert isinstance(events[1], NodeExecutionRejectedEvent)

    # AND the error should have the correct code and message
    rejected_event = events[1]
    assert rejected_event.body.error.code == WorkflowErrorCode.INVALID_INPUTS
    assert rejected_event.body.error.message == "Invalid request to integration"

    # AND the raw_data should contain the integration details
    assert rejected_event.body.error.raw_data == {
        "integration": {
            "name": "test_integration",
            "provider": "test_provider",
        }
    }


def test_workflow_runner__handles_403_api_error_with_integration_details():
    """
    Tests that WorkflowRunner handles 403 API errors with integration details correctly.
    """

    # GIVEN a node that raises an ApiError with status_code 403 and integration details
    class TestInputs(BaseInputs):
        pass

    class TestState(BaseState):
        pass

    class TestNode(BaseNode[TestState]):
        class Outputs(BaseNode.Outputs):
            result: str

        def run(self) -> "TestNode.Outputs":
            raise ApiError(
                status_code=403,
                body={
                    "message": "You must authenticate with this integration",
                    "integration": {
                        "name": "test_integration",
                        "provider": "test_provider",
                    },
                },
            )

    class TestWorkflow(BaseWorkflow[TestInputs, TestState]):
        graph = TestNode

        class Outputs(BaseWorkflow.Outputs):
            result: str

    workflow = TestWorkflow()

    # WHEN we run the node
    events = list(workflow.run_node(node=TestNode))

    # THEN we should get a rejected event with INTEGRATION_CREDENTIALS_UNAVAILABLE error code
    assert len(events) == 2
    assert isinstance(events[0], NodeExecutionInitiatedEvent)
    assert isinstance(events[1], NodeExecutionRejectedEvent)

    # AND the error should have the correct code and message
    rejected_event = events[1]
    assert rejected_event.body.error.code == WorkflowErrorCode.INTEGRATION_CREDENTIALS_UNAVAILABLE
    assert rejected_event.body.error.message == "You must authenticate with this integration"

    # AND the raw_data should contain the integration details
    assert rejected_event.body.error.raw_data == {
        "integration": {
            "name": "test_integration",
            "provider": "test_provider",
        }
    }


def test_workflow_runner__handles_400_api_error_without_integration_details():
    """
    Tests that WorkflowRunner handles 400 API errors without integration details
    as generic errors (not INTEGRATION_CREDENTIALS_UNAVAILABLE).
    """

    # GIVEN a node that raises an ApiError with status_code 400 but no integration details
    class TestInputs(BaseInputs):
        pass

    class TestState(BaseState):
        pass

    class TestNode(BaseNode[TestState]):
        class Outputs(BaseNode.Outputs):
            result: str

        def run(self) -> "TestNode.Outputs":
            raise ApiError(
                status_code=400,
                body={
                    "message": "Invalid request parameters",
                },
            )

    class TestWorkflow(BaseWorkflow[TestInputs, TestState]):
        graph = TestNode

        class Outputs(BaseWorkflow.Outputs):
            result: str

    workflow = TestWorkflow()

    # WHEN we run the node
    events = list(workflow.run_node(node=TestNode))

    # THEN we should get a rejected event
    assert len(events) == 2
    assert isinstance(events[0], NodeExecutionInitiatedEvent)
    assert isinstance(events[1], NodeExecutionRejectedEvent)

    # AND the error should NOT have INTEGRATION_CREDENTIALS_UNAVAILABLE code
    rejected_event = events[1]
    assert rejected_event.body.error.code != WorkflowErrorCode.INTEGRATION_CREDENTIALS_UNAVAILABLE
