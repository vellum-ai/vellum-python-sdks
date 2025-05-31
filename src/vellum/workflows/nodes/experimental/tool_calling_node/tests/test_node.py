import pytest
from typing import Any, List

from vellum.client.types.chat_message import ChatMessage
from vellum.client.types.function_call import FunctionCall
from vellum.client.types.function_call_vellum_value import FunctionCallVellumValue
from vellum.workflows.exceptions import NodeException
from vellum.workflows.nodes.experimental.tool_calling_node.utils import create_function_node, create_tool_router_node
from vellum.workflows.state.base import BaseState, StateMeta


def first_function() -> str:
    return "first_function"


def second_function() -> str:
    return "second_function"


def test_port_condition_match_function_name():
    """
    Test that the port condition correctly matches the function name.
    """
    # GIVEN a tool router node
    router_node = create_tool_router_node(
        ml_model="test-model",
        blocks=[],
        functions=[first_function, second_function],
        prompt_inputs=None,
    )

    # AND a state with a function call to the first function
    state = BaseState(
        meta=StateMeta(
            node_outputs={
                router_node.Outputs.results: [
                    FunctionCallVellumValue(
                        value=FunctionCall(
                            arguments={}, id="call_zp7pBQjGAOBCr7lo0AbR1HXT", name="first_function", state="FULFILLED"
                        ),
                    )
                ],
            },
        )
    )

    # WHEN the port condition is resolved
    # THEN the first function port should be true
    first_function_port = getattr(router_node.Ports, "first_function")
    assert first_function_port.resolve_condition(state) is True

    # AND the second function port should be false
    second_function_port = getattr(router_node.Ports, "second_function")
    assert second_function_port.resolve_condition(state) is False

    # AND the default port should be false
    default_port = getattr(router_node.Ports, "default")
    assert default_port.resolve_condition(state) is False


def my_string_function() -> str:
    return "hello"


def my_error_function() -> int:
    return "hello"  # type: ignore


def my_untyped_function():
    return "hello"


class State(BaseState):
    chat_history: List[ChatMessage] = []


def test_function_node_output_type_untyped():
    """
    Test that the function node runs successfully when function returns expected type.
    """

    # GIVEN a tool router node and function node
    router_node = create_tool_router_node(
        ml_model="test-model",
        blocks=[],
        functions=[my_untyped_function],
        prompt_inputs=None,
    )

    function_node_class = create_function_node(my_untyped_function, router_node)
    assert function_node_class.get_output_type() == Any

    # AND a state with function call results
    state = State()

    # WHEN we run the function node
    function_node = function_node_class(state=state)
    outputs = function_node.run()

    # THEN it should execute successfully
    assert outputs is not None


def test_function_node_output_type_inference():
    """
    Test that the function node runs successfully when function returns expected type.
    """

    # GIVEN a tool router node and function node
    router_node = create_tool_router_node(
        ml_model="test-model",
        blocks=[],
        functions=[my_string_function],
        prompt_inputs=None,
    )

    function_node_class = create_function_node(my_string_function, router_node)
    assert function_node_class.get_output_type() == str
    # AND a state with function call results
    state = State()

    # WHEN we run the function node
    function_node = function_node_class(state=state)
    outputs = function_node.run()

    # THEN it should execute successfully
    assert outputs is not None


def test_function_node_output_type_error():
    """
    Test that the function node runs successfully when function returns expected type.
    """

    # GIVEN a tool router node and function node
    router_node = create_tool_router_node(
        ml_model="test-model",
        blocks=[],
        functions=[my_error_function],
        prompt_inputs=None,
    )

    function_node_class = create_function_node(my_error_function, router_node)
    assert function_node_class.get_output_type() == int

    # AND a state with function call results
    state = State()

    # WHEN we run the function node
    function_node = function_node_class(state=state)

    # THEN it should raise an error
    with pytest.raises(NodeException) as e:
        function_node.run()

    assert str(e.value) == "Expected an output of type 'int', but received 'str'"
