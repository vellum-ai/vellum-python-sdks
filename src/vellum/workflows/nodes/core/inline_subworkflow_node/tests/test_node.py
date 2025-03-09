import pytest

from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.nodes.core.inline_subworkflow_node.node import InlineSubworkflowNode
from vellum.workflows.nodes.core.try_node.node import TryNode
from vellum.workflows.outputs.base import BaseOutput
from vellum.workflows.state.base import BaseState
from vellum.workflows.workflows.base import BaseWorkflow


class Inputs(BaseInputs):
    foo: str


class MyInnerNode(BaseNode):
    class Outputs(BaseNode.Outputs):
        out = Inputs.foo


class MySubworkflow(BaseWorkflow[Inputs, BaseState]):
    graph = MyInnerNode

    class Outputs(BaseWorkflow.Outputs):
        out = MyInnerNode.Outputs.out


@pytest.mark.parametrize("inputs", [{"foo": "bar"}, Inputs(foo="bar")])
def test_inline_subworkflow_node__inputs(inputs):
    # GIVEN a node setup with subworkflow inputs
    class MyNode(InlineSubworkflowNode):
        subworkflow = MySubworkflow
        subworkflow_inputs = inputs

    # WHEN the node is run
    node = MyNode()
    events = list(node.run())

    # THEN the output is as expected
    assert events == [
        BaseOutput(name="out", value="bar"),
    ]


def test_inline_subworkflow_node__support_inputs_as_attributes():
    # GIVEN a node setup with subworkflow inputs
    class MyNode(InlineSubworkflowNode):
        subworkflow = MySubworkflow
        foo = "bar"

    # WHEN the node is run
    node = MyNode()
    events = list(node.run())

    # THEN the output is as expected
    assert events == [
        BaseOutput(name="out", value="bar"),
    ]


def test_inline_subworkflow_node__nested_try():
    """
    Ensure that the nested try node doesn't affect the subworkflow node's outputs
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
    class OuterNode(InlineSubworkflowNode):
        subworkflow = Subworkflow

    # WHEN we run the try node
    stream = OuterNode().run()
    events = list(stream)

    # THEN we only have the outer node's outputs
    valid_events = [e for e in events if e.name == "bar"]
    assert len(valid_events) == len(events)
