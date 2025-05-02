import datetime
import threading
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


def test_map_node__nested_map_node():
    # GIVEN the inner map node's inputs
    class VegetableMapNodeInputs(MapNode.SubworkflowInputs):
        item: str

    # AND the outer map node's inputs
    class FruitMapNodeInputs(MapNode.SubworkflowInputs):
        item: str

    # AND a simple node that concats both attributes
    class SimpleConcatNode(BaseNode):
        fruit = FruitMapNodeInputs.item
        vegetable = VegetableMapNodeInputs.item

        class Outputs(BaseNode.Outputs):
            medley: str

        def run(self) -> Outputs:
            return self.Outputs(medley=f"{self.fruit} {self.vegetable}")

    # AND a workflow using that node
    class VegetableMapNodeWorkflow(BaseWorkflow[VegetableMapNodeInputs, BaseState]):
        graph = SimpleConcatNode

        class Outputs(BaseWorkflow.Outputs):
            final_output = SimpleConcatNode.Outputs.medley

    # AND an inner map node referencing that workflow
    class VegetableMapNode(MapNode):
        items = ["carrot", "potato"]
        subworkflow = VegetableMapNodeWorkflow

    # AND an outer subworkflow referencing the inner map node
    class FruitMapNodeWorkflow(BaseWorkflow[FruitMapNodeInputs, BaseState]):
        graph = VegetableMapNode

        class Outputs(BaseWorkflow.Outputs):
            final_output = VegetableMapNode.Outputs.final_output

    # AND an outer map node referencing the outer subworkflow
    class FruitMapNode(MapNode):
        items = ["apple", "banana"]
        subworkflow = FruitMapNodeWorkflow

    # WHEN we run the workflow
    stream = FruitMapNode().run()
    outputs = list(stream)

    # THEN the workflow should succeed
    assert outputs[-1].name == "final_output"
    assert outputs[-1].value == [
        ["apple carrot", "apple potato"],
        ["banana carrot", "banana potato"],
    ]


def test_map_node_parallel_execution_with_workflow():
    # TODO: Find a better way to test this such that it represents what a user would see.
    # https://linear.app/vellum/issue/APO-482/find-a-better-way-to-test-concurrency-with-map-nodes
    thread_ids = {}

    # GIVEN a series of nodes that simulate work
    class BaseNode1(BaseNode):
        item = MapNode.SubworkflowInputs.item

        class Outputs(BaseOutputs):
            output: str
            thread_id: int

        def run(self) -> Outputs:
            current_thread_id = threading.get_ident()
            thread_ids[self.item] = current_thread_id

            # Simulate work
            time.sleep(0.1)

            end = time.time()
            end_str = datetime.datetime.fromtimestamp(end).strftime("%Y-%m-%d %H:%M:%S.%f")

            return self.Outputs(output=end_str, thread_id=current_thread_id)

    # AND a workflow that connects these nodes
    class TestWorkflow(BaseWorkflow[MapNode.SubworkflowInputs, BaseState]):
        graph = BaseNode1

        class Outputs(BaseWorkflow.Outputs):
            final_output = BaseNode1.Outputs.output
            thread_id = BaseNode1.Outputs.thread_id

    # AND a map node that uses this workflow
    class TestMapNode(MapNode):
        items = [1, 2, 3]
        subworkflow = TestWorkflow

    # WHEN we run the map node
    node = TestMapNode()
    list(node.run())

    # AND each item should have run on a different thread
    thread_ids_list = list(thread_ids.values())
    assert len(set(thread_ids_list)) == 3
