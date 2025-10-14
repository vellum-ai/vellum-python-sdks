from __future__ import annotations

import pytest
from typing import ClassVar, Optional, Union

from vellum.workflows.types.utils import infer_types


class BasicClass:
    """Basic class with simple type annotations."""

    string_field: str
    int_field: int


class ClassWithOptional:
    """Class using Optional[] syntax."""

    optional_field: Optional[str]


class ClassWithUnion:
    """Class using Union[] syntax."""

    union_field: Union[str, int]


class ClassWithPEP604Union:
    """Class using PEP 604 union syntax (A | B)."""

    union_field: str | int
    optional_field: str | None


class ClassWithClassVar:
    """Class with ClassVar annotation."""

    class_var: ClassVar[str]


def test_infer_types__basic_type():
    """
    Tests that infer_types correctly infers basic type annotations.
    """
    result = infer_types(BasicClass, "string_field")

    assert result == (str,)


def test_infer_types__int_type():
    """
    Tests that infer_types correctly infers int type annotations.
    """
    result = infer_types(BasicClass, "int_field")

    assert result == (int,)


def test_infer_types__optional():
    """
    Tests that infer_types correctly infers Optional[] types.
    """
    result = infer_types(ClassWithOptional, "optional_field")

    assert result == (str, type(None))


def test_infer_types__union():
    """
    Tests that infer_types correctly infers Union[] types.
    """
    result = infer_types(ClassWithUnion, "union_field")

    assert result == (str, int)


def test_infer_types__pep604_union():
    """
    Tests that infer_types correctly infers PEP 604 union types (A | B).
    """
    result = infer_types(ClassWithPEP604Union, "union_field")

    assert result == (str, int)


def test_infer_types__pep604_optional():
    """
    Tests that infer_types correctly infers PEP 604 optional types (A | None).
    This is the specific case mentioned in the Linear ticket APO-1886.
    """
    result = infer_types(ClassWithPEP604Union, "optional_field")

    assert result == (str, type(None))


def test_infer_types__class_var():
    """
    Tests that infer_types correctly handles ClassVar annotations.
    """
    result = infer_types(ClassWithClassVar, "class_var")

    assert result == (str,)


def test_infer_types__missing_attribute():
    """
    Tests that infer_types raises AttributeError for non-existent attributes.
    """
    with pytest.raises(AttributeError, match="Failed to infer type from attribute"):
        infer_types(BasicClass, "non_existent_field")
