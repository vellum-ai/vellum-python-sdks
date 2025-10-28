from uuid import uuid4

from vellum.workflows.events.types import WorkflowParentContext
from vellum.workflows.events.workflow import WorkflowExecutionSnapshottedBody, WorkflowExecutionSnapshottedEvent
from vellum.workflows.inputs import BaseInputs
from vellum.workflows.nodes import BaseNode, InlineSubworkflowNode
from vellum.workflows.outputs.base import BaseOutputs
from vellum.workflows.state.base import BaseState
from vellum.workflows.workflows.base import BaseWorkflow
from vellum.workflows.workflows.event_filters import root_workflow_event_filter


class NestedInputs(BaseInputs):
    value: str


class NestedNode(BaseNode):
    value = NestedInputs.value

    class Outputs(BaseOutputs):
        result: str

    def run(self) -> Outputs:
        return self.Outputs(result=f"nested: {self.value}")


class NestedWorkflow(BaseWorkflow[NestedInputs, BaseState]):
    graph = NestedNode

    class Outputs(BaseOutputs):
        result = NestedNode.Outputs.result


class ParentInputs(BaseInputs):
    value: str


class SubworkflowNode(InlineSubworkflowNode):
    subworkflow_inputs = {
        "value": ParentInputs.value,
    }
    subworkflow = NestedWorkflow


class ParentWorkflow(BaseWorkflow[ParentInputs, BaseState]):
    graph = SubworkflowNode

    class Outputs(BaseOutputs):
        result = SubworkflowNode.Outputs.result


def test_root_workflow_event_filter__filters_nested_workflow_snapshotted_events():
    """
    Tests that root_workflow_event_filter filters out snapshotted events from nested workflows.
    """

    parent_workflow_class = ParentWorkflow
    nested_workflow_class = NestedWorkflow

    parent_workflow = ParentWorkflow()
    nested_workflow = NestedWorkflow()

    parent_state = parent_workflow.get_default_state(ParentInputs(value="test"))
    parent_snapshotted_event: WorkflowExecutionSnapshottedEvent = WorkflowExecutionSnapshottedEvent(
        trace_id=uuid4(),
        span_id=uuid4(),
        body=WorkflowExecutionSnapshottedBody(
            workflow_definition=parent_workflow_class,
            state=parent_state,
        ),
        parent=None,
    )

    nested_state = nested_workflow.get_default_state(NestedInputs(value="test"))
    nested_snapshotted_event: WorkflowExecutionSnapshottedEvent = WorkflowExecutionSnapshottedEvent(
        trace_id=uuid4(),
        span_id=uuid4(),
        body=WorkflowExecutionSnapshottedBody(
            workflow_definition=nested_workflow_class,
            state=nested_state,
        ),
        parent=WorkflowParentContext(
            span_id=uuid4(),
            workflow_definition=parent_workflow_class,
        ),
    )

    parent_event_passes = root_workflow_event_filter(parent_workflow_class, parent_snapshotted_event)
    nested_event_passes = root_workflow_event_filter(parent_workflow_class, nested_snapshotted_event)

    assert parent_event_passes is True

    assert nested_event_passes is False


def test_root_workflow_event_filter__includes_root_workflow_snapshotted_events():
    """
    Tests that root_workflow_event_filter includes snapshotted events from the root workflow.
    """

    workflow_class = ParentWorkflow

    workflow = ParentWorkflow()

    state = workflow.get_default_state(ParentInputs(value="test"))
    snapshotted_event: WorkflowExecutionSnapshottedEvent = WorkflowExecutionSnapshottedEvent(
        trace_id=uuid4(),
        span_id=uuid4(),
        body=WorkflowExecutionSnapshottedBody(
            workflow_definition=workflow_class,
            state=state,
        ),
        parent=None,
    )

    # WHEN we filter the event using root_workflow_event_filter
    event_passes = root_workflow_event_filter(workflow_class, snapshotted_event)

    assert event_passes is True
