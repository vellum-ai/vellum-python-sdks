from vellum.workflows.errors import WorkflowErrorCode
from vellum.workflows.exceptions import WorkflowInitializationException
from vellum.workflows.inputs import BaseInputs
from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.state import BaseState
from vellum.workflows.workflows.base import BaseWorkflow


class TestInputs(BaseInputs):
    test_input: str = "default_value"


class TestState(BaseState):
    test_field: str = "default_state"


class TestNode(BaseNode):
    def run(self):
        return self.Outputs()


class TestWorkflow(BaseWorkflow[TestInputs, TestState]):
    graph = TestNode


def test_workflow_initialization_exception_stream__with_inputs_and_state():
    """
    Tests that stream() method yields both initiated and rejected events with proper correlation.
    """
    exception = WorkflowInitializationException("Test initialization error")

    inputs = TestInputs(test_input="test_value")
    state = TestState(test_field="test_state")

    events = list(exception.stream(TestWorkflow, inputs, state))

    assert len(events) == 2

    initiated_event = events[0]
    assert initiated_event.name == "workflow.execution.initiated"
    assert initiated_event.body.workflow_definition == TestWorkflow
    assert initiated_event.body.inputs.test_input == "test_value"
    assert initiated_event.body.initial_state.test_field == "test_state"

    rejected_event = events[1]
    assert rejected_event.name == "workflow.execution.rejected"
    assert rejected_event.body.workflow_definition == TestWorkflow
    assert rejected_event.body.error.message == "Test initialization error"
    assert rejected_event.body.error.code == WorkflowErrorCode.INVALID_INPUTS

    assert initiated_event.trace_id == rejected_event.trace_id
    assert initiated_event.span_id == rejected_event.span_id


def test_workflow_initialization_exception_stream__with_defaults():
    """
    Tests that stream() method works with default inputs and no initial state.
    """
    exception = WorkflowInitializationException("Test error with defaults")

    events = list(exception.stream(TestWorkflow))

    assert len(events) == 2

    initiated_event = events[0]
    assert initiated_event.name == "workflow.execution.initiated"
    assert initiated_event.body.workflow_definition == TestWorkflow
    assert initiated_event.body.inputs.test_input == "default_value"
    assert initiated_event.body.initial_state is None

    rejected_event = events[1]
    assert rejected_event.name == "workflow.execution.rejected"
    assert rejected_event.body.error.message == "Test error with defaults"

    assert initiated_event.trace_id == rejected_event.trace_id
    assert initiated_event.span_id == rejected_event.span_id


def test_workflow_initialization_exception_stream__returns_workflow_event_generator():
    """
    Tests that stream() method returns a WorkflowEventGenerator with proper span_id.
    """
    exception = WorkflowInitializationException("Test generator")

    event_generator = exception.stream(TestWorkflow)

    from vellum.workflows.events.stream import WorkflowEventGenerator

    assert isinstance(event_generator, WorkflowEventGenerator)

    assert event_generator.span_id is not None

    events = list(event_generator)
    assert len(events) == 2
