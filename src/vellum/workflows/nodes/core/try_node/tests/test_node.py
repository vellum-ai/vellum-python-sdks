import pytest

from vellum.client import Vellum
from vellum.workflows.errors.types import WorkflowError, WorkflowErrorCode
from vellum.workflows.exceptions import NodeException
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.nodes.core.try_node.node import TryNode
from vellum.workflows.outputs import BaseOutputs
from vellum.workflows.outputs.base import BaseOutput
from vellum.workflows.state.base import BaseState, StateMeta
from vellum.workflows.state.context import WorkflowContext
from vellum.workflows.workflows.base import BaseWorkflow


def test_try_node__on_error_code__successfully_caught():
    # GIVEN a try node that is configured to catch PROVIDER_ERROR
    @TryNode.wrap(on_error_code=WorkflowErrorCode.PROVIDER_ERROR)
    class TestNode(BaseNode):
        class Outputs(BaseOutputs):
            value: int

        def run(self) -> Outputs:
            raise NodeException(message="This will be caught", code=WorkflowErrorCode.PROVIDER_ERROR)

    # WHEN the node is run and throws a PROVIDER_ERROR
    node = TestNode(state=BaseState())
    outputs = [o for o in node.run()]

    # THEN the exception is caught and returned
    assert len(outputs) == 2
    assert set(outputs) == {
        BaseOutput(name="value"),
        BaseOutput(
            name="error", value=WorkflowError(message="This will be caught", code=WorkflowErrorCode.PROVIDER_ERROR)
        ),
    }


def test_try_node__retry_on_error_code__missed():
    # GIVEN a try node that is configured to catch PROVIDER_ERROR
    @TryNode.wrap(on_error_code=WorkflowErrorCode.PROVIDER_ERROR)
    class TestNode(BaseNode):
        class Outputs(BaseOutputs):
            value: int

        def run(self) -> Outputs:
            raise NodeException(message="This will be missed", code=WorkflowErrorCode.INTERNAL_ERROR)

    # WHEN the node is run and throws a different exception
    node = TestNode(state=BaseState())
    with pytest.raises(NodeException) as exc_info:
        list(node.run())

    # THEN the exception is not caught
    assert exc_info.value.message == "Unexpected rejection: INTERNAL_ERROR.\nMessage: This will be missed"
    assert exc_info.value.code == WorkflowErrorCode.INVALID_OUTPUTS


def test_try_node__use_parent_inputs_and_state():
    # GIVEN a parent workflow Inputs and State
    class Inputs(BaseInputs):
        foo: str

    class State(BaseState):
        bar: str

    # AND a try node that uses the parent's inputs and state
    @TryNode.wrap()
    class TestNode(BaseNode):
        foo = Inputs.foo
        bar = State.bar

        class Outputs(BaseOutputs):
            value: str

        def run(self) -> Outputs:
            return self.Outputs(value=f"{self.foo} {self.bar}")

    # WHEN the node is run
    node = TestNode(
        state=State(
            bar="bar",
            meta=StateMeta(workflow_inputs=Inputs(foo="foo")),
        ),
    )
    outputs = list(node.run())

    # THEN the data is used successfully
    assert len(outputs) == 1
    assert outputs[-1] == BaseOutput(name="value", value="foo bar")


def test_try_node__use_parent_execution_context():
    # GIVEN a try node that uses node context to use the vellum client
    @TryNode.wrap()
    class TestNode(BaseNode):
        class Outputs(BaseOutputs):
            key: str

        def run(self) -> Outputs:
            return self.Outputs(key=self._context.vellum_client.ad_hoc._client_wrapper.api_key)

    # WHEN the node is run with a custom vellum client
    node = TestNode(
        context=WorkflowContext(
            vellum_client=Vellum(api_key="test-key"),
        )
    )
    outputs = list(node.run())

    # THEN the inner node had access to the key
    assert len(outputs) == 1
    assert outputs[-1] == BaseOutput(name="key", value="test-key")


def test_try_node__resolved_inputs():
    """
    This test ensures that node attributes of TryNodes are correctly resolved.
    """

    class State(BaseState):
        counter = 3.0

    @TryNode.wrap()
    class MyNode(BaseNode[State]):
        foo = State.counter

    assert MyNode.foo.types == (float,)


def test_try_node__nested_try():
    """
    Ensure that the nested try node doesn't affect the outer try node's outputs
    """

    # GIVEN a nested try node
    @TryNode.wrap()
    class InnerNode(BaseNode):
        class Outputs:
            foo = "hello"

    # AND a subworkflow
    class Subworkflow(BaseWorkflow):
        graph = InnerNode

        class Outputs(BaseWorkflow.Outputs):
            bar = InnerNode.Outputs.foo

    # AND an outer try node referencing that subworkflow
    class OuterNode(TryNode):
        subworkflow = Subworkflow

    # WHEN we run the try node
    stream = OuterNode().run()
    events = list(stream)

    # THEN we only have the outer node's outputs
    valid_events = [e for e in events if e.name == "bar"]
    assert len(valid_events) == len(events)
