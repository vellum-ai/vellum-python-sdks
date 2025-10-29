import pytest
from uuid import UUID

from vellum.workflows.triggers.base import BaseTrigger
from vellum.workflows.utils.uuids import get_trigger_attribute_id, get_trigger_id, uuid4_from_hash


@pytest.mark.parametrize(
    ["input_str", "expected"],
    [
        ("MyExampleString", UUID("b2dadec1-bff4-4e26-8d65-e99e62628cd2")),
        ("My Example String", UUID("a1e68bde-3263-4526-88bd-70f4bf800224")),
    ],
)
def test_uuid4_from_hash(input_str, expected):
    actual = uuid4_from_hash(input_str)
    assert actual == expected


def test_get_trigger_id__includes_module_name():
    """
    Tests that get_trigger_id includes the module name in the generated UUID.
    """

    class TestTrigger(BaseTrigger):
        pass

    trigger_id = get_trigger_id(TestTrigger)

    expected_id = uuid4_from_hash(f"{TestTrigger.__module__}.{TestTrigger.__qualname__}")
    assert trigger_id == expected_id


def test_get_trigger_id__different_modules_different_ids():
    """
    Tests that triggers with the same qualname but different modules generate different IDs.
    """

    class TestTrigger(BaseTrigger):
        pass

    class AnotherTestTrigger(BaseTrigger):
        pass

    AnotherTestTrigger.__module__ = "different.module"
    AnotherTestTrigger.__qualname__ = "TestTrigger"

    id1 = get_trigger_id(TestTrigger)
    id2 = get_trigger_id(AnotherTestTrigger)

    assert id1 != id2


def test_get_trigger_attribute_id__includes_module_name():
    """
    Tests that get_trigger_attribute_id includes the module name in the generated UUID.
    """

    class TestTrigger(BaseTrigger):
        pass

    attribute_name = "test_attribute"

    attribute_id = get_trigger_attribute_id(TestTrigger, attribute_name)

    expected_id = uuid4_from_hash(f"{TestTrigger.__module__}.{TestTrigger.__qualname__}|{attribute_name}")
    assert attribute_id == expected_id


def test_get_trigger_attribute_id__different_modules_different_ids():
    """
    Tests that trigger attributes with the same qualname but different modules generate different IDs.
    """

    class TestTrigger(BaseTrigger):
        pass

    class AnotherTestTrigger(BaseTrigger):
        pass

    AnotherTestTrigger.__module__ = "different.module"
    AnotherTestTrigger.__qualname__ = "TestTrigger"

    attribute_name = "test_attribute"

    id1 = get_trigger_attribute_id(TestTrigger, attribute_name)
    id2 = get_trigger_attribute_id(AnotherTestTrigger, attribute_name)

    assert id1 != id2
