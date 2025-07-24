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

    def test_extract_function_arguments_complex_data(self):
        """Test extraction with complex data structures"""
        # GIVEN a function call output with complex arguments
        complex_args = {"body": "Hello world", "recipients": ["user@example.com"], "metadata": {"priority": "high"}}
        function_call_value = FunctionCall(name="gmail_create_email_draft", arguments=complex_args)
        function_call_output = [FunctionCallVellumValue(type="FUNCTION_CALL", value=function_call_value)]

        # WHEN we extract arguments
        mixin = TestFunctionCallNodeMixin(function_call_output)
        arguments = mixin._extract_function_arguments()

        # THEN we should get the complex arguments as-is
        assert arguments == complex_args

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

    def test_extract_function_arguments_none_value(self):
        """Test extraction when function call value is None"""
        # GIVEN a function call output with None value
        function_call_output = [FunctionCallVellumValue(type="FUNCTION_CALL", value=None)]

        # WHEN we extract arguments
        mixin = TestFunctionCallNodeMixin(function_call_output)
        arguments = mixin._extract_function_arguments()

        # THEN we should get empty dict
        assert arguments == {}

    def test_extract_function_arguments_no_arguments(self):
        """Test extraction when function call has no arguments"""
        # GIVEN a function call with no arguments
        function_call_value = FunctionCall(name="test_function", arguments=None)
        function_call_output = [FunctionCallVellumValue(type="FUNCTION_CALL", value=function_call_value)]

        # WHEN we extract arguments
        mixin = TestFunctionCallNodeMixin(function_call_output)
        arguments = mixin._extract_function_arguments()

        # THEN we should get empty dict
        assert arguments == {}
