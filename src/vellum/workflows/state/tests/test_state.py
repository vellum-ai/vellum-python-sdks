import pytest
from copy import deepcopy
import json
from queue import Queue
import threading
from typing import Any, Dict, List, Optional, cast

from pydantic import Field

from vellum import ChatMessage
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


def test_state_deepcopy_handles_generator_in_node_outputs():
    """
    Tests that deepcopy handles generator objects in node outputs without raising TypeError.
    """

    def sample_generator():
        yield 1
        yield 2

    # GIVEN a state with a generator in node outputs
    state = MockState(foo="bar")
    gen = sample_generator()
    state.meta.node_outputs[MockNode.Outputs.baz] = gen

    # WHEN we deepcopy the state
    deepcopied_state = deepcopy(state)

    # THEN the deepcopy succeeds and the generator is preserved by reference
    assert deepcopied_state.meta.node_outputs[MockNode.Outputs.baz] is gen


def test_state_deepcopy_handles_generator_in_external_inputs():
    """
    Tests that deepcopy handles generator objects in external inputs without raising TypeError.
    """

    def sample_generator():
        yield "a"
        yield "b"

    # GIVEN a state with a generator in external inputs
    state = MockState(foo="bar")
    gen = sample_generator()
    state.meta.external_inputs[MockNode.ExternalInputs.message] = gen

    # WHEN we deepcopy the state
    deepcopied_state = deepcopy(state)

    # THEN the deepcopy succeeds and the generator is preserved by reference
    assert deepcopied_state.meta.external_inputs[MockNode.ExternalInputs.message] is gen


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


class BlockingValue:
    """A value that blocks during deepcopy until signaled to proceed."""

    def __init__(self, entered_event: threading.Event, proceed_event: threading.Event):
        self.entered_event = entered_event
        self.proceed_event = proceed_event

    def __deepcopy__(self, memo: Any) -> "BlockingValue":
        self.entered_event.set()
        self.proceed_event.wait(timeout=5.0)
        return BlockingValue(self.entered_event, self.proceed_event)


def test_state_snapshot__concurrent_mutation_during_deepcopy():
    """Test that concurrent mutations during deepcopy don't cause RuntimeError."""

    # GIVEN a state with a dict containing a blocking value
    class TestState(BaseState):
        data: Dict[str, Any] = Field(default_factory=dict)

    state = TestState()

    entered_event = threading.Event()
    proceed_event = threading.Event()
    state.data["blocking"] = BlockingValue(entered_event, proceed_event)
    state.data["other"] = "value"

    snapshot_exception: List[Exception] = []
    mutation_completed = threading.Event()

    def snapshot_thread_fn() -> None:
        try:
            with state.__lock__:
                deepcopy(state)
        except Exception as e:
            snapshot_exception.append(e)

    def mutation_thread_fn() -> None:
        state.data["new_key"] = "new_value"
        mutation_completed.set()

    # WHEN we start a snapshot (deepcopy) in one thread
    snapshot_thread = threading.Thread(target=snapshot_thread_fn)
    snapshot_thread.start()

    # AND wait for the deepcopy to be in progress (blocked on our blocking value)
    entered_event.wait(timeout=5.0)

    # AND try to mutate the dict from another thread
    mutation_thread = threading.Thread(target=mutation_thread_fn)
    mutation_thread.start()

    # THEN the mutation should block waiting for the lock (not complete immediately)
    mutation_completed.wait(timeout=0.2)
    mutation_blocked = not mutation_completed.is_set()

    # AND when we allow the deepcopy to proceed
    proceed_event.set()
    snapshot_thread.join(timeout=5.0)
    mutation_thread.join(timeout=5.0)

    # THEN the mutation should have been blocked by the lock
    assert mutation_blocked, "Mutation should block while deepcopy holds the lock"

    # AND no exception should have been raised during snapshot
    assert len(snapshot_exception) == 0, f"Snapshot raised exception: {snapshot_exception}"


def test_state_deepcopy__cloned_state_uses_own_snapshot_callback():
    """Test that deepcopied state's snapshottable containers use the clone's callback."""

    # GIVEN a state with a snapshottable dict attribute
    original_snapshot_count = 0
    clone_snapshot_count = 0

    class TestState(BaseState):
        data: Dict[str, int] = Field(default_factory=dict)

    state = TestState()
    state.data["key1"] = 1

    def original_callback(state_copy: BaseState, deltas: List[StateDelta]) -> None:
        nonlocal original_snapshot_count
        original_snapshot_count += 1

    state.__snapshot_callback__ = original_callback

    # WHEN we deepcopy the state
    cloned_state = deepcopy(state)

    def clone_callback(state_copy: BaseState, deltas: List[StateDelta]) -> None:
        nonlocal clone_snapshot_count
        clone_snapshot_count += 1

    cloned_state.__snapshot_callback__ = clone_callback

    # AND reset counters
    original_snapshot_count = 0
    clone_snapshot_count = 0

    # AND mutate the cloned state's snapshottable dict
    cloned_state.data["key2"] = 2

    # THEN only the clone's callback should be invoked
    assert clone_snapshot_count == 1, "Clone's callback should be invoked"
    assert original_snapshot_count == 0, "Original's callback should not be invoked"


def test_state_snapshot__top_level_attribute_assignment_blocks_during_deepcopy():
    """Test that top-level attribute assignments block while deepcopy holds the lock."""

    # GIVEN a state with a blocking value in a dict attribute
    class TestState(BaseState):
        data: Dict[str, Any] = Field(default_factory=dict)
        counter: int = 0

    state = TestState()

    entered_event = threading.Event()
    proceed_event = threading.Event()
    state.data["blocking"] = BlockingValue(entered_event, proceed_event)

    mutation_completed = threading.Event()

    def snapshot_thread_fn() -> None:
        with state.__lock__:
            deepcopy(state)

    def mutation_thread_fn() -> None:
        state.__is_quiet__ = True
        state.counter = 42
        mutation_completed.set()

    # WHEN we start a snapshot (deepcopy) in one thread
    snapshot_thread = threading.Thread(target=snapshot_thread_fn)
    snapshot_thread.start()

    # AND wait for the deepcopy to be in progress (blocked on our blocking value)
    entered_event.wait(timeout=5.0)

    # AND try to assign a top-level attribute from another thread
    mutation_thread = threading.Thread(target=mutation_thread_fn)
    mutation_thread.start()

    # THEN the mutation should block waiting for the lock (not complete immediately)
    mutation_completed.wait(timeout=0.2)
    mutation_blocked = not mutation_completed.is_set()

    # AND when we allow the deepcopy to proceed
    proceed_event.set()
    snapshot_thread.join(timeout=5.0)
    mutation_thread.join(timeout=5.0)

    # THEN the mutation should have been blocked by the lock
    assert mutation_blocked, "Top-level attribute assignment should block while deepcopy holds the lock"


def test_base_state_chat_history_with_default_factory_initializes_to_list():
    """
    Tests that a chat_history state variable with Optional[list[ChatMessage]] = Field(default_factory=list)
    initializes to an empty list instead of None.
    """

    # GIVEN a state class with chat_history using Field(default_factory=list)
    class TestState(BaseState):
        chat_history: Optional[List[ChatMessage]] = Field(default_factory=list)  # type: ignore[arg-type]

    # WHEN we create a state instance without providing a value
    state = TestState()

    # THEN the chat_history should be an empty list, not None
    assert state.chat_history is not None
    assert isinstance(state.chat_history, list)
    assert state.chat_history == []

    # AND we should be able to append ChatMessage objects to it
    chat_history = state.chat_history
    chat_history.append(ChatMessage(role="USER", text="Hello"))
    assert len(chat_history) == 1
    assert chat_history[0].role == "USER"
    assert chat_history[0].text == "Hello"


def test_base_state_chat_history_with_default_factory_creates_separate_instances():
    """
    Tests that Field(default_factory=list) creates separate list instances for each state,
    avoiding the mutable default argument issue.
    """

    # GIVEN a state class with chat_history using Field(default_factory=list)
    class TestState(BaseState):
        chat_history: Optional[List[ChatMessage]] = Field(default_factory=list)  # type: ignore[arg-type]

    # WHEN we create two state instances
    state1 = TestState()
    state2 = TestState()

    # THEN they should have separate list instances
    assert state1.chat_history is not state2.chat_history

    # AND modifying one should not affect the other
    chat_history1 = state1.chat_history
    chat_history2 = state2.chat_history
    assert chat_history1 is not None
    assert chat_history2 is not None
    chat_history1.append(ChatMessage(role="USER", text="Message 1"))
    chat_history2.append(ChatMessage(role="ASSISTANT", text="Message 2"))

    assert len(chat_history1) == 1
    assert len(chat_history2) == 1
    assert chat_history1[0].text == "Message 1"
    assert chat_history2[0].text == "Message 2"
