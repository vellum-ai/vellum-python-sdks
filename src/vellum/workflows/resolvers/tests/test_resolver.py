from datetime import datetime
from unittest.mock import Mock
from uuid import uuid4

from vellum.client.types.workflow_execution_detail import WorkflowExecutionDetail
from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.resolvers.resolver import VellumResolver
from vellum.workflows.state.base import BaseState, NodeExecutionCache
from vellum.workflows.state.context import WorkflowContext


def test_load_state_with_context_success():
    """Test load_state successfully loads state when context and client are available."""
    resolver = VellumResolver()
    execution_id = uuid4()

    class TestState(BaseState):
        test_key: str = "test_value"

    class TestWorkflow(BaseWorkflow[BaseInputs, TestState]):
        pass

    # GIVEN a state dictionary that matches what the resolver expects
    state_dict = {
        "test_key": "test_value",
        "meta": {
            "workflow_definition": "MockWorkflow",
            "id": str(uuid4()),
            "span_id": str(uuid4()),
            "updated_ts": datetime.now().isoformat(),
            "workflow_inputs": BaseInputs(),
            "external_inputs": {},
            "node_outputs": {},
            "node_execution_cache": NodeExecutionCache(),
            "parent": None,
        },
    }

    mock_response = WorkflowExecutionDetail(
        span_id="test-span-id", start=datetime.now(), inputs=[], outputs=[], spans=[], state=state_dict
    )

    mock_client = Mock()
    mock_client.workflow_executions.retrieve_workflow_execution_detail.return_value = mock_response

    # AND context with the test workflow class
    context = WorkflowContext(vellum_client=mock_client)
    TestWorkflow(context=context, resolvers=[resolver])

    result = resolver.load_state(previous_execution_id=execution_id)

    # THEN should return an instance of TestWorkflow.State, not BaseState
    assert isinstance(result, TestState)
    assert result.test_key == "test_value"

    mock_client.workflow_executions.retrieve_workflow_execution_detail.assert_called_once_with(
        execution_id=str(execution_id)
    )
