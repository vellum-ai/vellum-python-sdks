import pytest

from vellum.workflows.descriptors.utils import resolve_value
from vellum.workflows.errors.types import WorkflowError, WorkflowErrorCode
from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.references.constant import ConstantValueReference
from vellum.workflows.state.base import BaseState


class FixtureState(BaseState):
    alpha = 1
    beta = 2

    gamma = "hello"
    delta = "el"

    epsilon = 3
    zeta = {
        "foo": "bar",
    }

    eta = None
    theta = ["baz"]


class DummyNode(BaseNode[FixtureState]):
    class Outputs(BaseNode.Outputs):
        empty: str


@pytest.mark.parametrize(
    ["descriptor", "expected_value"],
    [
        (FixtureState.alpha | FixtureState.beta, 1),
        (FixtureState.alpha & FixtureState.beta, 2),
        (FixtureState.beta.coalesce(FixtureState.alpha), 2),
        (FixtureState.alpha.equals(FixtureState.beta), False),
        (FixtureState.alpha.does_not_equal(FixtureState.beta), True),
        (FixtureState.alpha.less_than(FixtureState.beta), True),
        (FixtureState.alpha.greater_than(FixtureState.beta), False),
        (FixtureState.alpha.less_than_or_equal_to(FixtureState.beta), True),
        (FixtureState.alpha.greater_than_or_equal_to(FixtureState.beta), False),
        (FixtureState.gamma.contains(FixtureState.delta), True),
        (FixtureState.gamma.begins_with(FixtureState.delta), False),
        (FixtureState.gamma.ends_with(FixtureState.delta), False),
        (FixtureState.gamma.does_not_contain(FixtureState.delta), False),
        (FixtureState.gamma.does_not_begin_with(FixtureState.delta), True),
        (FixtureState.gamma.does_not_end_with(FixtureState.delta), True),
        (FixtureState.alpha.is_null(), False),
        (FixtureState.eta.is_null(), True),
        (DummyNode.Outputs.empty.is_null(), False),
        (FixtureState.alpha.is_not_null(), True),
        (FixtureState.eta.is_not_null(), False),
        (DummyNode.Outputs.empty.is_not_null(), True),
        (FixtureState.alpha.is_nil(), False),
        (FixtureState.eta.is_nil(), True),
        (DummyNode.Outputs.empty.is_nil(), True),
        (FixtureState.alpha.is_not_nil(), True),
        (FixtureState.eta.is_not_nil(), False),
        (DummyNode.Outputs.empty.is_not_nil(), False),
        (FixtureState.alpha.is_undefined(), False),
        (FixtureState.eta.is_undefined(), False),
        (DummyNode.Outputs.empty.is_undefined(), True),
        (FixtureState.alpha.is_not_undefined(), True),
        (FixtureState.eta.is_not_undefined(), True),
        (DummyNode.Outputs.empty.is_not_undefined(), False),
        (FixtureState.delta.in_(FixtureState.gamma), True),
        (FixtureState.delta.not_in(FixtureState.gamma), False),
        (FixtureState.alpha.between(FixtureState.beta, FixtureState.epsilon), False),
        (FixtureState.alpha.not_between(FixtureState.beta, FixtureState.epsilon), True),
        (FixtureState.delta.is_blank(), False),
        (FixtureState.delta.is_not_blank(), True),
        (
            FixtureState.alpha.equals(FixtureState.alpha)
            | FixtureState.alpha.equals(FixtureState.beta) & FixtureState.alpha.equals(FixtureState.beta),
            True,
        ),
        (FixtureState.zeta["foo"], "bar"),
        (ConstantValueReference(1), 1),
        (FixtureState.theta[0], "baz"),
        (
            ConstantValueReference(
                WorkflowError(
                    message="This is a test",
                    code=WorkflowErrorCode.USER_DEFINED_ERROR,
                )
            ).contains("test"),
            True,
        ),
        (
            ConstantValueReference(
                WorkflowError(
                    message="This is a test",
                    code=WorkflowErrorCode.USER_DEFINED_ERROR,
                )
            ).does_not_contain("test"),
            False,
        ),
        (ConstantValueReference('{"foo": "bar"}').parse_json(), {"foo": "bar"}),
        (ConstantValueReference('{"foo": "bar"}').parse_json()["foo"], "bar"),
        (ConstantValueReference("[1, 2, 3]").parse_json(), [1, 2, 3]),
        (ConstantValueReference("[1, 2, 3]").parse_json()[0], 1),
        (ConstantValueReference(b'{"foo": "bar"}').parse_json(), {"foo": "bar"}),
        (ConstantValueReference(bytearray(b'{"foo": "bar"}')).parse_json(), {"foo": "bar"}),
        (ConstantValueReference(b'{"key": "\xf0\x9f\x8c\x9f"}').parse_json(), {"key": "🌟"}),
    ],
    ids=[
        "or",
        "and",
        "coalesce",
        "eq",
        "dne",
        "less_than",
        "greater_than",
        "less_than_or_equal_to",
        "greater_than_or_equal_to",
        "contains",
        "begins_with",
        "ends_with",
        "does_not_contain",
        "does_not_begin_with",
        "does_not_end_with",
        "is_null_on_value",
        "is_null_on_null",
        "is_null_on_undefined",
        "is_not_null_on_value",
        "is_not_null_on_null",
        "is_not_null_on_undefined",
        "is_nil_on_value",
        "is_nil_on_null",
        "is_nil_on_undefined",
        "is_not_nil_on_value",
        "is_not_nil_on_null",
        "is_not_nil_on_undefined",
        "is_undefined_on_value",
        "is_undefined_on_null",
        "is_undefined_on_undefined",
        "is_not_undefined_on_value",
        "is_not_undefined_on_null",
        "is_not_undefined_on_undefined",
        "in_",
        "not_in",
        "between",
        "not_between",
        "is_blank",
        "is_not_blank",
        "or_and",
        "accessor",
        "constants",
        "list_index",
        "error_contains",
        "error_does_not_contain",
        "parse_json_constant",
        "parse_json_accessor",
        "parse_json_list",
        "parse_json_list_index",
        "parse_json_bytes",
        "parse_json_bytearray",
        "parse_json_bytes_with_utf8_chars",
    ],
)
def test_resolve_value__happy_path(descriptor, expected_value):
    actual_value = resolve_value(descriptor, FixtureState())
    assert actual_value == expected_value
