import pytest
import glob
import os
from typing import List, Optional, Set, Tuple

current_file_path = os.path.abspath(__file__)
current_dir = os.path.dirname(os.path.abspath(__file__))


def _get_fixtures(
    subdirectory: str,
    exclude_fixtures: Optional[Set[str]] = None,
    include_fixtures: Optional[Set[str]] = None,
) -> List[str]:
    all_fixtures = glob.glob(os.path.join(current_dir, "fixtures", subdirectory, "**"))
    return [
        f
        for f in all_fixtures
        if (exclude_fixtures is None or os.path.basename(f) not in exclude_fixtures)
        and (include_fixtures is None or os.path.basename(f) in include_fixtures)
    ]


def _get_fixture_paths(root: str) -> Tuple[str, str, str]:
    original_file_path = os.path.join(root, "original.py")
    generated_file_path = os.path.join(root, "generated.py")
    expected_file_path = os.path.join(root, "expected.py")

    return original_file_path, generated_file_path, expected_file_path


_node_fixture_paths = _get_fixtures("nodes")
_node_fixture_ids = [os.path.basename(path) for path in _node_fixture_paths]


@pytest.fixture(
    params=_node_fixture_paths,
    ids=_node_fixture_ids,
)
def node_file_contents(request) -> Tuple[str, str, str]:
    root = request.param
    original_file_path, generated_file_path, expected_file_path = _get_fixture_paths(root)

    with open(original_file_path) as original_file:
        original_file_contents = original_file.read()

    with open(generated_file_path) as generated_file:
        generated_file_contents = generated_file.read()

    with open(expected_file_path) as expected_file:
        expected_file_contents = expected_file.read()

    return original_file_contents, generated_file_contents, expected_file_contents


def read_fixture_file(file_name: str) -> str:
    path = os.path.join(current_dir, "fixtures", file_name)
    with open(path) as file:
        return file.read()
