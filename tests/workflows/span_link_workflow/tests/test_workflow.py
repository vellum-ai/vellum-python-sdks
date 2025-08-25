from datetime import datetime
from uuid import uuid4

from vellum.client.types.span_link import SpanLink as ClientSpanLink
from vellum.client.types.vellum_code_resource_definition import (
    VellumCodeResourceDefinition as ClientVellumCodeResourceDefinition,
)
from vellum.client.types.workflow_execution_detail import WorkflowExecutionDetail
from vellum.client.types.workflow_execution_initiated_body import (
    WorkflowExecutionInitiatedBody as ClientWorkflowExecutionInitiatedBody,
)
from vellum.client.types.workflow_execution_initiated_event import (
    WorkflowExecutionInitiatedEvent as ClientWorkflowExecutionInitiatedEvent,
)
from vellum.client.types.workflow_execution_span import WorkflowExecutionSpan
from vellum.client.types.workflow_execution_span_attributes import WorkflowExecutionSpanAttributes
from vellum.client.types.workflow_parent_context import WorkflowParentContext as ClientWorkflowParentContext
from vellum.workflows.events.types import SpanLink, WorkflowParentContext
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.state.base import NodeExecutionCache
from vellum.workflows.types.definition import VellumCodeResourceDefinition
from vellum.workflows.workflows.event_filters import all_workflow_event_filter

from tests.workflows.span_link_workflow.workflow import SpanLinkWorkflow


def test_span_linking_across_three_executions(vellum_client):
    """Test that span linking works correctly across three workflow executions"""

    # GIVEN the first execution
    workflow1 = SpanLinkWorkflow()

    # WHEN the first execution is run
    events1 = list(workflow1.stream(event_filter=all_workflow_event_filter))
    terminal_event1 = events1[-1]

    # THEN the first execution should be fulfilled with count 1
    assert terminal_event1.name == "workflow.execution.fulfilled"
    assert terminal_event1.outputs == {"current_count": 1}

    # AND the workflow initiation event should have NO span links
    workflow_initiated_events = [e for e in events1 if e.name == "workflow.execution.initiated"]
    assert len(workflow_initiated_events) == 1

    workflow_init_event = workflow_initiated_events[0]
    assert workflow_init_event.links is None  # No span links for first execution

    first_trace_id = str(workflow1.context.execution_context.trace_id)
    assert workflow1.context.execution_context.parent_context is not None
    first_span_id = str(workflow1.context.execution_context.parent_context.span_id)

    first_execution_id = str(first_span_id)

    state_dict = {
        "execution_count": 1,
        "meta": {
            "workflow_definition": "SpanLinkWorkflow",
            "id": str(uuid4()),
            "span_id": str(first_span_id),
            "updated_ts": datetime.now().isoformat(),
            "workflow_inputs": BaseInputs(),
            "external_inputs": {},
            "node_outputs": {},
            "node_execution_cache": NodeExecutionCache(),
            "parent": None,
        },
    }

    mock_body = ClientWorkflowExecutionInitiatedBody(
        workflow_definition=ClientVellumCodeResourceDefinition(
            name="SpanLinkWorkflow",
            module=["tests", "workflows", "span_link_workflow", "workflow"],
            id="d0cb6b18-2170-428b-8dc3-de75a9eb5c8d",
        ),
        inputs={},
    )

    first_workflow_init_event = ClientWorkflowExecutionInitiatedEvent(
        id=str(uuid4()),
        timestamp=datetime.now(),
        trace_id=str(first_trace_id),
        span_id=str(first_span_id),
        body=mock_body,
        links=None,
    )

    mock_span = WorkflowExecutionSpan(
        name="workflow.execution",
        span_id=str(first_execution_id),
        start_ts=datetime.now(),
        end_ts=datetime.now(),
        events=[first_workflow_init_event],
        attributes=WorkflowExecutionSpanAttributes(label="Span Linking Workflow", workflow_id=str(uuid4())),
    )

    mock_execution_detail = WorkflowExecutionDetail(
        span_id="test-span-id", start=datetime.now(), inputs=[], outputs=[], spans=[mock_span], state=state_dict
    )

    vellum_client.workflow_executions.retrieve_workflow_execution_detail.return_value = mock_execution_detail

    # WHEN the second execution is run with the previous execution ID
    workflow2 = SpanLinkWorkflow()

    events2 = list(workflow2.stream(previous_execution_id=first_execution_id, event_filter=all_workflow_event_filter))
    terminal_event2 = events2[-1]

    # THEN the second execution should be fulfilled with count 2
    assert terminal_event2.name == "workflow.execution.fulfilled"
    assert terminal_event2.outputs == {"current_count": 2}

    # AND the workflow initiation event should have correct span links (previous and root)
    workflow_initiated_events = [e for e in events2 if e.name == "workflow.execution.initiated"]
    assert len(workflow_initiated_events) == 1

    workflow_init_event = workflow_initiated_events[0]
    assert workflow_init_event.links == [
        SpanLink(
            trace_id=first_trace_id,
            type="PREVIOUS_SPAN",
            span_context=WorkflowParentContext(
                parent=None,
                links=None,
                workflow_definition=VellumCodeResourceDefinition(
                    name="SpanLinkWorkflow",
                    module=["tests", "workflows", "span_link_workflow", "workflow"],
                    id="d0cb6b18-2170-428b-8dc3-de75a9eb5c8d",
                ),
                type="WORKFLOW",
                span_id=first_span_id,
            ),
        ),
        SpanLink(
            trace_id=first_trace_id,
            type="ROOT_SPAN",
            span_context=WorkflowParentContext(
                parent=None,
                links=None,
                workflow_definition=VellumCodeResourceDefinition(
                    name="SpanLinkWorkflow",
                    module=["tests", "workflows", "span_link_workflow", "workflow"],
                    id="d0cb6b18-2170-428b-8dc3-de75a9eb5c8d",
                ),
                type="WORKFLOW",
                span_id=first_span_id,
            ),
        ),
    ]

    second_trace_id = str(workflow2.context.execution_context.trace_id)
    assert workflow2.context.execution_context.parent_context is not None
    second_span_id = str(workflow2.context.execution_context.parent_context.span_id)

    second_execution_id = str(second_span_id)

    state_dict = {
        "execution_count": 2,
        "meta": {
            "workflow_definition": "SpanLinkWorkflow",
            "id": str(uuid4()),
            "span_id": str(second_span_id),
            "updated_ts": datetime.now().isoformat(),
            "workflow_inputs": BaseInputs(),
            "external_inputs": {},
            "node_outputs": {},
            "node_execution_cache": NodeExecutionCache(),
            "parent": None,
        },
    }

    second_workflow_init_event = ClientWorkflowExecutionInitiatedEvent(
        id=str(uuid4()),
        timestamp=datetime.now(),
        trace_id=str(second_trace_id),
        span_id=str(second_span_id),
        body=mock_body,
        links=[
            ClientSpanLink(
                trace_id=str(first_trace_id),
                type="PREVIOUS_SPAN",
                span_context=ClientWorkflowParentContext(
                    workflow_definition=ClientVellumCodeResourceDefinition(
                        name="SpanLinkWorkflow",
                        module=["tests", "workflows", "span_link_workflow", "workflow"],
                        id="d0cb6b18-2170-428b-8dc3-de75a9eb5c8d",
                    ),
                    type="WORKFLOW",
                    span_id=str(first_span_id),
                ),
            ),
            ClientSpanLink(
                trace_id=str(first_trace_id),
                type="ROOT_SPAN",
                span_context=ClientWorkflowParentContext(
                    workflow_definition=ClientVellumCodeResourceDefinition(
                        name="SpanLinkWorkflow",
                        module=["tests", "workflows", "span_link_workflow", "workflow"],
                        id="d0cb6b18-2170-428b-8dc3-de75a9eb5c8d",
                    ),
                    type="WORKFLOW",
                    span_id=str(first_span_id),
                ),
            ),
        ],
    )

    mock_span = WorkflowExecutionSpan(
        name="workflow.execution",
        span_id=str(second_execution_id),  # Use the actual second execution ID
        start_ts=datetime.now(),
        end_ts=datetime.now(),
        events=[second_workflow_init_event],
        attributes=WorkflowExecutionSpanAttributes(label="Span Linking Workflow", workflow_id=str(uuid4())),
    )

    mock_execution_detail = WorkflowExecutionDetail(
        span_id="test-span-id", start=datetime.now(), inputs=[], outputs=[], spans=[mock_span], state=state_dict
    )

    vellum_client.workflow_executions.retrieve_workflow_execution_detail.return_value = mock_execution_detail

    workflow3 = SpanLinkWorkflow()

    events3 = list(workflow3.stream(previous_execution_id=second_execution_id, event_filter=all_workflow_event_filter))
    terminal_event3 = events3[-1]

    # THEN third execution should be fulfilled with count 3
    assert terminal_event3.name == "workflow.execution.fulfilled"
    assert terminal_event3.outputs == {"current_count": 3}

    # AND the workflow initiation event should have correct span links
    workflow_initiated_events = [e for e in events3 if e.name == "workflow.execution.initiated"]
    assert len(workflow_initiated_events) == 1

    workflow_init_event = workflow_initiated_events[0]
    assert workflow_init_event.links == [
        SpanLink(
            trace_id=second_trace_id,
            type="PREVIOUS_SPAN",
            span_context=WorkflowParentContext(
                parent=None,
                links=None,
                workflow_definition=VellumCodeResourceDefinition(
                    name="SpanLinkWorkflow",
                    module=["tests", "workflows", "span_link_workflow", "workflow"],
                    id="d0cb6b18-2170-428b-8dc3-de75a9eb5c8d",
                ),
                type="WORKFLOW",
                span_id=second_span_id,
            ),
        ),
        SpanLink(
            trace_id=first_trace_id,  # Root should always point to the first execution
            type="ROOT_SPAN",
            span_context=WorkflowParentContext(
                parent=None,
                links=None,
                workflow_definition=VellumCodeResourceDefinition(
                    name="SpanLinkWorkflow",
                    module=["tests", "workflows", "span_link_workflow", "workflow"],
                    id="d0cb6b18-2170-428b-8dc3-de75a9eb5c8d",
                ),
                type="WORKFLOW",
                span_id=first_span_id,  # Root should always point to the first execution
            ),
        ),
    ]
