"""Tests for expressions serialization utilities"""

import pytest

from vellum.workflows.constants import undefined
from vellum_ee.workflows.display.utils.expressions import serialize_value


class TestSerializeValue:
    """Tests for the serialize_value function"""

    @pytest.mark.parametrize("value", [undefined, None])
    def test_serialize_value(self, value):
        """Test that values are properly serialized"""
        # WHEN we serialize a value
        result = serialize_value(display_context=None, value=value)
        # THEN it should match the expected serialization
        assert result == {"type": "CONSTANT_VALUE", "value": {"type": "JSON", "value": None}}
