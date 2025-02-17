import pytest

from vellum.workflows.constants import undefined


def test_undefined__ensure_sensible_error_messages():
    # WHEN we invoke an invalid operation on `undefined`
    with pytest.raises(Exception) as e:
        len(undefined)

    # THEN we get a sensible error message
    assert str(e.value) == "object of type 'undefined' has no len()"
