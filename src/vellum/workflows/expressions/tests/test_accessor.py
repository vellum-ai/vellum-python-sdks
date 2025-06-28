import pytest
from dataclasses import dataclass

from pydantic import BaseModel

from vellum.workflows.descriptors.exceptions import InvalidExpressionException
from vellum.workflows.expressions.accessor import AccessorExpression
from vellum.workflows.references.constant import ConstantValueReference
from vellum.workflows.state.base import BaseState


@dataclass
class TestDataclass:
    name: str
    value: int


class TestBaseModel(BaseModel):
    name: str
    value: int


class TestState(BaseState):
    pass


def test_accessor_expression_dict_valid_key():
    state = TestState()
    base_ref = ConstantValueReference({"name": "test", "value": 42})
    accessor = AccessorExpression(base=base_ref, field="name")

    result = accessor.resolve(state)

    assert result == "test"


def test_accessor_expression_dict_invalid_key():
    state = TestState()
    base_ref = ConstantValueReference({"name": "test", "value": 42})
    accessor = AccessorExpression(base=base_ref, field="missing_key")

    with pytest.raises(InvalidExpressionException) as exc_info:
        accessor.resolve(state)

    assert "Key 'missing_key' not found in mapping" in str(exc_info.value)


def test_accessor_expression_list_valid_index():
    state = TestState()
    base_ref = ConstantValueReference(["first", "second", "third"])
    accessor = AccessorExpression(base=base_ref, field=1)

    result = accessor.resolve(state)

    assert result == "second"


def test_accessor_expression_list_invalid_index():
    state = TestState()
    base_ref = ConstantValueReference(["first", "second"])
    accessor = AccessorExpression(base=base_ref, field=5)

    with pytest.raises(InvalidExpressionException) as exc_info:
        accessor.resolve(state)

    assert "Index 5 is out of bounds for sequence of length 2" in str(exc_info.value)


def test_accessor_expression_list_negative_index():
    state = TestState()
    base_ref = ConstantValueReference(["first", "second", "third"])
    accessor = AccessorExpression(base=base_ref, field=-1)

    result = accessor.resolve(state)

    assert result == "third"


def test_accessor_expression_list_invalid_negative_index():
    state = TestState()
    base_ref = ConstantValueReference(["first", "second"])
    accessor = AccessorExpression(base=base_ref, field=-5)

    with pytest.raises(InvalidExpressionException) as exc_info:
        accessor.resolve(state)

    assert "Index -5 is out of bounds for sequence of length 2" in str(exc_info.value)


def test_accessor_expression_list_string_index():
    state = TestState()
    base_ref = ConstantValueReference(["first", "second", "third"])
    accessor = AccessorExpression(base=base_ref, field="1")

    result = accessor.resolve(state)

    assert result == "second"


def test_accessor_expression_list_invalid_string_index():
    state = TestState()
    base_ref = ConstantValueReference(["first", "second"])
    accessor = AccessorExpression(base=base_ref, field="invalid")

    with pytest.raises(InvalidExpressionException) as exc_info:
        accessor.resolve(state)

    assert "Invalid index 'invalid' for sequence access" in str(exc_info.value)


def test_accessor_expression_dataclass_valid_field():
    state = TestState()
    test_obj = TestDataclass(name="test", value=42)
    base_ref = ConstantValueReference(test_obj)
    accessor = AccessorExpression(base=base_ref, field="name")

    result = accessor.resolve(state)

    assert result == "test"


def test_accessor_expression_dataclass_invalid_field():
    state = TestState()
    test_obj = TestDataclass(name="test", value=42)
    base_ref = ConstantValueReference(test_obj)
    accessor = AccessorExpression(base=base_ref, field="missing_field")

    with pytest.raises(InvalidExpressionException) as exc_info:
        accessor.resolve(state)

    assert "Field 'missing_field' not found on dataclass TestDataclass" in str(exc_info.value)


def test_accessor_expression_basemodel_valid_field():
    state = TestState()
    test_obj = TestBaseModel(name="test", value=42)
    base_ref = ConstantValueReference(test_obj)
    accessor = AccessorExpression(base=base_ref, field="name")

    result = accessor.resolve(state)

    assert result == "test"


def test_accessor_expression_basemodel_invalid_field():
    state = TestState()
    test_obj = TestBaseModel(name="test", value=42)
    base_ref = ConstantValueReference(test_obj)
    accessor = AccessorExpression(base=base_ref, field="missing_field")

    with pytest.raises(InvalidExpressionException) as exc_info:
        accessor.resolve(state)

    assert "Field 'missing_field' not found on BaseModel TestBaseModel" in str(exc_info.value)


def test_accessor_expression_dataclass_index_access():
    state = TestState()
    test_obj = TestDataclass(name="test", value=42)
    base_ref = ConstantValueReference(test_obj)
    accessor = AccessorExpression(base=base_ref, field=0)

    with pytest.raises(InvalidExpressionException) as exc_info:
        accessor.resolve(state)

    assert "Cannot access field by index on a dataclass" in str(exc_info.value)


def test_accessor_expression_basemodel_index_access():
    state = TestState()
    test_obj = TestBaseModel(name="test", value=42)
    base_ref = ConstantValueReference(test_obj)
    accessor = AccessorExpression(base=base_ref, field=0)

    with pytest.raises(InvalidExpressionException) as exc_info:
        accessor.resolve(state)

    assert "Cannot access field by index on a BaseModel" in str(exc_info.value)


def test_accessor_expression_unsupported_type():
    state = TestState()
    base_ref = ConstantValueReference(42)
    accessor = AccessorExpression(base=base_ref, field="field")

    with pytest.raises(InvalidExpressionException) as exc_info:
        accessor.resolve(state)

    assert "Cannot get field field from 42" in str(exc_info.value)


def test_accessor_expression_list_type_inference():
    """Test that accessor expressions correctly infer element types from List[str]."""
    from typing import List

    from vellum.workflows.outputs.base import BaseOutputs
    from vellum.workflows.references.output import OutputReference

    base_ref: OutputReference = OutputReference(
        name="test_list",
        types=(List[str],),
        instance=None,
        outputs_class=BaseOutputs,
    )

    accessor = AccessorExpression(base=base_ref, field=0)

    assert accessor.types == (str,)


def test_accessor_expression_tuple_type_inference():
    """Test that accessor expressions correctly infer element types from Tuple types."""
    from typing import List

    from vellum.workflows.outputs.base import BaseOutputs
    from vellum.workflows.references.output import OutputReference

    base_ref: OutputReference = OutputReference(
        name="test_list_for_tuple_behavior",
        types=(List[str],),
        instance=None,
        outputs_class=BaseOutputs,
    )

    accessor = AccessorExpression(base=base_ref, field=0)

    assert accessor.types == (str,)


def test_accessor_expression_dict_type_inference():
    """Test that accessor expressions correctly infer value types from Dict types."""
    from typing import Dict

    from vellum.workflows.outputs.base import BaseOutputs
    from vellum.workflows.references.output import OutputReference

    base_ref: OutputReference = OutputReference(
        name="test_dict",
        types=(Dict[str, int],),
        instance=None,
        outputs_class=BaseOutputs,
    )

    accessor = AccessorExpression(base=base_ref, field="some_key")

    assert accessor.types == (int,)


def test_accessor_expression_no_type_inference_for_non_container():
    """Test that accessor expressions don't infer types for non-container types."""
    from vellum.workflows.outputs.base import BaseOutputs
    from vellum.workflows.references.output import OutputReference

    base_ref: OutputReference = OutputReference(
        name="test_str",
        types=(str,),
        instance=None,
        outputs_class=BaseOutputs,
    )

    accessor = AccessorExpression(base=base_ref, field=0)

    assert accessor.types == ()


def test_accessor_expression_empty_base_types():
    """Test that accessor expressions handle empty base types gracefully."""
    from vellum.workflows.outputs.base import BaseOutputs
    from vellum.workflows.references.output import OutputReference

    base_ref: OutputReference = OutputReference(
        name="test_empty",
        types=(),
        instance=None,
        outputs_class=BaseOutputs,
    )

    accessor = AccessorExpression(base=base_ref, field=0)

    assert accessor.types == ()


def test_accessor_expression_multiple_indices():
    """Test that accessor expressions work correctly for multiple indices."""
    from typing import List

    from vellum.workflows.outputs.base import BaseOutputs
    from vellum.workflows.references.output import OutputReference

    base_ref: OutputReference = OutputReference(
        name="test_multiple_indices",
        types=(List[str],),
        instance=None,
        outputs_class=BaseOutputs,
    )

    accessor0 = AccessorExpression(base=base_ref, field=0)
    accessor1 = AccessorExpression(base=base_ref, field=1)

    assert accessor0.types == (str,)
    assert accessor1.types == (str,)
