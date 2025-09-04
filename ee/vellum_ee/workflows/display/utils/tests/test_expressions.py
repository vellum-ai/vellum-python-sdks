"""Tests for expressions serialization utilities"""

import pytest

from vellum.workflows.constants import undefined
from vellum_ee.workflows.display.utils.expressions import serialize_value


class TestSerializeValue:
    """Tests for the serialize_value function"""

    @pytest.mark.parametrize(
        "value, expected_serialization",
        [
            (undefined, {"type": "CONSTANT_VALUE", "value": {"type": "JSON", "value": None}}),
            (None, {"type": "CONSTANT_VALUE", "value": {"type": "JSON", "value": None}}),
        ],
    )
    def test_serialize_value(self):
        """Test that values are properly serialized to JSON null

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
