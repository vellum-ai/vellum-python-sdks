from uuid import uuid4

from vellum.workflows import BaseWorkflow
from vellum.workflows.context import ExecutionContext
from vellum.workflows.events import NodeExecutionFulfilledEvent, NodeExecutionInitiatedEvent
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.runner.runner import WorkflowRunner
from vellum.workflows.state.base import BaseState


class TestInputs(BaseInputs):
    pass


class TestState(BaseState):
    pass


class TestNode(BaseNode[TestState]):
    class Outputs(BaseNode.Outputs):
        result: str

    def run(self) -> "TestNode.Outputs":
        return self.Outputs(result="test_output")


class TestWorkflow(BaseWorkflow[TestInputs, TestState]):
    graph = TestNode

    class Outputs(BaseWorkflow.Outputs):
        result: str


def test_run_node_emits_correct_events():
    """Test that run_node method emits the expected events."""
    state = TestState()
    node = TestNode(state=state)
    span_id = uuid4()
    execution_context = ExecutionContext()

    workflow = TestWorkflow()
    runner = WorkflowRunner(workflow=workflow)

    events = list(runner.run_node(node=node, span_id=span_id, execution_context=execution_context))

    assert len(events) == 2
    assert isinstance(events[0], NodeExecutionInitiatedEvent)
    assert isinstance(events[1], NodeExecutionFulfilledEvent)
    assert events[0].span_id == span_id
    assert events[1].span_id == span_id
    assert events[1].body.outputs.result == "test_output"
