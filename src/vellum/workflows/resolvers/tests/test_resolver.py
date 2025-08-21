from datetime import datetime
from unittest.mock import Mock
from uuid import uuid4

from vellum.client.types.workflow_execution_detail import WorkflowExecutionDetail
from vellum.workflows.resolvers.resolver import VellumResolver
from vellum.workflows.state.context import WorkflowContext


def test_load_state_with_context_success():
    """Test load_state successfully loads state when context and client are available."""
    resolver = VellumResolver()
    execution_id = uuid4()

    mock_response = WorkflowExecutionDetail(
        span_id="test-span-id", start=datetime.now(), inputs=[], outputs=[], spans=[], state={"test_key": "test_value"}
    )

    mock_client = Mock()
    mock_client.workflow_executions.retrieve_workflow_execution_detail.return_value = mock_response

    context = WorkflowContext(vellum_client=mock_client)
    resolver.register_context(context)

    result = resolver.load_state(previous_execution_id=execution_id)

    assert result == {"test_key": "test_value"}
    mock_client.workflow_executions.retrieve_workflow_execution_detail.assert_called_once_with(
        execution_id=execution_id
    )
