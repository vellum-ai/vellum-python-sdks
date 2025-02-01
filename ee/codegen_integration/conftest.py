import pytest
from datetime import datetime
import glob
import os
from uuid import uuid4
from typing import List, Optional, Set, Tuple

from vellum import DeploymentRead, WorkspaceSecretRead

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
        "faa_q_and_a_bot",
        "simple_search_node",
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
