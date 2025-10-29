import pytest
from uuid import UUID

from vellum.workflows.utils.uuids import uuid4_from_hash


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
