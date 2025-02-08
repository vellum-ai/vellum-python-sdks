import pytest
from collections import defaultdict
from copy import deepcopy
import json
from queue import Queue
from typing import Dict

from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.outputs.base import BaseOutputs
from vellum.workflows.state.base import BaseState
from vellum.workflows.state.encoder import DefaultStateEncoder

snapshot_count: Dict[int, int] = defaultdict(int)


class MockState(BaseState):
    foo: str
    nested_dict: Dict[str, int] = {}

    def __snapshot__(self) -> None:
        global snapshot_count
        snapshot_count[id(self)] += 1


class MockNode(BaseNode):
    class ExternalInputs(BaseNode.ExternalInputs):
        message: str

    class Outputs(BaseOutputs):
        baz: str


def test_state_snapshot__node_attribute_edit():
    # GIVEN an initial state instance
    state = MockState(foo="bar")
    assert snapshot_count[id(state)] == 0

    # WHEN we edit an attribute
    state.foo = "baz"

    # THEN the snapshot is emitted
    assert snapshot_count[id(state)] == 1


def test_state_snapshot__node_output_edit():
    # GIVEN an initial state instance
    state = MockState(foo="bar")
    assert snapshot_count[id(state)] == 0

    # WHEN we add a Node Output to state
    for output in MockNode.Outputs:
        state.meta.node_outputs[output] = "hello"

    # THEN the snapshot is emitted
    assert snapshot_count[id(state)] == 1


def test_state_snapshot__nested_dictionary_edit():
    # GIVEN an initial state instance
    state = MockState(foo="bar")
    assert snapshot_count[id(state)] == 0

    # WHEN we edit a nested dictionary
    state.nested_dict["hello"] = 1

    # THEN the snapshot is emitted
    assert snapshot_count[id(state)] == 1


def test_state_snapshot__external_input_edit():
    # GIVEN an initial state instance
    state = MockState(foo="bar")
    assert snapshot_count[id(state)] == 0

    # WHEN we add an external input to state
    state.meta.external_inputs[MockNode.ExternalInputs.message] = "hello"

    # THEN the snapshot is emitted
    assert snapshot_count[id(state)] == 1


def test_state_deepcopy():
    # GIVEN an initial state instance
    state = MockState(foo="bar")

    # AND we add a Node Output to state
    state.meta.node_outputs[MockNode.Outputs.baz] = "hello"

    # WHEN we deepcopy the state
    deepcopied_state = deepcopy(state)

    # THEN node outputs are deepcopied
    assert deepcopied_state.meta.node_outputs == state.meta.node_outputs


@pytest.mark.skip(reason="https://app.shortcut.com/vellum/story/5654")
def test_state_deepcopy__with_node_output_updates():
    # GIVEN an initial state instance
    state = MockState(foo="bar")

    # AND we add a Node Output to state
    state.meta.node_outputs[MockNode.Outputs.baz] = "hello"

    # AND we deepcopy the state
    deepcopied_state = deepcopy(state)

    # AND we update the original state
    state.meta.node_outputs[MockNode.Outputs.baz] = "world"

    # THEN the copied state is not updated
    assert deepcopied_state.meta.node_outputs[MockNode.Outputs.baz] == "hello"

    # AND the original state has had the correct number of snapshots
    assert snapshot_count[id(state)] == 2

    # AND the copied state has had the correct number of snapshots
    assert snapshot_count[id(deepcopied_state)] == 0


def test_state_json_serialization__with_node_output_updates():
    # GIVEN an initial state instance
    state = MockState(foo="bar")

    # AND we add a Node Output to state
    state.meta.node_outputs[MockNode.Outputs.baz] = "hello"

    # WHEN we serialize the state
    json_state = json.loads(json.dumps(state, cls=DefaultStateEncoder))

    # THEN the state is serialized correctly
    assert json_state["meta"]["node_outputs"] == {"MockNode.Outputs.baz": "hello"}


def test_state_deepcopy__with_external_input_updates():
    # GIVEN an initial state instance
    state = MockState(foo="bar")

    # AND we add an external input to state
    state.meta.external_inputs[MockNode.ExternalInputs.message] = "hello"

    # AND we deepcopy the state
    deepcopied_state = deepcopy(state)

    # AND we update the original state
    state.meta.external_inputs[MockNode.ExternalInputs.message] = "world"

    # THEN the copied state is not updated
    assert deepcopied_state.meta.external_inputs[MockNode.ExternalInputs.message] == "hello"

    # AND the original state has had the correct number of snapshots
    assert snapshot_count[id(state)] == 2

    # AND the copied state has had the correct number of snapshots
    assert snapshot_count[id(deepcopied_state)] == 0


def test_state_json_serialization__with_queue():
    # GIVEN an initial state instance
    state = MockState(foo="bar")

    # AND we add a Node Output queue to state
    queue: Queue[str] = Queue()
    queue.put("test1")
    queue.put("test2")

    state.meta.node_outputs[MockNode.Outputs.baz] = queue

    # WHEN we serialize the state
    json_state = json.loads(json.dumps(state, cls=DefaultStateEncoder))

    # THEN the state is serialized correctly with the queue turned into a list
    assert json_state["meta"]["node_outputs"] == {"MockNode.Outputs.baz": ["test1", "test2"]}
