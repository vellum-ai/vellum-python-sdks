from typing import Any, Tuple, Type

from vellum.workflows.descriptors.base import BaseDescriptor
from vellum.workflows.types.utils import resolve_combined_types, resolve_types


class MockDescriptor(BaseDescriptor[Any]):
    """Mock descriptor for testing purposes."""

    def resolve(self, state):
        return "mock"


def test_resolve_types__with_descriptor():
    """
    Tests that resolve_types returns the types from a BaseDescriptor.
    """
    descriptor = MockDescriptor(name="test", types=(str, int))

    result: Tuple[Type[Any], ...] = resolve_types(descriptor)

    assert result == (str, int)


def test_resolve_types__with_regular_object():
    """
    Tests that resolve_types returns the class type for regular objects.
    """
    value = "test"

    result: Tuple[Type[Any], ...] = resolve_types(value)

    assert result == (str,)


def test_resolve_combined_types__both_descriptors():
    """
    Tests that resolve_combined_types preserves lhs order before rhs types.
    """
    lhs = MockDescriptor(name="lhs", types=(str, int))
    rhs = MockDescriptor(name="rhs", types=(float, bool))

    result: Tuple[Type[Any], ...] = resolve_combined_types(lhs, rhs)

    assert result == (str, int, float, bool)


def test_resolve_combined_types__with_overlapping_types():
    """
    Tests that resolve_combined_types maintains distinctness while preserving order.
    """
    lhs = MockDescriptor(name="lhs", types=(str, int, float))
    rhs = MockDescriptor(name="rhs", types=(float, bool, str))

    result: Tuple[Type[Any], ...] = resolve_combined_types(lhs, rhs)

    assert result == (str, int, float, bool)


def test_resolve_combined_types__descriptor_and_object():
    """
    Tests resolve_combined_types with a descriptor and regular object.
    """
    lhs = MockDescriptor(name="lhs", types=(str, int))
    rhs = 3.14  # float object

    result: Tuple[Type[Any], ...] = resolve_combined_types(lhs, rhs)

    assert result == (str, int, float)


def test_resolve_combined_types__object_and_descriptor():
    """
    Tests resolve_combined_types with a regular object and descriptor.
    """
    lhs = "hello"  # str object
    rhs = MockDescriptor(name="rhs", types=(int, bool))

    result: Tuple[Type[Any], ...] = resolve_combined_types(lhs, rhs)

    assert result == (str, int, bool)


def test_resolve_combined_types__both_objects():
    """
    Tests resolve_combined_types with two regular objects.
    """
    lhs = "hello"  # str
    rhs = 42  # int

    result: Tuple[Type[Any], ...] = resolve_combined_types(lhs, rhs)

    assert result == (str, int)


def test_resolve_combined_types__same_types():
    """
    Tests resolve_combined_types with identical types maintains distinctness.
    """
    lhs = "hello"
    rhs = "world"

    result: Tuple[Type[Any], ...] = resolve_combined_types(lhs, rhs)

    assert result == (str,)


def test_resolve_combined_types__empty_types():
    """
    Tests resolve_combined_types with descriptors having empty types.
    """
    lhs = MockDescriptor(name="lhs", types=())
    rhs = MockDescriptor(name="rhs", types=(int, str))

    result: Tuple[Type[Any], ...] = resolve_combined_types(lhs, rhs)

    assert result == (int, str)


def test_resolve_combined_types__preserves_order_complex():
    """
    Tests that resolve_combined_types preserves complex ordering scenarios.
    """
    lhs = MockDescriptor(name="lhs", types=(dict, list, str, int))
    rhs = MockDescriptor(name="rhs", types=(int, tuple, dict, bool))

    result: Tuple[Type[Any], ...] = resolve_combined_types(lhs, rhs)

    assert result == (dict, list, str, int, tuple, bool)
