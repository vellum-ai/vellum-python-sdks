import black.parsing
from python_file_merging.nodes import merge_python_file, merge_python_files
from python_file_merging.tests.conftest import read_fixture_file


def test_merge_python_file(node_file_contents):
    # GIVEN an original file and a generated file, and we know what the expected merged file should look like
    original_file_contents, generated_file_contents, expected_file_contents = node_file_contents

    # WHEN we merge the generated file with the original file
    actual = merge_python_file(original_file_contents, generated_file_contents, "filename.py")

    # THEN the merged file should match the expected file
    assert actual == expected_file_contents


def test_merge_python_files():
    # GIVEN an original file and a generated file, and we know what the expected merged file should look like
    # and we put them into a file map with some other files where some only exist in the original and vice versa
    original_file_map = {
        "base.py": read_fixture_file("nodes/existing_internal_statements/original.py"),
        "base2.py": read_fixture_file("nodes/existing_internal_statements/original.py"),
    }

    generated_file_map = {
        "base.py": read_fixture_file("nodes/existing_internal_statements/generated.py"),
        "base3.py": read_fixture_file("nodes/existing_internal_statements/generated.py"),
    }

    # WHEN we merge file maps together
    actual = merge_python_files(original_file_map, generated_file_map)

    # THEN the merged file map should have the expected contents and have all files from the generated file map but
    # not have any files from the original file map that are not in the generated map
    assert actual == {
        "base.py": read_fixture_file("nodes/existing_internal_statements/expected.py"),
        "base3.py": read_fixture_file("nodes/existing_internal_statements/generated.py"),
    }


def test_merge_python_file_black_formatting_failure(mocker):
    """
    Tests that merge_python_file continues processing when black formatting fails.
    """
    original_file_contents = """
class TestNode:
    def __init__(self):
        pass
"""
    generated_file_contents = """
class TestNode:
    def run(self):
        return "test"
"""

    mock_black_format = mocker.patch("python_file_merging.nodes.black.format_str")
    mock_black_format.side_effect = black.parsing.InvalidInput("Cannot parse: 11:0: <line number missing in source>")

    mock_logger = mocker.patch("python_file_merging.nodes.logging.exception")

    # WHEN we merge the files
    result = merge_python_file(original_file_contents, generated_file_contents, "test_file.py")

    # THEN the merge should complete successfully with unformatted code
    assert "def run(self):" in result
    assert "return 'test'" in result

    mock_logger.assert_called_once_with("Black formatting failed for file: %s", "test_file.py")
