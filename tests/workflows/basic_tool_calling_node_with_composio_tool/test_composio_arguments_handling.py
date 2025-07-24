import json
from unittest.mock import MagicMock, Mock, patch

import requests

from vellum.client.types.function_call import FunctionCall
from vellum.client.types.function_call_vellum_value import FunctionCallVellumValue
from vellum.workflows.nodes.displayable.tool_calling_node.composio_service import ComposioCoreService
from vellum.workflows.nodes.displayable.tool_calling_node.utils import FunctionCallNodeMixin


class TestFunctionCallNodeMixin(FunctionCallNodeMixin):
    """Test implementation of FunctionCallNodeMixin"""

    def __init__(self, function_call_output):
        self.function_call_output = function_call_output


class TestComposioArgumentsHandling:
    """Test that Composio tool arguments are handled correctly"""

    def test_extract_function_arguments_normal_format(self):
        """Test extraction with normal argument format"""
        # GIVEN a function call output with normal arguments
        function_call_value = FunctionCall(name="test_function", arguments={"body": "Hello world", "title": "Test"})
        function_call_output = [FunctionCallVellumValue(type="FUNCTION_CALL", value=function_call_value)]

        # WHEN we extract arguments
        mixin = TestFunctionCallNodeMixin(function_call_output)
        arguments = mixin._extract_function_arguments()

        # THEN we should get the arguments as-is
        assert arguments == {"body": "Hello world", "title": "Test"}

    def test_extract_function_arguments_kwargs_wrapper(self):
        """Test extraction with kwargs wrapper (Composio case)"""
        # GIVEN a function call output with kwargs-wrapped arguments
        function_call_value = FunctionCall(
            name="gmail_create_email_draft", arguments={"kwargs": '{"body": "Hello world"}'}
        )
        function_call_output = [FunctionCallVellumValue(type="FUNCTION_CALL", value=function_call_value)]

        # WHEN we extract arguments
        mixin = TestFunctionCallNodeMixin(function_call_output)
        arguments = mixin._extract_function_arguments()

        # THEN we should get the unwrapped arguments
        assert arguments == {"body": "Hello world"}

    def test_extract_function_arguments_kwargs_complex_data(self):
        """Test extraction with complex data in kwargs wrapper"""
        # GIVEN a function call output with complex kwargs-wrapped arguments
        complex_args = {"body": "Hello world", "recipients": ["user@example.com"], "metadata": {"priority": "high"}}
        function_call_value = FunctionCall(
            name="gmail_create_email_draft", arguments={"kwargs": json.dumps(complex_args)}
        )
        function_call_output = [FunctionCallVellumValue(type="FUNCTION_CALL", value=function_call_value)]

        # WHEN we extract arguments
        mixin = TestFunctionCallNodeMixin(function_call_output)
        arguments = mixin._extract_function_arguments()

        # THEN we should get the unwrapped complex arguments
        assert arguments == complex_args

    def test_extract_function_arguments_invalid_json_kwargs(self):
        """Test extraction with invalid JSON in kwargs wrapper"""
        # GIVEN a function call output with invalid JSON in kwargs
        function_call_value = FunctionCall(name="test_function", arguments={"kwargs": "invalid json {"})
        function_call_output = [FunctionCallVellumValue(type="FUNCTION_CALL", value=function_call_value)]

        # WHEN we extract arguments
        mixin = TestFunctionCallNodeMixin(function_call_output)
        arguments = mixin._extract_function_arguments()

        # THEN we should fall back to original arguments
        assert arguments == {"kwargs": "invalid json {"}

    def test_extract_function_arguments_kwargs_not_only_key(self):
        """Test extraction when kwargs is not the only key"""
        # GIVEN a function call output with kwargs plus other keys
        function_call_value = FunctionCall(
            name="test_function", arguments={"kwargs": '{"body": "Hello"}', "other_param": "value"}
        )
        function_call_output = [FunctionCallVellumValue(type="FUNCTION_CALL", value=function_call_value)]

        # WHEN we extract arguments
        mixin = TestFunctionCallNodeMixin(function_call_output)
        arguments = mixin._extract_function_arguments()

        # THEN we should not unwrap kwargs (return original)
        assert arguments == {"kwargs": '{"body": "Hello"}', "other_param": "value"}

    def test_extract_function_arguments_empty_output(self):
        """Test extraction with empty function call output"""
        # GIVEN empty function call output
        mixin = TestFunctionCallNodeMixin([])

        # WHEN we extract arguments
        arguments = mixin._extract_function_arguments()

        # THEN we should get empty dict
        assert arguments == {}


class TestComposioCoreServiceHTTPSchema:
    """Test HTTP-based schema fetching functionality"""

    @patch("requests.get")
    def test_get_tool_schema_from_api_success(self, mock_get):
        """Test successful HTTP API call for tool schema"""
        # GIVEN a ComposioCoreService with API key
        service = ComposioCoreService("test_api_key")

        # AND a mock successful HTTP response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "name": "Gmail Create Email Draft",
            "input_parameters": {
                "body": {"type": "string", "description": "Email body content", "required": True},
                "subject": {
                    "type": "string",
                    "description": "Email subject",
                    "required": False,
                    "default": "No Subject",
                },
            },
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        # WHEN we fetch tool schema
        schema = service.get_tool_schema_from_api("GMAIL_CREATE_EMAIL_DRAFT")

        # THEN the HTTP request should be made correctly
        mock_get.assert_called_once_with(
            "https://backend.composio.dev/api/v3/tools/GMAIL_CREATE_EMAIL_DRAFT",
            headers={"x-api-key": "test_api_key"},
            timeout=10,
        )

        # AND we should get the schema data
        assert schema is not None
        assert schema["name"] == "Gmail Create Email Draft"
        assert "input_parameters" in schema
        assert "body" in schema["input_parameters"]

    @patch("requests.get")
    def test_get_tool_schema_from_api_http_error(self, mock_get):
        """Test HTTP error during schema fetch"""
        # GIVEN a ComposioCoreService
        service = ComposioCoreService("test_api_key")

        # AND a mock HTTP error response
        mock_get.side_effect = requests.exceptions.RequestException("HTTP 404 Not Found")

        # WHEN we fetch tool schema
        schema = service.get_tool_schema_from_api("INVALID_TOOL")

        # THEN we should get None
        assert schema is None

    @patch("requests.get")
    def test_get_tool_schema_from_api_json_error(self, mock_get):
        """Test JSON parsing error during schema fetch"""
        # GIVEN a ComposioCoreService
        service = ComposioCoreService("test_api_key")

        # AND a mock response with invalid JSON
        mock_response = MagicMock()
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        # WHEN we fetch tool schema
        schema = service.get_tool_schema_from_api("GMAIL_CREATE_EMAIL_DRAFT")

        # THEN we should get None
        assert schema is None

    @patch("requests.get")
    def test_get_tool_schema_caching(self, mock_get):
        """Test that schema results are cached"""
        # GIVEN a ComposioCoreService
        service = ComposioCoreService("test_api_key")

        # AND a mock successful HTTP response
        mock_response = MagicMock()
        mock_response.json.return_value = {"name": "Test Tool", "input_parameters": {}}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        # WHEN we fetch the same tool schema twice
        schema1 = service.get_tool_schema_from_api("TEST_TOOL")
        schema2 = service.get_tool_schema_from_api("TEST_TOOL")

        # THEN HTTP should only be called once (cached on second call)
        assert mock_get.call_count == 1
        assert schema1 == schema2

    @patch.object(ComposioCoreService, "get_tool_schema_from_api")
    def test_get_tool_arguments_with_http_schema(self, mock_schema_api):
        """Test argument processing with HTTP-fetched schema"""
        # GIVEN a ComposioCoreService
        service = ComposioCoreService("test_api_key")

        # AND a mock schema from HTTP API
        mock_schema_api.return_value = {
            "name": "Gmail Create Email Draft",
            "input_parameters": {
                "body": {"type": "string", "description": "Email body content", "required": True},
                "subject": {
                    "type": "string",
                    "description": "Email subject",
                    "required": False,
                    "default": "No Subject",
                },
            },
        }

        # AND provided arguments with kwargs wrapper
        provided_args = {"kwargs": '{"body": "Hello World", "subject": "Test Email"}'}

        # WHEN we get tool arguments
        result = service.get_tool_arguments("GMAIL_CREATE_EMAIL_DRAFT", provided_args)

        # THEN the HTTP schema API should be called
        mock_schema_api.assert_called_once_with("GMAIL_CREATE_EMAIL_DRAFT")

        # AND arguments should be properly parsed and validated
        assert result == {"body": "Hello World", "subject": "Test Email"}

    @patch.object(ComposioCoreService, "get_tool_schema_from_api")
    def test_get_tool_arguments_http_fallback(self, mock_schema_api):
        """Test fallback when HTTP schema fetch fails"""
        # GIVEN a ComposioCoreService
        service = ComposioCoreService("test_api_key")

        # AND HTTP schema fetch returns None (failed)
        mock_schema_api.return_value = None

        # AND provided arguments with kwargs wrapper
        provided_args = {"kwargs": '{"body": "Hello World"}'}

        # WHEN we get tool arguments
        result = service.get_tool_arguments("GMAIL_CREATE_EMAIL_DRAFT", provided_args)

        # THEN we should fall back to raw argument parsing
        assert result == {"body": "Hello World"}

    @patch.object(ComposioCoreService, "get_tool_schema_from_api")
    def test_get_tool_arguments_missing_required_warning(self, mock_schema_api):
        """Test warning for missing required parameters (no failure)"""
        # GIVEN a ComposioCoreService
        service = ComposioCoreService("test_api_key")

        # AND a mock schema with required parameters
        mock_schema_api.return_value = {
            "name": "Test Tool",
            "input_parameters": {
                "required_param": {"type": "string", "required": True},
                "optional_param": {"type": "string", "required": False, "default": "default_value"},
            },
        }

        # AND provided arguments missing the required parameter
        provided_args = {"kwargs": '{"other_param": "value"}'}

        # WHEN we get tool arguments (should not raise an exception)
        result = service.get_tool_arguments("TEST_TOOL", provided_args)

        # THEN we should get the optional parameter with default value
        # and the function should not fail (just log warning)
        assert result == {"optional_param": "default_value"}

    def test_extract_function_arguments_none_output(self):
        """Test extraction with None function call output"""
        # GIVEN None function call output
        mixin = TestFunctionCallNodeMixin(None)

        # WHEN we extract arguments
        arguments = mixin._extract_function_arguments()

        # THEN we should get empty dict
        assert arguments == {}
