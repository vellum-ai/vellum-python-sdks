from uuid import UUID, uuid4

from vellum.workflows import BaseWorkflow
from vellum.workflows.context import execution_context, get_execution_context
from vellum.workflows.events.types import NodeParentContext, WorkflowParentContext
from vellum.workflows.inputs import BaseInputs
from vellum.workflows.nodes import BaseNode
from vellum.workflows.references import VellumSecretReference
from vellum.workflows.state import BaseState


class MockInputs(BaseInputs):
    foo: str


class MockNode(BaseNode):
    node_foo = MockInputs.foo
    node_secret = VellumSecretReference("secret")

    class Outputs(BaseNode.Outputs):
        example: str


class MockWorkflow(BaseWorkflow[MockInputs, BaseState]):
    graph = MockNode


def test_context_trace_and_parent(mock_uuid4_generator):
    trace_id_generator = mock_uuid4_generator("vellum.workflows.context.uuid4")
    trace_id = trace_id_generator()
    second_trace_id = trace_id_generator()
    parent_context = NodeParentContext(
        node_definition=MockNode,
        span_id=UUID("123e4567-e89b-12d3-a456-426614174000"),
        parent=WorkflowParentContext(
            workflow_definition=MockWorkflow,
            span_id=UUID("123e4567-e89b-12d3-a456-426614174000"),
        ),
    )
    second_parent_context = WorkflowParentContext(
        workflow_definition=MockWorkflow, span_id=uuid4(), parent=parent_context
    )
    # When using execution context , if we set trace id within
    with execution_context(parent_context=parent_context):
        test = get_execution_context()
        assert test
        assert test.trace_id == trace_id
        assert test.parent_context == parent_context
        with execution_context(parent_context=second_parent_context):
            test1 = get_execution_context()
            assert test1
            assert test1.trace_id == trace_id
            assert test1.parent_context == second_parent_context
            # then we can assume trace id will not change
            with execution_context():
                test3 = get_execution_context()
                assert test3
                assert test3.trace_id == trace_id
            with execution_context(parent_context=parent_context):
                test3 = get_execution_context()
                assert test3
                assert test3.trace_id == trace_id
    # and if we have a new context, the trace will differ
    with execution_context(parent_context=parent_context):
        test = get_execution_context()
        assert test
        assert test.trace_id == second_trace_id, trace_id
