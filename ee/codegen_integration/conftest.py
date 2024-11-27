import pytest
import glob
import os
from typing import List, Optional, Set, Tuple

current_file_path = os.path.abspath(__file__)
current_dir = os.path.dirname(os.path.abspath(__file__))
all_fixtures = glob.glob(os.path.join(current_dir, "fixtures/**"))


def _get_fixtures(
    exclude_fixtures: Optional[Set[str]] = None, include_fixtures: Optional[Set[str]] = None
) -> List[str]:
    return [
        f
        for f in all_fixtures
        if (exclude_fixtures is None or os.path.basename(f) not in exclude_fixtures)
        and (include_fixtures is None or os.path.basename(f) in include_fixtures)
    ]


def _get_fixture_paths(root: str) -> Tuple[str, str]:
    display_file = os.path.join(root, "display_data", f"{root.split('/')[-1]}.json")
    code_dir = os.path.join(root, "code")

    return display_file, code_dir


@pytest.fixture(
    params=_get_fixtures(
        # TODO: Remove exclusions on all of these fixtures
        # https://app.shortcut.com/vellum/story/4649/remove-fixture-exclusions-for-serialization
        exclude_fixtures={
            "simple_guardrail_node",
            "simple_map_node",
            "simple_code_execution_node",
        }
    )
)
def code_to_display_fixture_paths(request) -> Tuple[str, str]:
    root = request.param
    return _get_fixture_paths(root)
