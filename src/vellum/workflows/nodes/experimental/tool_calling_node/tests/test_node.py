from vellum.client.types.function_call import FunctionCall
from vellum.client.types.function_call_vellum_value import FunctionCallVellumValue
from vellum.workflows.nodes.experimental.tool_calling_node.utils import create_tool_router_node
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
