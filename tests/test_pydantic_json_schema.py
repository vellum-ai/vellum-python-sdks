import pytest

from pydantic import BaseModel

from vellum.client.core.pydantic_utilities import convert_pydantic_to_json_schema
from vellum.client.types.prompt_parameters import PromptParameters


class TestPydanticJsonSchemaConversion:
    def test_dict_passthrough(self):
        """Test that existing dict schemas pass through unchanged."""
        schema_dict = {"type": "object", "properties": {"name": {"type": "string"}}, "required": ["name"]}
        result = convert_pydantic_to_json_schema(schema_dict)
        assert result == schema_dict

    def test_pydantic_model_class_conversion(self):
        """Test conversion of Pydantic model class to JSON schema."""

        class TestModel(BaseModel):
            name: str
            age: int
            email: str = "default@example.com"

        result = convert_pydantic_to_json_schema(TestModel)

        assert result["type"] == "object"
        assert "properties" in result
        assert "name" in result["properties"]
        assert "age" in result["properties"]
        assert "email" in result["properties"]
        assert result["properties"]["name"]["type"] == "string"
        assert result["properties"]["age"]["type"] == "integer"
        assert "required" in result
        assert "name" in result["required"]
        assert "age" in result["required"]
        assert "email" not in result["required"]

    def test_pydantic_model_instance_conversion(self):
        """Test conversion of Pydantic model instance to JSON schema."""

        class TestModel(BaseModel):
            name: str
            age: int

        instance = TestModel(name="test", age=25)
        result = convert_pydantic_to_json_schema(instance)

        assert result["type"] == "object"
        assert "properties" in result
        assert "name" in result["properties"]
        assert "age" in result["properties"]

    def test_invalid_input_raises_error(self):
        """Test that invalid input types raise ValueError."""
        with pytest.raises(ValueError, match="Expected Pydantic model class/instance or dict"):
            convert_pydantic_to_json_schema("invalid_input")

    def test_prompt_parameters_integration(self):
        """Test integration with PromptParameters custom_parameters."""

        class ResponseModel(BaseModel):
            result: str
            confidence: float

        params = PromptParameters(custom_parameters={"json_schema": {"name": "get_result", "schema": ResponseModel}})

        serialized = params.dict()
        assert "custom_parameters" in serialized
        assert "json_schema" in serialized["custom_parameters"]
        assert "schema" in serialized["custom_parameters"]["json_schema"]

        schema = serialized["custom_parameters"]["json_schema"]["schema"]
        assert schema["type"] == "object"
        assert "properties" in schema
        assert "result" in schema["properties"]
        assert "confidence" in schema["properties"]

    def test_backward_compatibility_with_dict_schema(self):
        """Test that existing dict schemas continue to work."""
        params = PromptParameters(
            custom_parameters={
                "json_schema": {
                    "name": "get_result",
                    "schema": {"type": "object", "properties": {"result": {"type": "string"}}, "required": ["result"]},
                }
            }
        )

        serialized = params.dict()
        schema = serialized["custom_parameters"]["json_schema"]["schema"]
        assert schema["type"] == "object"
        assert schema["properties"]["result"]["type"] == "string"
        assert schema["required"] == ["result"]

    def test_complex_pydantic_model(self):
        """Test conversion of complex Pydantic model with various field types."""

        class ComplexModel(BaseModel):
            name: str
            age: int
            height: float
            is_active: bool
            tags: list
            metadata: dict

        result = convert_pydantic_to_json_schema(ComplexModel)

        assert result["type"] == "object"
        properties = result["properties"]
        assert properties["name"]["type"] == "string"
        assert properties["age"]["type"] == "integer"
        assert properties["height"]["type"] == "number"
        assert properties["is_active"]["type"] == "boolean"
        assert properties["tags"]["type"] == "array"
        assert properties["metadata"]["type"] == "object"

        assert len(result["required"]) == 6
