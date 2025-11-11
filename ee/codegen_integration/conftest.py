import pytest
from datetime import datetime
import glob
import importlib
from io import StringIO
import json
import os
import sys
from unittest.mock import patch
from uuid import uuid4
from typing import List, Optional, Set, Tuple

from vellum import DeploymentRead, WorkspaceSecretRead
from vellum.workflows.triggers.base import _get_trigger_path_to_id_mapping

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


_fixture_paths = _get_fixtures(
    # TODO: Remove exclusions on all of these fixtures
    # https://app.shortcut.com/vellum/story/4649/remove-fixture-exclusions-for-serialization
    exclude_fixtures={
        "simple_search_node",
        # TODO: Remove once serialization support is in
        "simple_workflow_node_with_output_values",
    }
)
_fixture_ids = [os.path.basename(path) for path in _fixture_paths]


@pytest.fixture(
    params=_fixture_paths,
    ids=_fixture_ids,
)
def code_to_display_fixture_paths(request) -> Tuple[str, str]:
    root = request.param
    return _get_fixture_paths(root)


@pytest.fixture
def workspace_secret_client(vellum_client):
    workspace_secret = WorkspaceSecretRead(
        id="cecd16a2-4de5-444d-acff-37a5c400600c",
        modified=datetime.now(),
        name="MY_SECRET",
        label="My Secret",
        secret_type="USER_DEFINED",
    )
    vellum_client.workspace_secrets.retrieve.return_value = workspace_secret


@pytest.fixture
def deployment_client(vellum_client):
    deployment = DeploymentRead(
        id="e68d6033-f3e6-4681-a7b9-6bfd2828a237",
        created=datetime.now(),
        label="Example Deployment",
        name="example deployment",
        last_deployed_on=datetime.now(),
        input_variables=[],
        active_model_version_ids=[],
        last_deployed_history_item_id=str(uuid4()),
    )
    vellum_client.workflow_deployments.retrieve.return_value = deployment


@pytest.fixture(autouse=True)
def mock_trigger_metadata():
    """Mock virtual_open to return metadata.json with trigger path to ID mapping."""

    _get_trigger_path_to_id_mapping.cache_clear()

    metadata_content = {
        "trigger_path_to_id_mapping": {".triggers.scheduled.Scheduled": "c484ce55-a392-4a1b-8c10-1233b81c4539"},
        "edges_to_id_mapping": {
            "vellum.workflows.triggers.manual.Manual|codegen_integration.fixtures.simple_scheduled_trigger.code.nodes.output.Output.Trigger": "42a1cc56-f544-4864-afa5-33d399d4e7eb",  # noqa: E501
            "codegen_integration.fixtures.simple_scheduled_trigger.code.triggers.scheduled.Scheduled|codegen_integration.fixtures.simple_scheduled_trigger.code.nodes.output.Output.Trigger": "43083a12-5c4a-4839-ad92-8221f54ddfd3",  # noqa: E501
        },
    }

    original_virtual_open = __import__("vellum.workflows.utils.files", fromlist=["virtual_open"]).virtual_open

    def mock_virtual_open(file_path: str):
        # Normalize the file path
        normalized_path = file_path.replace(os.path.sep, "/")

        if normalized_path.endswith("codegen_integration/fixtures/simple_scheduled_trigger/code/metadata.json"):
            return StringIO(json.dumps(metadata_content))

        # Fall back to original implementation
        return original_virtual_open(file_path)

    # Patch virtual_open
    with patch("vellum.workflows.utils.files.virtual_open", side_effect=mock_virtual_open), patch(
        "vellum.workflows.triggers.base.virtual_open", side_effect=mock_virtual_open
    ), patch("vellum_ee.workflows.display.workflows.base_workflow_display.virtual_open", side_effect=mock_virtual_open):

        # Reload any already-imported trigger modules to pick up the mocked metadata
        modules_to_reload = [name for name in sys.modules if "fixtures" in name and "triggers" in name]
        for module_name in modules_to_reload:
            importlib.reload(sys.modules[module_name])

        yield

    # Clear cache after test
    _get_trigger_path_to_id_mapping.cache_clear()
