import pytest
from typing import Any, Union

from vellum.workflows.utils.validate import validate_target_type


@pytest.mark.parametrize(
    ["declared_type", "target_type"],
    [
        (str, int),
        (list[str], list[int]),
        (str, Union[str, int]),
        (int, Union[str, int]),
        (list[str], Union[list[str], list[int]]),
        (Union[str, int], Union[bool, float]),
    ],
    ids=[
        "str_int",
        "list_str_int",
        "str_union_str_int",
        "int_union_str_int",
        "list_str_union",
        "union_str_int_union_bool_float",
    ],
)
def test_validate__should_raise_exception(
    declared_type,
    target_type,
):
    """
    Tests that validate_target_type raises an exception for mismatched types.
    """

    # WHEN validating the target type
    with pytest.raises(ValueError) as exc_info:
        validate_target_type(declared_type, target_type)

    # THEN an exception should be raised
    assert "Output type mismatch" in str(exc_info.value)


@pytest.mark.parametrize(
    ["declared_type", "target_type"],
    [
        (str, str),
        (list[str], list[str]),
        (dict, dict[str, str]),
        (str, Any),
        (Any, str),
        (Union[str, int], str),
        (Union[str, int], int),
        (Union[str, int], Union[str, int]),
        (Union[str, int], Union[int, str]),
        (Union[str, int], Union[str, bool]),
    ],
    ids=[
        "str",
        "list_str",
        "bare_dict_params_dict",
        "str_any",
        "any_str",
        "union_str_int_str",
        "union_str_int_int",
        "union_str_int_union_str_int",
        "union_str_int_union_int_str",
        "union_str_int_union_str_bool",
    ],
)
def test_validate__should_validate(
    declared_type,
    target_type,
):
    """
    Tests that validate_target_type accepts matching types.
    """

    # WHEN validating the target type
    # THEN no exception should be raised
    validate_target_type(declared_type, target_type)
