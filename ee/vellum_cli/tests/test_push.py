import pytest
import io
import json
import os
import tarfile
from unittest import mock
from uuid import uuid4

from click.testing import CliRunner

from vellum.client.core.api_error import ApiError
from vellum.client.types.workflow_push_response import WorkflowPushResponse
from vellum.utils.uuid import is_valid_uuid
from vellum_cli import main as cli_main


def _extract_tar_gz(tar_gz_bytes: bytes) -> dict[str, str]:
    files = {}
    with tarfile.open(fileobj=io.BytesIO(tar_gz_bytes), mode="r:gz") as tar:
        for member in tar.getmembers():
            if not member.isfile():
                continue
            content = tar.extractfile(member)
            if content is None:
                continue

            files[member.name] = content.read().decode("latin-1")

    return files


def _ensure_workflow_py(temp_dir: str, module: str) -> str:
    base_dir = os.path.join(temp_dir, *module.split("."))
    os.makedirs(base_dir, exist_ok=True)
    workflow_py_file_content = """\
from vellum.workflows import BaseWorkflow

class ExampleWorkflow(BaseWorkflow):
    pass
"""
    with open(os.path.join(temp_dir, *module.split("."), "workflow.py"), "w") as f:
        f.write(workflow_py_file_content)

    return workflow_py_file_content


def test_push__no_config(mock_module):
    # GIVEN no config file set
    mock_module.set_pyproject_toml({"workflows": []})

    # WHEN calling `vellum push`
    runner = CliRunner()
    result = runner.invoke(cli_main, ["push"])

    # THEN it should fail
    assert result.exit_code == 1
    assert result.exception
    assert str(result.exception) == "No Workflows found in project to push."


def test_push__multiple_workflows_configured__no_module_specified(mock_module):
    # GIVEN multiple workflows configured
    mock_module.set_pyproject_toml({"workflows": [{"module": "examples.mock"}, {"module": "examples.mock2"}]})

    # WHEN calling `vellum push` without a module specified
    runner = CliRunner()
    result = runner.invoke(cli_main, ["push"])

    # THEN it should fail
    assert result.exit_code == 1
    assert result.exception
    assert (
        str(result.exception)
        == "Multiple workflows found in project to push. Pushing only a single workflow is supported."
    )


def test_push__multiple_workflows_configured__not_found_module(mock_module):
    # GIVEN multiple workflows configured
    module = mock_module.module
    mock_module.set_pyproject_toml({"workflows": [{"module": "examples.mock2"}, {"module": "examples.mock3"}]})

    # WHEN calling `vellum push` with a module that doesn't exist
    runner = CliRunner()
    result = runner.invoke(cli_main, ["push", module])

    # THEN it should fail
    assert result.exit_code == 1
    assert result.exception
    assert str(result.exception) == f"No workflow config for '{module}' found in project to push."


@pytest.mark.parametrize(
    "base_command",
    [
        ["push"],
        ["workflows", "push"],
    ],
    ids=["push", "workflows_push"],
)
def test_push__happy_path(mock_module, vellum_client, base_command):
    # GIVEN a single workflow configured
    temp_dir = mock_module.temp_dir
    module = mock_module.module

    # AND a workflow exists in the module successfully
    workflow_py_file_content = _ensure_workflow_py(temp_dir, module)

    # AND the push API call returns successfully
    vellum_client.workflows.push.return_value = WorkflowPushResponse(
        workflow_sandbox_id=str(uuid4()),
    )

    # WHEN calling `vellum push`
    runner = CliRunner()
    result = runner.invoke(cli_main, base_command + [module])

    # THEN it should succeed
    assert result.exit_code == 0

    # Get the last part of the module path and format it
    expected_artifact_name = f"{mock_module.module.replace('.', '__')}.tar.gz"

    # AND we should have called the push API with the correct args
    vellum_client.workflows.push.assert_called_once()
    call_args = vellum_client.workflows.push.call_args.kwargs
    assert json.loads(call_args["exec_config"])["workflow_raw_data"]["definition"]["name"] == "ExampleWorkflow"
    assert is_valid_uuid(call_args["workflow_sandbox_id"])
    assert call_args["artifact"].name == expected_artifact_name
    assert "deplyment_config" not in call_args

    extracted_files = _extract_tar_gz(call_args["artifact"].read())
    assert extracted_files["workflow.py"] == workflow_py_file_content


@pytest.mark.parametrize(
    "base_command",
    [
        ["push"],
        ["workflows", "push"],
    ],
    ids=["push", "workflows_push"],
)
def test_push__workflow_sandbox_option__existing_id(mock_module, vellum_client, base_command):
    # GIVEN a single workflow configured
    temp_dir = mock_module.temp_dir
    module = mock_module.module
    existing_workflow_sandbox_id = mock_module.workflow_sandbox_id

    # AND a workflow exists in the module successfully
    workflow_py_file_content = _ensure_workflow_py(temp_dir, module)

    # AND the push API call would return successfully
    vellum_client.workflows.push.return_value = WorkflowPushResponse(
        workflow_sandbox_id=existing_workflow_sandbox_id,
    )

    # WHEN calling `vellum push` with the workflow sandbox option on an existing config
    runner = CliRunner()
    result = runner.invoke(cli_main, base_command + [module, "--workflow-sandbox-id", existing_workflow_sandbox_id])

    # THEN it should succeed
    assert result.exit_code == 0

    # Get the last part of the module path and format it
    expected_artifact_name = f"{mock_module.module.replace('.', '__')}.tar.gz"

    # AND we should have called the push API with the correct args
    vellum_client.workflows.push.assert_called_once()
    call_args = vellum_client.workflows.push.call_args.kwargs
    assert json.loads(call_args["exec_config"])["workflow_raw_data"]["definition"]["name"] == "ExampleWorkflow"
    assert call_args["workflow_sandbox_id"] == existing_workflow_sandbox_id
    assert call_args["artifact"].name == expected_artifact_name
    assert "deplyment_config" not in call_args

    extracted_files = _extract_tar_gz(call_args["artifact"].read())
    assert extracted_files["workflow.py"] == workflow_py_file_content


def test_push__workflow_sandbox_option__existing_no_module(mock_module, vellum_client):
    # GIVEN a single workflow configured
    temp_dir = mock_module.temp_dir
    first_module = mock_module.module
    second_module = f"{first_module}2"
    first_workflow_sandbox_id = mock_module.workflow_sandbox_id
    second_workflow_sandbox_id = str(uuid4())

    # AND the pyproject.toml has two workflow sandboxes configured
    mock_module.set_pyproject_toml(
        {
            "workflows": [
                {"module": first_module, "workflow_sandbox_id": first_workflow_sandbox_id},
                {"module": second_module, "workflow_sandbox_id": second_workflow_sandbox_id},
            ]
        }
    )

    # AND a workflow exists for both modules
    _ensure_workflow_py(temp_dir, first_module)
    workflow_py_file_content = _ensure_workflow_py(temp_dir, second_module)

    # AND the push API call would return successfully for the second module
    vellum_client.workflows.push.return_value = WorkflowPushResponse(
        workflow_sandbox_id=second_workflow_sandbox_id,
    )

    # WHEN calling `vellum push` with the workflow sandbox option on the second module
    runner = CliRunner()
    result = runner.invoke(cli_main, ["workflows", "push", "--workflow-sandbox-id", second_workflow_sandbox_id])

    # THEN it should succeed
    assert result.exit_code == 0

    # Get the last part of the module path and format it
    expected_artifact_name = f"{second_module.replace('.', '__')}.tar.gz"

    # AND we should have called the push API with the correct args
    vellum_client.workflows.push.assert_called_once()
    call_args = vellum_client.workflows.push.call_args.kwargs
    assert json.loads(call_args["exec_config"])["workflow_raw_data"]["definition"]["name"] == "ExampleWorkflow"
    assert call_args["workflow_sandbox_id"] == second_workflow_sandbox_id
    assert call_args["artifact"].name == expected_artifact_name
    assert "deplyment_config" not in call_args

    extracted_files = _extract_tar_gz(call_args["artifact"].read())
    assert extracted_files["workflow.py"] == workflow_py_file_content


def test_push__workflow_sandbox_option__existing_id_different_module(mock_module):
    # GIVEN a single workflow configured
    temp_dir = mock_module.temp_dir
    module = mock_module.module
    second_module = f"{module}2"
    first_workflow_sandbox_id = mock_module.workflow_sandbox_id
    second_workflow_sandbox_id = str(uuid4())
    set_pyproject_toml = mock_module.set_pyproject_toml

    # AND the pyproject.toml has two workflow sandboxes configured
    set_pyproject_toml(
        {
            "workflows": [
                {"module": module, "workflow_sandbox_id": first_workflow_sandbox_id},
                {"module": second_module, "workflow_sandbox_id": second_workflow_sandbox_id},
            ]
        }
    )

    # AND a workflow exists in both modules successfully
    _ensure_workflow_py(temp_dir, module)
    _ensure_workflow_py(temp_dir, second_module)

    # WHEN calling `vellum push` with the first module and the second workflow sandbox id
    runner = CliRunner()
    result = runner.invoke(cli_main, ["workflows", "push", module, "--workflow-sandbox-id", second_workflow_sandbox_id])

    # THEN it should fail
    assert result.exit_code == 1
    assert result.exception
    assert (
        str(result.exception)
        == "Multiple workflows found in project to push. Pushing only a single workflow is supported."
    )


@pytest.mark.parametrize(
    "base_command",
    [
        ["push"],
        ["workflows", "push"],
    ],
    ids=["push", "workflows_push"],
)
def test_push__deployment(mock_module, vellum_client, base_command):
    # GIVEN a single workflow configured
    temp_dir = mock_module.temp_dir
    module = mock_module.module

    # AND a workflow exists in the module successfully
    workflow_py_file_content = _ensure_workflow_py(temp_dir, module)

    # AND the push API call returns successfully
    vellum_client.workflows.push.return_value = WorkflowPushResponse(
        workflow_sandbox_id=str(uuid4()),
    )

    # WHEN calling `vellum push`
    runner = CliRunner()
    result = runner.invoke(cli_main, base_command + [module, "--deploy"])

    # THEN it should succeed
    assert result.exit_code == 0

    # Get the last part of the module path and format it
    expected_artifact_name = f"{mock_module.module.replace('.', '__')}.tar.gz"

    # AND we should have called the push API with the correct args
    vellum_client.workflows.push.assert_called_once()
    call_args = vellum_client.workflows.push.call_args.kwargs
    assert json.loads(call_args["exec_config"])["workflow_raw_data"]["definition"]["name"] == "ExampleWorkflow"
    assert is_valid_uuid(call_args["workflow_sandbox_id"])
    assert call_args["artifact"].name == expected_artifact_name
    assert call_args["deployment_config"] == "{}"

    extracted_files = _extract_tar_gz(call_args["artifact"].read())
    assert extracted_files["workflow.py"] == workflow_py_file_content


def test_push__dry_run_option_returns_report(mock_module, vellum_client):
    # GIVEN a single workflow configured
    temp_dir = mock_module.temp_dir
    module = mock_module.module

    # AND a workflow exists in the module successfully
    base_dir = os.path.join(temp_dir, *module.split("."))
    os.makedirs(base_dir, exist_ok=True)
    workflow_py_file_content = """\
from typing import Dict
from vellum.workflows import BaseWorkflow
from vellum.workflows.nodes import BaseNode
from vellum_ee.workflows.display.nodes.base_node_display import BaseNodeDisplay

class NotSupportedNode(BaseNode):
    pass

class NotSupportedNodeDisplay(BaseNodeDisplay[NotSupportedNode]):
    def serialize(self, display_context, **kwargs) -> Dict:
        raise NotImplementedError(f"Serialization is not supported.")

class ExampleWorkflow(BaseWorkflow):
    graph = NotSupportedNode
"""
    with open(os.path.join(temp_dir, *module.split("."), "workflow.py"), "w") as f:
        f.write(workflow_py_file_content)

    # AND the push API call returns successfully
    vellum_client.workflows.push.return_value = WorkflowPushResponse(
        workflow_sandbox_id=str(uuid4()),
        proposed_diffs={
            "iterable_item_added": {
                "root['raw_data']['nodes'][0]": {
                    "id": str(uuid4()),
                    "type": "GENERIC",
                    "definition": None,
                    "display_data": None,
                    "trigger": {"id": str(uuid4()), "merge_behavior": "AWAIT_ATTRIBUTES"},
                    "ports": [{"id": str(uuid4()), "name": "default", "type": "DEFAULT"}],
                },
            },
        },
    )

    # WHEN calling `vellum push`
    runner = CliRunner(mix_stderr=True)
    result = runner.invoke(cli_main, ["push", module, "--dry-run"])

    # THEN it should succeed
    assert result.exit_code == 0

    # AND we should have called the push API with the dry-run option
    vellum_client.workflows.push.assert_called_once()
    call_args = vellum_client.workflows.push.call_args.kwargs
    assert call_args["dry_run"] is True

    # AND the report should be in the output
    assert "## Errors" in result.output
    assert "Serialization is not supported." in result.output
    assert "## Proposed Diffs" in result.output
    assert "iterable_item_added" in result.output


def test_push__strict_option_returns_diffs(mock_module, vellum_client):
    # GIVEN a single workflow configured
    temp_dir = mock_module.temp_dir
    module = mock_module.module

    # AND a workflow exists in the module successfully
    _ensure_workflow_py(temp_dir, module)

    # AND the push API call returns a 4xx response with diffs
    vellum_client.workflows.push.side_effect = ApiError(
        status_code=400,
        body={
            "detail": "Failed to push workflow due to unexpected detected differences in the generated artifact.",
            "diffs": {
                "generated_only": ["state.py"],
                "modified": {
                    "workflow.py": [
                        "--- a/workflow.py\n",
                        "+++ b/workflow.py\n",
                        "@@ -1 +1 @@\n",
                        "-print('hello')",
                        "+print('foo')",
                    ]
                },
                "original_only": ["inputs.py"],
            },
        },
    )

    # WHEN calling `vellum push` on strict mode
    runner = CliRunner()
    result = runner.invoke(cli_main, ["push", module, "--strict"])

    # THEN it should succeed
    assert result.exit_code == 0

    # AND we should have called the push API with the strict option
    vellum_client.workflows.push.assert_called_once()
    call_args = vellum_client.workflows.push.call_args.kwargs
    assert call_args["strict"] is True

    # AND the report should be in the output
    assert (
        result.output
        == """\
\x1b[38;20mLoading workflow from examples.mock.test_push__strict_option_returns_diffs\x1b[0m
\x1b[31;20mFailed to push workflow due to unexpected detected differences in the generated artifact.

Files that were generated but not found in the original project:
- state.py

Files that were found in the original project but not generated:
- inputs.py

Files that were different between the original project and the generated artifact:

--- a/workflow.py
+++ b/workflow.py
@@ -1 +1 @@
-print('hello')
+print('foo')
\x1b[0m
"""
    )


def test_push__workspace_option__uses_different_api_key(mock_module, vellum_client_class):
    # GIVEN a single workflow configured
    temp_dir = mock_module.temp_dir
    module = mock_module.module
    workflow_sandbox_id = mock_module.workflow_sandbox_id
    set_pyproject_toml = mock_module.set_pyproject_toml

    # AND a different workspace is set in the pyproject.toml
    set_pyproject_toml(
        {
            "workflows": [
                {
                    "module": module,
                    "workflow_sandbox_id": workflow_sandbox_id,
                }
            ],
            "workspaces": [
                {
                    "name": "my_other_workspace",
                    "api_key": "MY_OTHER_VELLUM_API_KEY",
                }
            ],
        }
    )

    # AND the .env file has the other api key stored
    with open(os.path.join(temp_dir, ".env"), "w") as f:
        f.write(
            """\
VELLUM_API_KEY=abcdef123456
MY_OTHER_VELLUM_API_KEY=aaabbbcccddd
"""
        )

    # AND a workflow exists in the module successfully
    _ensure_workflow_py(temp_dir, module)

    # AND the push API call returns a new workflow sandbox id
    new_workflow_sandbox_id = str(uuid4())
    vellum_client_class.return_value.workflows.push.return_value = WorkflowPushResponse(
        workflow_sandbox_id=new_workflow_sandbox_id,
    )

    # WHEN calling `vellum push` on strict mode
    runner = CliRunner()
    result = runner.invoke(cli_main, ["push", module, "--workspace", "my_other_workspace"])

    # THEN it should succeed
    assert result.exit_code == 0, result.output

    # AND we should have called the push API once
    vellum_client_class.return_value.workflows.push.assert_called_once()

    # AND the workflow sandbox id arg passed in should be `None`
    call_args = vellum_client_class.return_value.workflows.push.call_args.kwargs
    assert call_args["workflow_sandbox_id"] is None, result.output

    # AND with the correct api key
    vellum_client_class.assert_called_once_with(
        api_key="aaabbbcccddd",
        environment=mock.ANY,
    )

    # AND the vellum lock file should have been updated with the correct workspace
    with open(os.path.join(temp_dir, "vellum.lock.json")) as f:
        lock_file_content = json.load(f)
        assert lock_file_content["workflows"][1] == {
            "module": module,
            "workflow_sandbox_id": new_workflow_sandbox_id,
            "workspace": "my_other_workspace",
            "container_image_name": None,
            "container_image_tag": None,
            "deployments": [],
            "ignore": None,
            "target_directory": None,
        }


def test_push__workspace_option__both_options_already_configured(mock_module, vellum_client_class):
    # GIVEN a single workflow configured
    temp_dir = mock_module.temp_dir
    module = mock_module.module
    workflow_sandbox_id = mock_module.workflow_sandbox_id
    set_pyproject_toml = mock_module.set_pyproject_toml
    second_workflow_sandbox_id = str(uuid4())

    # AND the module is configured twice
    set_pyproject_toml(
        {
            "workflows": [
                {
                    "module": module,
                    "workflow_sandbox_id": workflow_sandbox_id,
                },
                {
                    "module": module,
                    "workflow_sandbox_id": second_workflow_sandbox_id,
                    "workspace": "my_other_workspace",
                },
            ],
            "workspaces": [
                {
                    "name": "my_other_workspace",
                    "api_key": "MY_OTHER_VELLUM_API_KEY",
                }
            ],
        }
    )

    # AND the .env file has the other api key stored
    with open(os.path.join(temp_dir, ".env"), "w") as f:
        f.write(
            """\
VELLUM_API_KEY=abcdef123456
MY_OTHER_VELLUM_API_KEY=aaabbbcccddd
"""
        )

    # AND a workflow exists in the module
    _ensure_workflow_py(temp_dir, module)

    # AND the push API call returns  workflow sandbox id
    vellum_client_class.return_value.workflows.push.return_value = WorkflowPushResponse(
        workflow_sandbox_id=second_workflow_sandbox_id,
    )

    # WHEN calling `vellum push` on strict mode
    runner = CliRunner()
    result = runner.invoke(cli_main, ["push", module, "--workspace", "my_other_workspace"])

    # THEN it should succeed
    assert result.exit_code == 0, result.output

    # AND we should have called the push API once
    vellum_client_class.return_value.workflows.push.assert_called_once()

    # AND the workflow sandbox id arg passed in should be `None`
    call_args = vellum_client_class.return_value.workflows.push.call_args.kwargs
    assert call_args["workflow_sandbox_id"] == second_workflow_sandbox_id

    # AND with the correct api key
    vellum_client_class.assert_called_once_with(
        api_key="aaabbbcccddd",
        environment=mock.ANY,
    )

    # AND the vellum lock file should have the same two workflows
    with open(os.path.join(temp_dir, "vellum.lock.json")) as f:
        lock_file_content = json.load(f)
        assert len(lock_file_content["workflows"]) == 2
        assert lock_file_content["workflows"][0]["module"] == module
        assert lock_file_content["workflows"][0]["workflow_sandbox_id"] == workflow_sandbox_id
        assert lock_file_content["workflows"][0]["workspace"] == "default"
        assert lock_file_content["workflows"][1]["module"] == module
        assert lock_file_content["workflows"][1]["workflow_sandbox_id"] == second_workflow_sandbox_id
        assert lock_file_content["workflows"][1]["workspace"] == "my_other_workspace"


def test_push__create_new_config_for_existing_module(mock_module, vellum_client):
    # GIVEN an empty config (no workflows configured)
    temp_dir = mock_module.temp_dir
    module = mock_module.module
    # GIVEN multiple workflows configured
    mock_module.set_pyproject_toml({"workflows": [{"module": "examples.mock"}, {"module": "examples.mock2"}]})

    # AND a workflow exists in the module successfully
    workflow_py_file_content = _ensure_workflow_py(temp_dir, module)

    # AND the push API call returns successfully
    new_workflow_sandbox_id = str(uuid4())
    vellum_client.workflows.push.return_value = WorkflowPushResponse(
        workflow_sandbox_id=new_workflow_sandbox_id,
    )

    # WHEN calling `vellum push` with a module that exists but isn't in config
    runner = CliRunner()
    result = runner.invoke(cli_main, ["workflows", "push", module])

    # THEN it should succeed
    assert result.exit_code == 0, result.output

    # AND we should have called the push API with the correct args
    vellum_client.workflows.push.assert_called_once()
    call_args = vellum_client.workflows.push.call_args.kwargs
    assert json.loads(call_args["exec_config"])["workflow_raw_data"]["definition"]["name"] == "ExampleWorkflow"
    assert call_args["workflow_sandbox_id"] is None  # Should be None since it's a new config
    assert call_args["artifact"].name == f"{module.replace('.', '__')}.tar.gz"

    # AND the files in the artifact should be correct
    extracted_files = _extract_tar_gz(call_args["artifact"].read())
    assert extracted_files["workflow.py"] == workflow_py_file_content

    # AND check that lockfile was updated with new config
    with open(os.path.join(temp_dir, "vellum.lock.json")) as f:
        lock_file_content = json.load(f)
        new_configs = [w for w in lock_file_content["workflows"] if w["module"] == module]
        assert len(new_configs) == 1  # Should only create one config
        new_config = new_configs[0]
        assert new_config["workflow_sandbox_id"] == new_workflow_sandbox_id
        assert new_config["workspace"] == "default"
