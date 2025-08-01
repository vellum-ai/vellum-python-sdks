import pytest
from copy import deepcopy
import json
from queue import Queue
from typing import Dict, List, cast

from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.outputs.base import BaseOutputs
from vellum.workflows.state.base import BaseState
from vellum.workflows.state.delta import SetStateDelta, StateDelta
from vellum.workflows.state.encoder import DefaultStateEncoder


@pytest.fixture()
def mock_deepcopy(mocker):
    return mocker.patch("vellum.workflows.state.base.deepcopy")


@pytest.fixture
def mock_logger(mocker):
    return mocker.patch("vellum.workflows.state.base.logger")


class MockState(BaseState):
    foo: str
    nested_dict: Dict[str, int] = {}

    __snapshot_count__: int = 0

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.__snapshot_callback__ = lambda _, __: self.__mock_snapshot__()

    def __mock_snapshot__(self) -> None:
        self.__snapshot_count__ += 1

    def __deepcopy__(self, memo: dict) -> "MockState":
        new_state = cast(MockState, super().__deepcopy__(memo))
        new_state.__snapshot_count__ = 0
        return new_state


class MockNode(BaseNode):
    class ExternalInputs(BaseNode.ExternalInputs):
        message: str

    class Outputs(BaseOutputs):
        baz: str


MOCK_NODE_OUTPUT_ID = "e4dc3136-0c27-4bda-b3ab-ea355d5219d6"


def test_state_snapshot__node_attribute_edit():
    # GIVEN an initial state instance
    state = MockState(foo="bar")
    assert state.__snapshot_count__ == 0

    # WHEN we edit an attribute
    state.foo = "baz"

    # THEN the snapshot is emitted
    assert state.__snapshot_count__ == 1


def test_state_snapshot__node_output_edit():
    # GIVEN an initial state instance
    state = MockState(foo="bar")
    assert state.__snapshot_count__ == 0

    # WHEN we add a Node Output to state
    for output in MockNode.Outputs:
        state.meta.node_outputs[output] = "hello"

    # THEN the snapshot is emitted
    assert state.__snapshot_count__ == 1


def test_state_snapshot__nested_dictionary_edit():
    # GIVEN an initial state instance
    state = MockState(foo="bar")
    assert state.__snapshot_count__ == 0

    # WHEN we edit a nested dictionary
    state.nested_dict["hello"] = 1

    # THEN the snapshot is emitted
    assert state.__snapshot_count__ == 1


def test_state_snapshot__external_input_edit():
    # GIVEN an initial state instance
    state = MockState(foo="bar")
    assert state.__snapshot_count__ == 0

    # WHEN we add an external input to state
    state.meta.external_inputs[MockNode.ExternalInputs.message] = "hello"

    # THEN the snapshot is emitted
    assert state.__snapshot_count__ == 1


def test_state_deepcopy():
    # GIVEN an initial state instance
    state = MockState(foo="bar")

    # AND we add a Node Output to state
    state.meta.node_outputs[MockNode.Outputs.baz] = "hello"

    # WHEN we deepcopy the state
    deepcopied_state = deepcopy(state)

    # THEN node outputs are deepcopied
    assert deepcopied_state.meta.node_outputs == state.meta.node_outputs


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
    assert state.__snapshot_count__ == 2

    # AND the copied state has had the correct number of snapshots
    assert deepcopied_state.__snapshot_count__ == 0


def test_state_json_serialization__with_node_output_updates():
    # GIVEN an initial state instance
    state = MockState(foo="bar")

    # AND we add a Node Output to state
    state.meta.node_outputs[MockNode.Outputs.baz] = "hello"

    # WHEN we serialize the state
    json_state = json.loads(json.dumps(state, cls=DefaultStateEncoder))

    # THEN the state is serialized correctly
    assert json_state["meta"]["node_outputs"] == {MOCK_NODE_OUTPUT_ID: "hello"}


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
    assert state.__snapshot_count__ == 2

    # AND the copied state has had the correct number of snapshots
    assert deepcopied_state.__snapshot_count__ == 0


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
    assert json_state["meta"]["node_outputs"] == {MOCK_NODE_OUTPUT_ID: ["test1", "test2"]}


def test_state_snapshot__deepcopy_fails__logs_error(mock_deepcopy, mock_logger):
    # GIVEN an initial state instance
    class MockState(BaseState):
        foo: str

    state = MockState(foo="bar")

    # AND we have a snapshot callback that we are tracking
    snapshot_count = 0

    def __snapshot_callback__(state: "BaseState", deltas: List[StateDelta]) -> None:
        nonlocal snapshot_count
        snapshot_count += 1

    state.__snapshot_callback__ = __snapshot_callback__

    # AND deepcopy fails the first time but succeeds the second time
    deepcopy_side_effect_count = 0

    def side_effect(*args, **kwargs):
        nonlocal deepcopy_side_effect_count
        deepcopy_side_effect_count += 1
        if deepcopy_side_effect_count == 1:
            raise Exception("Failed to deepcopy")
        return deepcopy(args[0])

    mock_deepcopy.side_effect = side_effect

    # WHEN we snapshot the state twice
    state.__snapshot__(SetStateDelta(name="foo", delta="bar"))
    state.__snapshot__(SetStateDelta(name="foo", delta="baz"))

    # THEN we were able to invoke the callback once
    assert snapshot_count == 1

    # AND alert sentry once
    assert mock_logger.exception.call_count == 1
