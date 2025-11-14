import json

from pydantic import Field
from pydantic.fields import FieldInfo

from vellum.utils.json_encoder import VellumJsonEncoder


class TestVellumJsonEncoder:
    """Tests for VellumJsonEncoder."""

    def test_encode_fieldinfo_with_default(self):
        """Test that FieldInfo objects with defaults are serialized to their default value."""
        # Create a FieldInfo with a default value
        field_info = Field(default="default_value")

        result = json.dumps({"field": field_info}, cls=VellumJsonEncoder)
        assert result == '{"field": "default_value"}'

    def test_encode_fieldinfo_without_default(self):
        """Test that FieldInfo objects without defaults are serialized to None."""
        # Create a FieldInfo without a default value (annotation only)
        field_info = FieldInfo(annotation=str)

        result = json.dumps({"field": field_info}, cls=VellumJsonEncoder)
        assert result == '{"field": null}'

    def test_encode_nested_dict_with_fieldinfo(self):
        """Test that nested structures containing FieldInfo are properly serialized."""
        field_info_with_default = Field(default=42)
        field_info_without_default = FieldInfo(annotation=int)

        data = {
            "config": {
                "cron": field_info_with_default,
                "timezone": field_info_without_default,
                "regular_value": "test",
            }
        }

        result = json.dumps(data, cls=VellumJsonEncoder)
        expected = '{"config": {"cron": 42, "timezone": null, "regular_value": "test"}}'
        assert result == expected

    def test_encode_list_with_fieldinfo(self):
        """Test that lists containing FieldInfo are properly serialized."""
        field_info = Field(default="item")

        data = [field_info, "normal_string", field_info]

        result = json.dumps(data, cls=VellumJsonEncoder)
        assert result == '["item", "normal_string", "item"]'

    def test_encode_fieldinfo_with_default_factory(self):
        """Test that FieldInfo objects with default_factory are serialized properly."""

        field_info = Field(
            default_factory=lambda: {
                "key1": "value1",
                "key2": "value2",
            }
        )

        data = {"test": field_info}

        result = json.dumps(data, cls=VellumJsonEncoder)
        # Note: When a FieldInfo has default_factory instead of default,
        # the default attribute will be PydanticUndefined, which should serialize to None
        # The actual default_factory is only called when instantiating a model
        assert result == '{"test": null}'
