"""Tests for expressions serialization utilities"""

from vellum.workflows.constants import undefined
from vellum_ee.workflows.display.types import WorkflowDisplayContext
from vellum_ee.workflows.display.utils.expressions import serialize_value


class TestSerializeValue:
    """Tests for the serialize_value function"""

    def test_serialize_undefined(self):
        """Test that undefined values are properly handled"""
        # GIVEN a display context
        display_context = WorkflowDisplayContext()
        # WHEN we serialize an undefined value
        result = serialize_value(display_context=display_context, value=undefined)
        # THEN it should return undefined (to be filtered by parent serializers)
        assert result is undefined

    def test_serialize_null(self):
        """Test that null values are properly serialized"""
        # GIVEN a display context
        display_context = WorkflowDisplayContext()
        # WHEN we serialize a null value
        result = serialize_value(display_context=display_context, value=None)
        # THEN it should match the expected serialization
        assert result == {"type": "CONSTANT_VALUE", "value": {"type": "JSON", "value": None}}
