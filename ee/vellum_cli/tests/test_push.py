import pytest
import io
import json
import os
import tarfile
from uuid import uuid4

from click.testing import CliRunner

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
    base_dir = os.path.join(temp_dir, *module.split("."))
    os.makedirs(base_dir, exist_ok=True)
    workflow_py_file_content = """\
from vellum.workflows import BaseWorkflow

class ExampleWorkflow(BaseWorkflow):
    pass
"""
    with open(os.path.join(temp_dir, *module.split("."), "workflow.py"), "w") as f:
        f.write(workflow_py_file_content)

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
    expected_label = mock_module.module.split(".")[-1].replace("_", " ").title()
    expected_artifact_name = f"{mock_module.module.replace('.', '__')}.tar.gz"

    # AND we should have called the push API with the correct args
    vellum_client.workflows.push.assert_called_once()
    call_args = vellum_client.workflows.push.call_args.kwargs
    assert json.loads(call_args["exec_config"])["workflow_raw_data"]["definition"]["name"] == "ExampleWorkflow"
    assert call_args["label"] == expected_label
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
def test_push__deployment(mock_module, vellum_client, base_command):
    # GIVEN a single workflow configured
    temp_dir = mock_module.temp_dir
    module = mock_module.module

    # AND a workflow exists in the module successfully
    base_dir = os.path.join(temp_dir, *module.split("."))
    os.makedirs(base_dir, exist_ok=True)
    workflow_py_file_content = """\
from vellum.workflows import BaseWorkflow

class ExampleWorkflow(BaseWorkflow):
    pass
"""
    with open(os.path.join(temp_dir, *module.split("."), "workflow.py"), "w") as f:
        f.write(workflow_py_file_content)

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
    expected_label = mock_module.module.split(".")[-1].replace("_", " ").title()
    expected_artifact_name = f"{mock_module.module.replace('.', '__')}.tar.gz"

    # AND we should have called the push API with the correct args
    vellum_client.workflows.push.assert_called_once()
    call_args = vellum_client.workflows.push.call_args.kwargs
    assert json.loads(call_args["exec_config"])["workflow_raw_data"]["definition"]["name"] == "ExampleWorkflow"
    assert call_args["label"] == expected_label
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
from vellum_ee.workflows.display.nodes import BaseNodeDisplay

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
