import time

from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.nodes.core.map_node.node import MapNode
from vellum.workflows.nodes.core.try_node.node import TryNode
from vellum.workflows.outputs.base import BaseOutput, BaseOutputs
from vellum.workflows.state.base import BaseState, StateMeta
from vellum.workflows.workflows.base import BaseWorkflow


def test_map_node__use_parent_inputs_and_state():
    # GIVEN a parent workflow Inputs and State
    class Inputs(BaseInputs):
        foo: str

    class State(BaseState):
        bar: str

    # AND a map node that is configured to use the parent's inputs and state
    @MapNode.wrap(items=[1, 2, 3])
    class TestNode(BaseNode):
        item = MapNode.SubworkflowInputs.item
        foo = Inputs.foo
        bar = State.bar

        class Outputs(BaseOutputs):
            value: str

        def run(self) -> Outputs:
            return self.Outputs(value=f"{self.foo} {self.bar} {self.item}")

    # WHEN the node is run
    node = TestNode(
        state=State(
            bar="bar",
            meta=StateMeta(workflow_inputs=Inputs(foo="foo")),
        )
    )
    outputs = list(node.run())

    # THEN the data is used successfully
    assert outputs[-1] == BaseOutput(name="value", value=["foo bar 1", "foo bar 2", "foo bar 3"])


def test_map_node__use_parallelism():
    # GIVEN a map node that is configured to use the parent's inputs and state
    @MapNode.wrap(items=list(range(10)))
    class TestNode(BaseNode):
        item = MapNode.SubworkflowInputs.item

        class Outputs(BaseOutputs):
            value: int

        def run(self) -> Outputs:
            time.sleep(0.03)
            return self.Outputs(value=self.item + 1)

    # WHEN the node is run
    node = TestNode(state=BaseState())
    start_ts = time.time_ns()
    node.run()
    end_ts = time.time_ns()

    # THEN the node should have ran in parallel
    run_time = (end_ts - start_ts) / 10**9
    assert run_time < 0.2


def test_map_node__empty_list():
    # GIVEN a map node that is configured to use the parent's inputs and state
    @MapNode.wrap(items=[])
    class TestNode(BaseNode):
        item = MapNode.SubworkflowInputs.item

        class Outputs(BaseOutputs):
            value: int

        def run(self) -> Outputs:
            time.sleep(0.03)
            return self.Outputs(value=self.item + 1)

    # WHEN the node is run
    node = TestNode()
    outputs = list(node.run())

    # THEN the node should return an empty output
    fulfilled_output = outputs[-1]
    assert fulfilled_output == BaseOutput(name="value", value=[])


def test_map_node__inner_try():
    # GIVEN a try wrapped node
    @TryNode.wrap()
    class InnerNode(BaseNode):
        class Outputs(BaseNode.Outputs):
            foo: str

    # AND a workflow using that node
    class SimpleMapNodeWorkflow(BaseWorkflow[MapNode.SubworkflowInputs, BaseState]):
        graph = InnerNode

        class Outputs(BaseWorkflow.Outputs):
            final_output = InnerNode.Outputs.foo

    # AND a map node referencing that workflow
    class SimpleMapNode(MapNode):
        items = ["hello", "world"]
        subworkflow = SimpleMapNodeWorkflow
        max_concurrency = 4

    # WHEN we run the workflow
    stream = SimpleMapNode().run()
    outputs = list(stream)

    # THEN the workflow should succeed
    assert outputs[-1].name == "final_output"
    assert len(outputs[-1].value) == 2
