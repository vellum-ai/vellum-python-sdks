import pytest

from vellum.workflows.utils.validate import validate_target_types


@pytest.mark.parametrize(
    ["declared_type", "target_types"],
    [
        (str, (int,)),
        (list[str], (list[int],)),
    ],
    ids=[
        "str_int",
        "list_str_int",
    ],
)
def test_validate__should_raise_exception(
    declared_type,
    target_types,
):
    # WHEN validating the target types
    with pytest.raises(ValueError) as exc_info:
        validate_target_types(declared_type, target_types)

    # THEN an exception should be raised
    assert "Output type mismatch" in str(exc_info.value)


@pytest.mark.parametrize(
    ["declared_type", "target_types"],
    [
        (str, (str,)),
        (list[str], (list[str],)),
        (dict, (dict[str, str],)),
    ],
    ids=[
        "str",
        "list_str",
        "bare_dict_params_dict",
    ],
)
def test_validate__should_validate(
    declared_type,
    target_types,
):
    # WHEN validating the target types
    # THEN no exception should be raised
    validate_target_types(declared_type, target_types)
