"""Tests for expressions serialization utilities"""

from vellum.workflows.constants import undefined
from vellum_ee.workflows.display.utils.expressions import serialize_value


class TestSerializeValue:
    """Tests for the serialize_value function"""

    def test_serialize_undefined_value(self):
        """Test that undefined values are properly serialized to JSON null

        This test prevents regression of APO-1404 where undefined values
        would cause a "'undefined' object cannot be converted to SchemaSerializer" error
        """
        # WHEN we serialize an undefined value
        result = serialize_value(display_context=None, value=undefined)

        # THEN it should be serialized as a constant JSON null value
        assert result == {
            "type": "CONSTANT_VALUE",
            "value": {
                "type": "JSON",
                "value": None,
            },
        }

    def test_serialize_none_value(self):
        """Test that None values are handled differently from undefined"""
        # WHEN we serialize a None value
        result = serialize_value(display_context=None, value=None)

        # THEN it should be serialized as a constant JSON null value
        assert result == {
            "type": "CONSTANT_VALUE",
            "value": {
                "type": "JSON",
                "value": None,
            },
        }
