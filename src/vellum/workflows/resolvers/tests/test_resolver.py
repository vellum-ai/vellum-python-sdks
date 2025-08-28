from datetime import datetime
from unittest.mock import Mock
from uuid import uuid4

from vellum.client.types.span_link import SpanLink
from vellum.client.types.vellum_code_resource_definition import VellumCodeResourceDefinition
from vellum.client.types.workflow_execution_detail import WorkflowExecutionDetail
from vellum.client.types.workflow_execution_initiated_body import WorkflowExecutionInitiatedBody
from vellum.client.types.workflow_execution_initiated_event import WorkflowExecutionInitiatedEvent
from vellum.client.types.workflow_execution_span import WorkflowExecutionSpan
from vellum.client.types.workflow_execution_span_attributes import WorkflowExecutionSpanAttributes
from vellum.client.types.workflow_parent_context import WorkflowParentContext
from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.resolvers.resolver import VellumResolver
from vellum.workflows.resolvers.types import LoadStateResult
from vellum.workflows.state.base import BaseState, NodeExecutionCache
from vellum.workflows.state.context import WorkflowContext


def test_load_state_with_context_success():
    """Test load_state successfully loads state when context and client are available."""
    resolver = VellumResolver()
    execution_id = uuid4()
    root_execution_id = uuid4()

    class TestState(BaseState):
        test_key: str = "test_value"

    class TestWorkflow(BaseWorkflow[BaseInputs, TestState]):
        pass

    # GIVEN a state dictionary that matches what the resolver expects
    prev_id = str(uuid4())
    prev_span_id = str(uuid4())
    state_dict = {
        "test_key": "test_value",
        "meta": {
            "workflow_definition": "MockWorkflow",
            "id": prev_id,
            "span_id": prev_span_id,
            "updated_ts": datetime.now().isoformat(),
            "workflow_inputs": BaseInputs(),
            "external_inputs": {},
            "node_outputs": {},
            "node_execution_cache": NodeExecutionCache(),
            "parent": None,
        },
    }

    mock_workflow_definition = VellumCodeResourceDefinition(
        name="TestWorkflow", module=["test", "module"], id=str(uuid4())
    )

    mock_body = WorkflowExecutionInitiatedBody(workflow_definition=mock_workflow_definition, inputs={})

    previous_trace_id = str(uuid4())
    root_trace_id = str(uuid4())

    previous_invocation = WorkflowExecutionInitiatedEvent(
        id=str(uuid4()),
        timestamp=datetime.now(),
        trace_id=previous_trace_id,
        span_id=str(execution_id),
        body=mock_body,
        links=[
            SpanLink(
                trace_id=previous_trace_id,
                type="PREVIOUS_SPAN",
                span_context=WorkflowParentContext(workflow_definition=mock_workflow_definition, span_id=str(uuid4())),
            ),
            SpanLink(
                trace_id=root_trace_id,
                type="ROOT_SPAN",
                span_context=WorkflowParentContext(
                    workflow_definition=mock_workflow_definition, span_id=str(root_execution_id)
                ),
            ),
        ],
    )

    root_invocation = WorkflowExecutionInitiatedEvent(
        id=str(uuid4()),
        timestamp=datetime.now(),
        trace_id=root_trace_id,
        span_id=str(root_execution_id),
        body=mock_body,
        links=None,  # Root invocation has no links
    )

    mock_span = WorkflowExecutionSpan(
        span_id=str(execution_id),  # Use the actual execution_id
        start_ts=datetime.now(),
        end_ts=datetime.now(),
        attributes=WorkflowExecutionSpanAttributes(label="Test Workflow", workflow_id=str(uuid4())),
        events=[previous_invocation, root_invocation],
    )

    mock_response = WorkflowExecutionDetail(
        span_id="test-span-id", start=datetime.now(), inputs=[], outputs=[], spans=[mock_span], state=state_dict
    )

    mock_client = Mock()
    mock_client.workflow_executions.retrieve_workflow_execution_detail.return_value = mock_response

    # AND context with the test workflow class is set up
    context = WorkflowContext(vellum_client=mock_client)
    TestWorkflow(context=context, resolvers=[resolver])

    # WHEN load_state is called
    result = resolver.load_state(previous_execution_id=execution_id)

    # THEN should return LoadStateResult with state and span link info
    assert isinstance(result, LoadStateResult)
    assert result.state is not None
    assert isinstance(result.state, TestState)
    assert result.state.test_key == "test_value"

    # AND the new state should have different meta IDs than those provided in the loaded state_dict
    assert str(result.state.meta.id) != prev_id
    assert str(result.state.meta.span_id) != prev_span_id

    # AND should have span link info
    assert result.previous_trace_id == previous_invocation.trace_id
    assert result.previous_span_id == previous_invocation.span_id
    assert result.root_trace_id == root_invocation.trace_id
    assert result.root_span_id == root_invocation.span_id

    mock_client.workflow_executions.retrieve_workflow_execution_detail.assert_called_once_with(
        execution_id=str(execution_id)
    )
