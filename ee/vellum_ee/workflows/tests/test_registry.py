from datetime import datetime, timezone
from uuid import uuid4

from vellum.workflows.events.types import NodeParentContext, WorkflowParentContext
from vellum.workflows.events.workflow import WorkflowExecutionInitiatedBody, WorkflowExecutionInitiatedEvent
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes import BaseNode
from vellum.workflows.state.base import BaseState
from vellum.workflows.workflows.base import BaseWorkflow
from vellum_ee.workflows.display.utils.registry import (
    get_parent_display_context_from_event,
    register_workflow_display_context,
)


class MockInputs(BaseInputs):
    pass


class MockState(BaseState):
    pass


class MockNode(BaseNode):
    pass


class MockWorkflow(BaseWorkflow[MockInputs, MockState]):
    pass


class MockWorkflowDisplayContext:
    pass


def test_get_parent_display_context_from_event__no_parent():
    """Test event with no parent returns None"""
    # GIVEN a workflow execution initiated event with no parent
    event: WorkflowExecutionInitiatedEvent = WorkflowExecutionInitiatedEvent(
        id=uuid4(),
        timestamp=datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
        trace_id=uuid4(),
        span_id=uuid4(),
        body=WorkflowExecutionInitiatedBody(
            workflow_definition=MockWorkflow,
            inputs=MockInputs(),
        ),
        parent=None,  # No parent
    )

    # WHEN getting parent display context
    result = get_parent_display_context_from_event(event)

    # THEN it should return None
    assert result is None


def test_get_parent_display_context_from_event__non_workflow_parent():
    """Test event with non-workflow parent continues traversal"""
    # GIVEN an event with a non-workflow parent (NodeParentContext)
    non_workflow_parent = NodeParentContext(node_definition=MockNode, span_id=uuid4(), parent=None)

    event: WorkflowExecutionInitiatedEvent = WorkflowExecutionInitiatedEvent(
        id=uuid4(),
        timestamp=datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
        trace_id=uuid4(),
        span_id=uuid4(),
        body=WorkflowExecutionInitiatedBody(
            workflow_definition=MockWorkflow,
            inputs=MockInputs(),
        ),
        parent=non_workflow_parent,
    )

    # WHEN getting parent display context
    result = get_parent_display_context_from_event(event)

    # THEN it should return None (no workflow parent found)
    assert result is None


def test_get_parent_display_context_from_event__nested_workflow_parents():
    """Test event with nested workflow parents traverses correctly"""
    # GIVEN a chain of nested contexts:
    # Event -> WorkflowParent -> NodeParent -> MiddleWorkflowParent -> NodeParent

    # Top level workflow parent
    top_workflow_span_id = uuid4()
    top_context = MockWorkflowDisplayContext()
    register_workflow_display_context(top_workflow_span_id, top_context)  # type: ignore[arg-type]

    top_workflow_parent = WorkflowParentContext(
        workflow_definition=MockWorkflow, span_id=top_workflow_span_id, parent=None
    )

    top_node_parent = NodeParentContext(node_definition=MockNode, span_id=uuid4(), parent=top_workflow_parent)

    # AND middle workflow parent (no display context)
    middle_workflow_span_id = uuid4()
    middle_workflow_parent = WorkflowParentContext(
        workflow_definition=MockWorkflow, span_id=middle_workflow_span_id, parent=top_node_parent
    )

    # AND node parent between middle workflow and event
    node_parent = NodeParentContext(node_definition=MockNode, span_id=uuid4(), parent=middle_workflow_parent)

    event: WorkflowExecutionInitiatedEvent = WorkflowExecutionInitiatedEvent(
        id=uuid4(),
        timestamp=datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
        trace_id=uuid4(),
        span_id=uuid4(),
        body=WorkflowExecutionInitiatedBody(
            workflow_definition=MockWorkflow,
            inputs=MockInputs(),
        ),
        parent=node_parent,
    )

    # WHEN getting parent display context
    result = get_parent_display_context_from_event(event)

    # THEN it should find the top-level workflow context
    assert result == top_context


def test_get_parent_display_context_from_event__middle_workflow_has_context():
    """Test event returns middle workflow context when it's the first one with registered context"""
    # GIVEN a chain of nested contexts:
    # Event -> WorkflowParent -> NodeParent -> MiddleWorkflowParent -> NodeParent

    top_workflow_span_id = uuid4()
    top_context = MockWorkflowDisplayContext()
    register_workflow_display_context(top_workflow_span_id, top_context)  # type: ignore[arg-type]

    top_workflow_parent = WorkflowParentContext(
        workflow_definition=MockWorkflow, span_id=top_workflow_span_id, parent=None
    )

    # AND node parent between top workflow and middle workflow
    top_node_parent = NodeParentContext(node_definition=MockNode, span_id=uuid4(), parent=top_workflow_parent)

    # AND middle workflow parent
    middle_workflow_span_id = uuid4()
    middle_context = MockWorkflowDisplayContext()
    register_workflow_display_context(middle_workflow_span_id, middle_context)  # type: ignore[arg-type]

    middle_workflow_parent = WorkflowParentContext(
        workflow_definition=MockWorkflow, span_id=middle_workflow_span_id, parent=top_node_parent
    )

    node_parent = NodeParentContext(node_definition=MockNode, span_id=uuid4(), parent=middle_workflow_parent)

    event: WorkflowExecutionInitiatedEvent = WorkflowExecutionInitiatedEvent(
        id=uuid4(),
        timestamp=datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
        trace_id=uuid4(),
        span_id=uuid4(),
        body=WorkflowExecutionInitiatedBody(
            workflow_definition=MockWorkflow,
            inputs=MockInputs(),
        ),
        parent=node_parent,
    )

    # WHEN getting parent display context
    result = get_parent_display_context_from_event(event)

    # THEN it should find the MIDDLE workflow context
    assert result == middle_context
