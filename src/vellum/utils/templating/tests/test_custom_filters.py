import pytest

from vellum.utils.templating.custom_filters import replace


@pytest.mark.parametrize(
    ["input_str", "old", "new", "expected"],
    [
        ("foo", "foo", "bar", "bar"),
        ({"message": "hello"}, "hello", "world", '{"message": "world"}'),
        ("Value: 123", 123, 456, "Value: 456"),
        (123, 2, 4, "143"),
        ("", "", "", ""),
        ("foo", "", "bar", "foo"),
    ],
)
def test_replace(input_str, old, new, expected):
    actual = replace(input_str, old, new)
    assert actual == expected
