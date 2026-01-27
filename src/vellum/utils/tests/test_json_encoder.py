import json

from pydantic import BaseModel, Field
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
        # the default attribute will be PydanticUndefined, which should serialize to None.
        assert result == '{"test": null}'

    def test_encode_basemodel_with_default_factory(self):
        """
        Tests that BaseModel instances with default_factory fields serialize correctly.

        This demonstrates that when pushing workflows to Vellum, the default_factory
        values are preserved because Pydantic invokes the factory during model instantiation.
        """

        class ConfigModel(BaseModel):
            settings: dict = Field(default_factory=lambda: {"key1": "value1", "key2": "value2"})
            name: str = "test"

        model_instance = ConfigModel()

        assert model_instance.settings == {"key1": "value1", "key2": "value2"}

        # AND when we serialize the model instance with VellumJsonEncoder
        result = json.dumps(model_instance, cls=VellumJsonEncoder)

        deserialized = json.loads(result)
        assert deserialized["settings"] == {"key1": "value1", "key2": "value2"}
        assert deserialized["name"] == "test"

    def test_encode_generator_object(self):
        """
        Tests that generator objects are serialized to a string representation.

        This prevents PydanticSerializationError when workflow events contain
        generator objects that cannot be JSON serialized.
        """

        # GIVEN a generator object
        def my_generator():
            yield 1
            yield 2
            yield 3

        gen = my_generator()

        # WHEN we serialize a dict containing the generator
        result = json.dumps({"data": gen}, cls=VellumJsonEncoder)

        # THEN the generator is serialized to a string representation
        deserialized = json.loads(result)
        assert deserialized["data"] == "<generator object>"

    def test_encode_nested_generator_object(self):
        """
        Tests that nested generator objects are serialized correctly.
        """

        # GIVEN a nested structure containing a generator
        def my_generator():
            yield "item"

        data = {
            "outer": {
                "inner": my_generator(),
                "normal": "value",
            }
        }

        # WHEN we serialize the nested structure
        result = json.dumps(data, cls=VellumJsonEncoder)

        # THEN the generator is serialized to a string representation
        deserialized = json.loads(result)
        assert deserialized["outer"]["inner"] == "<generator object>"
        assert deserialized["outer"]["normal"] == "value"
