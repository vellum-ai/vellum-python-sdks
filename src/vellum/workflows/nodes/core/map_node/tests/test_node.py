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


def test_map_node_serial_execution_with_max_concurrency_1():
    # GIVEN a map node with max_concurrency=1 that should enforce serial execution
    execution_times = []
    thread_ids = []

    class SerialTestNode(BaseNode):
        item = MapNode.SubworkflowInputs.item

        class Outputs(BaseOutputs):
            output: str
            thread_id: int

        def run(self) -> Outputs:
            start_time = time.time()
            current_thread_id = threading.get_ident()
            thread_ids.append(current_thread_id)

            # Simulate work with a meaningful delay
            time.sleep(0.1)

            end_time = time.time()
            execution_times.append((self.item, start_time, end_time))

            return self.Outputs(output=f"item_{self.item}", thread_id=current_thread_id)

    # AND a workflow that connects these nodes
    class SerialTestWorkflow(BaseWorkflow[MapNode.SubworkflowInputs, BaseState]):
        graph = SerialTestNode

        class Outputs(BaseWorkflow.Outputs):
            final_output = SerialTestNode.Outputs.output
            thread_id = SerialTestNode.Outputs.thread_id

    # AND a map node with max_concurrency=1
    class SerialMapNode(MapNode):
        items = [1, 2, 3]
        max_concurrency = 1
        subworkflow = SerialTestWorkflow

    # WHEN we run the map node
    node = SerialMapNode()
    start_total = time.time()
    list(node.run())
    end_total = time.time()

    unique_threads = set(thread_ids)
    assert len(unique_threads) == 1, f"Expected 1 thread, got {len(unique_threads)} threads: {unique_threads}"

    for i in range(1, len(execution_times)):
        prev_item, prev_start, prev_end = execution_times[i - 1]
        curr_item, curr_start, curr_end = execution_times[i]

        assert (
            curr_start >= prev_end - 0.01
        ), f"Task {curr_item} started at {curr_start} before task {prev_item} ended at {prev_end}"

    total_time = end_total - start_total
    expected_min_time = len(execution_times) * 0.1  # 0.1s per task
    assert (
        total_time >= expected_min_time - 0.05
    ), f"Total time {total_time} too short for serial execution, expected at least {expected_min_time}"


def test_map_node_event_ordering_with_max_concurrency_1():
    # GIVEN a map node with max_concurrency=1 that should process events in order
    execution_order = []

    class EventOrderTestNode(BaseNode):
        item = MapNode.SubworkflowInputs.item

        class Outputs(BaseOutputs):
            output: str

        def run(self) -> Outputs:
            execution_order.append(self.item)
            # Simulate variable work time to potentially expose race conditions
            time.sleep(0.05 + (self.item * 0.02))
            return self.Outputs(output=f"processed_{self.item}")

    class EventOrderTestWorkflow(BaseWorkflow[MapNode.SubworkflowInputs, BaseState]):
        graph = EventOrderTestNode

        class Outputs(BaseWorkflow.Outputs):
            final_output = EventOrderTestNode.Outputs.output

    class EventOrderMapNode(MapNode):
        items = [1, 2, 3, 4, 5]
        max_concurrency = 1
        subworkflow = EventOrderTestWorkflow

    # WHEN we run the map node and capture events
    node = EventOrderMapNode()
    outputs = list(node.run())

    final_outputs = [output for output in outputs if hasattr(output, "value") and isinstance(output.value, list)]

    assert execution_order == [1, 2, 3, 4, 5], f"Expected serial execution order [1, 2, 3, 4, 5], got {execution_order}"

    assert len(final_outputs) == 1, f"Expected 1 final output, got {len(final_outputs)}"
    final_output_values = final_outputs[0].value
    expected_values = ["processed_1", "processed_2", "processed_3", "processed_4", "processed_5"]
    assert final_output_values == expected_values, f"Expected {expected_values}, got {final_output_values}"
