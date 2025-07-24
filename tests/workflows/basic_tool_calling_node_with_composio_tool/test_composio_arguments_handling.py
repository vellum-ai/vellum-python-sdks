import json

from vellum.client.types.function_call import FunctionCall
from vellum.client.types.function_call_vellum_value import FunctionCallVellumValue
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

    def test_extract_function_arguments_none_output(self):
        """Test extraction with None function call output"""
        # GIVEN None function call output
        mixin = TestFunctionCallNodeMixin(None)

        # WHEN we extract arguments
        arguments = mixin._extract_function_arguments()

        # THEN we should get empty dict
        assert arguments == {}
