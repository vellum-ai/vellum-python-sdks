"""Tests for error parser utility functions."""

import traceback
from typing import Dict

from vellum_ee.workflows.display.utils.error_parser import (
    extract_code_snippet,
    find_user_code_frame,
    generate_suggestion,
    map_namespace_to_file,
    parse_exception_to_structured_error,
)
from vellum_ee.workflows.display.workflows.base_workflow_display import SerializationError


class TestMapNamespaceToFile:
    """Tests for map_namespace_to_file function."""

    def test_maps_namespace_to_file(self):
        """Test basic namespace to file mapping."""
        result = map_namespace_to_file("AtUlfaZJaEHC6U.nodes.tools", "AtUlfaZJaEHC6U")
        assert result == "nodes/tools.py"

    def test_maps_nested_namespace(self):
        """Test deeply nested namespace mapping."""
        result = map_namespace_to_file("AtUlfaZJaEHC6U.nodes.api.client", "AtUlfaZJaEHC6U")
        assert result == "nodes/api/client.py"

    def test_returns_path_if_no_namespace(self):
        """Test that non-namespace paths are returned as-is."""
        result = map_namespace_to_file("/some/system/path.py", "AtUlfaZJaEHC6U")
        assert result == "/some/system/path.py"

    def test_handles_single_module(self):
        """Test single module name after namespace."""
        result = map_namespace_to_file("AtUlfaZJaEHC6U.workflow", "AtUlfaZJaEHC6U")
        assert result == "workflow.py"


class TestFindUserCodeFrame:
    """Tests for find_user_code_frame function."""

    def test_finds_user_code_frame(self):
        """Test finding frame with namespace."""
        try:
            # Create a traceback by raising an exception
            exec(compile("raise ValueError('test')", "AtUlfaZJaEHC6U.nodes.tools", "exec"))
        except Exception as e:
            tb = traceback.extract_tb(e.__traceback__)
            frame = find_user_code_frame(tb, "AtUlfaZJaEHC6U")
            assert frame is not None
            assert "AtUlfaZJaEHC6U" in frame.filename

    def test_returns_last_frame_as_fallback(self):
        """Test fallback to last frame when no namespace found."""
        try:
            raise ValueError("test")
        except Exception as e:
            tb = traceback.extract_tb(e.__traceback__)
            frame = find_user_code_frame(tb, "NonExistentNamespace")
            assert frame is not None
            # Should return the last frame
            assert frame == tb[-1]

    def test_returns_none_for_empty_traceback(self):
        """Test handling of empty traceback."""
        tb = traceback.StackSummary.from_list([])
        frame = find_user_code_frame(tb, "AtUlfaZJaEHC6U")
        assert frame is None


class TestExtractCodeSnippet:
    """Tests for extract_code_snippet function."""

    def test_extracts_snippet_with_context(self):
        """Test extracting code snippet with surrounding lines."""
        files = {"nodes/tools.py": "line1\nline2\nline3\nline4\nline5"}
        snippet = extract_code_snippet(files, "nodes/tools.py", 3, context_lines=1)
        assert snippet is not None
        assert "line2" in snippet
        assert "→    3 | line3" in snippet
        assert "line4" in snippet

    def test_handles_start_of_file(self):
        """Test snippet extraction at start of file."""
        files = {"workflow.py": "line1\nline2\nline3"}
        snippet = extract_code_snippet(files, "workflow.py", 1, context_lines=2)
        assert snippet is not None
        assert "→    1 | line1" in snippet
        assert "line3" in snippet

    def test_handles_end_of_file(self):
        """Test snippet extraction at end of file."""
        files = {"workflow.py": "line1\nline2\nline3"}
        snippet = extract_code_snippet(files, "workflow.py", 3, context_lines=2)
        assert snippet is not None
        assert "line1" in snippet
        assert "→    3 | line3" in snippet

    def test_returns_none_for_missing_file(self):
        """Test handling of missing file."""
        files: Dict[str, str] = {}
        snippet = extract_code_snippet(files, "missing.py", 1)
        assert snippet is None

    def test_returns_none_for_invalid_line(self):
        """Test handling of invalid line number."""
        files = {"workflow.py": "line1\nline2"}
        snippet = extract_code_snippet(files, "workflow.py", 100)
        assert snippet is None

    def test_returns_none_for_none_line(self):
        """Test handling of None line number."""
        files = {"workflow.py": "line1\nline2"}
        snippet = extract_code_snippet(files, "workflow.py", None)
        assert snippet is None


class TestGenerateSuggestion:
    """Tests for generate_suggestion function."""

    def test_suggests_import_for_name_error(self):
        """Test suggestion for NameError with capitalized name."""
        exc = NameError("name 'MyClass' is not defined")
        suggestion = generate_suggestion(exc, "nodes/tools.py")
        assert suggestion is not None
        assert "Did you forget to import MyClass?" == suggestion

    def test_suggests_check_for_lowercase_name_error(self):
        """Test suggestion for NameError with lowercase name."""
        exc = NameError("name 'my_var' is not defined")
        suggestion = generate_suggestion(exc, "workflow.py")
        assert suggestion is not None
        assert "Check if 'my_var' is defined" in suggestion

    def test_suggests_module_installation_for_import_error(self):
        """Test suggestion for ImportError."""
        exc = ImportError("No module named 'requests'")
        suggestion = generate_suggestion(exc, "nodes/api.py")
        assert suggestion is not None
        assert "Ensure 'requests' is installed" in suggestion

    def test_suggests_module_installation_for_module_not_found(self):
        """Test suggestion for ModuleNotFoundError."""
        exc = ModuleNotFoundError("No module named 'pandas'")
        suggestion = generate_suggestion(exc, "nodes/data.py")
        assert suggestion is not None
        assert "Ensure 'pandas' is installed" in suggestion

    def test_suggests_attribute_check(self):
        """Test suggestion for AttributeError."""
        exc = AttributeError("'str' object has no attribute 'append'")
        suggestion = generate_suggestion(exc, "workflow.py")
        assert suggestion is not None
        assert "Check if 'append' exists on str objects" in suggestion

    def test_suggests_argument_check_for_type_error(self):
        """Test suggestion for TypeError with missing arguments."""
        exc = TypeError("missing 1 required positional argument")
        suggestion = generate_suggestion(exc, "nodes/tools.py")
        assert suggestion is not None
        assert "required arguments are provided" in suggestion

    def test_suggests_syntax_fix(self):
        """Test suggestion for SyntaxError."""
        exc = SyntaxError("invalid syntax")
        suggestion = generate_suggestion(exc, "workflow.py")
        assert suggestion is not None
        assert "Fix the syntax error" in suggestion

    def test_suggests_indentation_fix(self):
        """Test suggestion for IndentationError."""
        exc = IndentationError("unexpected indent")
        suggestion = generate_suggestion(exc, "workflow.py")
        assert suggestion is not None
        assert "indentation" in suggestion

    def test_returns_none_for_unknown_error(self):
        """Test that unknown errors return None."""
        exc = RuntimeError("Some runtime error")
        suggestion = generate_suggestion(exc, "workflow.py")
        assert suggestion is None


class TestParseExceptionToStructuredError:
    """Tests for parse_exception_to_structured_error function."""

    def test_parses_basic_exception(self):
        """Test parsing a basic exception into structured error."""
        files = {"nodes/tools.py": "line1\nraise NameError('test')\nline3"}

        try:
            exec(compile("raise NameError(\"name 'MyClass' is not defined\")", "AtUlfaZJaEHC6U.nodes.tools", "exec"))
        except Exception as exc:
            error = parse_exception_to_structured_error(exc, files, "AtUlfaZJaEHC6U", include_debug=False)

            assert isinstance(error, SerializationError)
            assert error.file == "nodes/tools.py"
            assert error.error_type == "NameError"
            assert "MyClass" in error.message
            assert error.suggestion is not None
            assert "import MyClass" in error.suggestion
            assert error.debug is None

    def test_includes_debug_info_when_requested(self):
        """Test that debug info is included when requested."""
        files = {"workflow.py": "raise ValueError('test')"}

        try:
            exec(compile("raise ValueError('test error')", "AtUlfaZJaEHC6U.workflow", "exec"))
        except Exception as exc:
            error = parse_exception_to_structured_error(exc, files, "AtUlfaZJaEHC6U", include_debug=True)

            assert error.debug is not None
            assert "full_traceback" in error.debug
            assert "namespace" in error.debug
            assert error.debug["namespace"] == "AtUlfaZJaEHC6U"
            assert "ValueError" in error.debug["full_traceback"]

    def test_excludes_debug_info_by_default(self):
        """Test that debug info is excluded by default."""
        files = {"workflow.py": "raise ValueError('test')"}

        try:
            exec(compile("raise ValueError('test')", "AtUlfaZJaEHC6U.workflow", "exec"))
        except Exception as exc:
            error = parse_exception_to_structured_error(exc, files, "AtUlfaZJaEHC6U")

            assert error.debug is None

    def test_handles_exception_without_user_frame(self):
        """Test handling exception without user code frame."""
        files: Dict[str, str] = {}

        try:
            raise ValueError("test error")
        except Exception as exc:
            error = parse_exception_to_structured_error(exc, files, "NonExistentNamespace")

            # When no namespace match found, it uses the last frame (which will be this test file)
            # Just verify that file is set to something
            assert error.file is not None
            assert error.code_snippet is None
            assert error.error_type == "ValueError"

    def test_can_serialize_to_dict(self):
        """Test that SerializationError can be serialized to dict."""
        files = {"workflow.py": "line1\nline2\nline3"}

        try:
            exec(compile("raise NameError('test')", "AtUlfaZJaEHC6U.workflow", "exec"))
        except Exception as exc:
            error = parse_exception_to_structured_error(exc, files, "AtUlfaZJaEHC6U")

            # Should be able to convert to dict
            error_dict = error.model_dump()
            assert isinstance(error_dict, dict)
            assert "file" in error_dict
            assert "error_type" in error_dict
            assert "message" in error_dict
