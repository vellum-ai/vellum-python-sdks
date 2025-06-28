from typing import Any

from pydantic import BaseModel

from vellum.workflows.expressions.accessor import AccessorExpression
from vellum.workflows.references.constant import ConstantValueReference
from vellum.workflows.state.base import BaseState


class TestState(BaseState):
    pass


class TestModel(BaseModel):
    field: Any


def test_pydantic_plugin__empty_types_descriptor():
    """
    Test that the pydantic plugin handles BaseDescriptor with empty types gracefully.
    """

    base_ref = ConstantValueReference({"name": "test"})
    accessor = AccessorExpression(base=base_ref, field="name")

    model = TestModel(field=accessor)

    assert model is not None
    assert hasattr(model, "field")
    assert model.field == accessor
