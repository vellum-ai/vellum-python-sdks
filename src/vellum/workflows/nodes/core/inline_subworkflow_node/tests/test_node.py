import pytest

from vellum.workflows.errors.types import WorkflowErrorCode
from vellum.workflows.exceptions import NodeException
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.nodes.core.inline_subworkflow_node.node import InlineSubworkflowNode
from vellum.workflows.nodes.core.try_node.node import TryNode
from vellum.workflows.outputs.base import BaseOutput
from vellum.workflows.state.base import BaseState
from vellum.workflows.workflows.base import BaseWorkflow
from vellum.workflows.workflows.event_filters import all_workflow_event_filter


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


def test_inline_subworkflow_node__base_inputs_validation():
    """Test that InlineSubworkflowNode properly validates required inputs"""

    # GIVEN a real subworkflow class with a required input
    class SubworkflowInputs(BaseInputs):
        required_input: str  # This is a required field without a default

    class TestSubworkflow(BaseWorkflow[SubworkflowInputs, BaseState]):
        pass

    # AND a node that uses this subworkflow
    class TestNode(InlineSubworkflowNode):
        subworkflow = TestSubworkflow
        subworkflow_inputs = {"required_input": None}

    # WHEN we try to run the node
    node = TestNode()

    # THEN it should raise a NodeException
    with pytest.raises(NodeException) as e:
        list(node.run())

    # AND the error message should indicate the missing required input
    assert e.value.code == WorkflowErrorCode.INVALID_INPUTS
    assert "Required input variables required_input should have defined value" == str(e.value)


def test_inline_subworkflow_node__with_adornment():
    # GIVEN a simple inline subworkflow with an output
    class InnerNode(BaseNode):
        class Outputs(BaseNode.Outputs):
            final_output = "hello"

    class TestSubworkflow(BaseWorkflow):
        graph = InnerNode

        class Outputs(BaseWorkflow.Outputs):
            final_output = InnerNode.Outputs.final_output

    # AND it's wrapped in a TryNode
    @TryNode.wrap()
    class TestNode(InlineSubworkflowNode):
        subworkflow = TestSubworkflow

    # THEN the wrapped node should have the correct output IDs
    assert "final_output" in TestNode.__output_ids__

    # AND when we run the node
    node = TestNode()
    outputs = list(node.run())

    assert outputs[-1].name == "final_output" and outputs[-1].value == "hello"


@pytest.mark.skip(reason="Enable after we set is_dynamic on the subworkflow class")
def test_inline_subworkflow_node__is_dynamic_subworkflow():
    """Test that InlineSubworkflowNode sets is_dynamic=True on the subworkflow class"""

    # GIVEN a subworkflow class
    class TestSubworkflow(BaseWorkflow[BaseInputs, BaseState]):
        graph = MyInnerNode

        class Outputs(BaseWorkflow.Outputs):
            out = MyInnerNode.Outputs.out

    # AND a node that uses this subworkflow
    class TestNode(InlineSubworkflowNode):
        subworkflow = TestSubworkflow

    # AND a workflow that uses this node
    class TestWorkflow(BaseWorkflow[BaseInputs, BaseState]):
        graph = TestNode

        class Outputs(BaseWorkflow.Outputs):
            out = TestNode.Outputs.out

    # WHEN the workflow is executed
    workflow = TestWorkflow()
    events = list(workflow.stream(event_filter=all_workflow_event_filter))

    # AND we should find workflow execution initiated events
    initiated_events = [event for event in events if event.name == "workflow.execution.initiated"]
    assert len(initiated_events) == 2  # Main workflow + inline workflow

    assert initiated_events[0].body.workflow_definition.is_dynamic is False  # Main workflow
    assert initiated_events[1].body.workflow_definition.is_dynamic is True  # Inline workflow
