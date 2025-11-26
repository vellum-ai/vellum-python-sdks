import pytest
from copy import deepcopy
import json
from queue import Queue
from typing import Dict, List, cast

from pydantic import Field

from vellum.utils.json_encoder import VellumJsonEncoder
from vellum.workflows.constants import undefined
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.outputs.base import BaseOutputs
from vellum.workflows.state.base import BaseState
from vellum.workflows.state.delta import SetStateDelta, StateDelta
from vellum.workflows.types.code_execution_node_wrappers import DictWrapper


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


MOCK_NODE_OUTPUT_ID = "a864331d-9b1c-43db-90e7-6b1998d8179d"


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
    json_state = json.loads(json.dumps(state, cls=VellumJsonEncoder))

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
    json_state = json.loads(json.dumps(state, cls=VellumJsonEncoder))

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


def test_state_deepcopy_handles_undefined_values():
    # GIVEN a state with undefined values in node outputs
    state = MockState(foo="bar")
    state.meta.node_outputs[MockNode.Outputs.baz] = DictWrapper({"foo": undefined})

    # WHEN we deepcopy the state
    deepcopied_state = deepcopy(state)

    # THEN the undefined values are preserved
    assert deepcopied_state.meta.node_outputs[MockNode.Outputs.baz] == {"foo": undefined}


def test_base_state_initializes_field_with_default_factory():
    """Test that BaseState properly initializes fields with Field(default_factory=...)."""

    # GIVEN a state class with fields using Field(default_factory=...)
    class TestState(BaseState):
        chat_history: List[str] = Field(default_factory=list)
        items: Dict[str, int] = Field(default_factory=dict)
        counter: int = Field(default_factory=lambda: 0)

    # WHEN we create a state instance without providing values
    state = TestState()

    # THEN the fields should be initialized with the factory results, not FieldInfo objects
    assert isinstance(state.chat_history, list)
    assert state.chat_history == []
    assert isinstance(state.items, dict)
    assert state.items == {}
    assert isinstance(state.counter, int)
    assert state.counter == 0

    # AND we should be able to modify them
    state.chat_history.append("message1")
    state.items["key1"] = 1
    state.counter += 1

    assert state.chat_history == ["message1"]
    assert state.items == {"key1": 1}
    assert state.counter == 1


def test_base_state_field_with_default_factory_creates_separate_instances():
    """Test that Field(default_factory=...) creates separate instances for each state."""

    # GIVEN a state class with Field(default_factory=list)
    class TestState(BaseState):
        items: List[str] = Field(default_factory=list)

    # WHEN we create two state instances
    state1 = TestState()
    state2 = TestState()

    # THEN they should have separate list instances
    assert state1.items is not state2.items

    # AND modifying one should not affect the other
    state1.items.append("item1")
    assert state1.items == ["item1"]
    assert state2.items == []
