from typing import Any, Dict, Tuple, Type

from vellum.workflows.descriptors.base import BaseDescriptor
from vellum.workflows.descriptors.utils import resolve_value
from vellum.workflows.state.base import BaseState


class DescriptorWithoutIsSensitive(BaseDescriptor[str]):
    """
    A descriptor subclass that bypasses BaseDescriptor.__init__ and doesn't define _is_sensitive.
    This simulates the scenario described in the PR comment where certain descriptor subclasses
    don't call super().__init__() and thus lack the _is_sensitive attribute.
    """

    def __init__(self, name: str, types: Tuple[Type[str], ...]) -> None:
        self._name = name
        self._types = types
        self._instance = None

    def resolve(self, state: BaseState) -> str:
        return "resolved_value"


def test_resolve_value__descriptor_without_is_sensitive__does_not_raise():
    """
    Tests that resolve_value handles descriptors without _is_sensitive attribute gracefully.
    """

    # GIVEN a descriptor that doesn't have _is_sensitive defined
    descriptor = DescriptorWithoutIsSensitive(name="test_descriptor", types=(str,))

    # AND a state object
    class TestState(BaseState):
        pass

    state = TestState()

    # AND a memo dict to track resolved values
    memo: Dict[str, Any] = {}

    # WHEN we call resolve_value with this descriptor
    result = resolve_value(descriptor, state, path="test.path", memo=memo)

    # THEN it should not raise an AttributeError
    assert result == "resolved_value"

    # AND the memo should contain the resolved value (not the descriptor itself)
    # since the descriptor is treated as non-sensitive when _is_sensitive is missing
    assert memo["test.path"] == "resolved_value"


def test_resolve_value__descriptor_without_is_sensitive__no_memo__does_not_raise():
    """
    Tests that resolve_value handles descriptors without _is_sensitive when memo is None.
    """

    # GIVEN a descriptor that doesn't have _is_sensitive defined (important-comment)
    descriptor = DescriptorWithoutIsSensitive(name="test_descriptor", types=(str,))

    # AND a state object
    class TestState(BaseState):
        pass

    state = TestState()

    # WHEN we call resolve_value without a memo
    result = resolve_value(descriptor, state, path="test.path", memo=None)

    # THEN it should not raise an AttributeError (important-comment)
    assert result == "resolved_value"
