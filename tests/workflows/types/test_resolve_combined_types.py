from typing import Any, Tuple, Type

from vellum.workflows.descriptors.base import BaseDescriptor
from vellum.workflows.types.utils import resolve_combined_types


class MockDescriptor(BaseDescriptor[Any]):
    """Mock descriptor for testing purposes."""

    def resolve(self, state):
        return "mock"


def test_resolve_combined_types__with_overlapping_types():
    """
    Tests that resolve_combined_types maintains distinctness while preserving order.
    """
    lhs = MockDescriptor(name="lhs", types=(str, int, float))
    rhs = MockDescriptor(name="rhs", types=(float, bool, str))

    result: Tuple[Type[Any], ...] = resolve_combined_types(lhs, rhs)

    assert result == (str, int, float, bool)
