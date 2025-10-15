import pytest
import io
import json
import os
import tarfile
from unittest import mock
from uuid import uuid4

from click.testing import CliRunner
from httpx import Response

from vellum.client.core.api_error import ApiError
from vellum.client.types.workflow_push_response import WorkflowPushResponse
from vellum.utils.uuid import is_valid_uuid
from vellum_cli import main as cli_main
from vellum_ee.workflows.display.nodes.utils import to_kebab_case


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


def _ensure_file(temp_dir: str, module: str, file_name: str, content: str) -> str:
    file_path = os.path.join(temp_dir, *module.split("."), file_name)
    base_dir = os.path.dirname(file_path)
    os.makedirs(base_dir, exist_ok=True)

    with open(file_path, "w") as f:
        f.write(content)

    return content


def _ensure_workflow_py(temp_dir: str, module: str) -> str:
    workflow_py_file_content = """\
from vellum.workflows import BaseWorkflow

class ExampleWorkflow(BaseWorkflow):
    pass
"""
    return _ensure_file(temp_dir, module, "workflow.py", workflow_py_file_content)


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
    assert str(result.exception) == (
        "Multiple workflows found. Please specify a single workflow to push. Found: examples.mock, examples.mock2"
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


@pytest.mark.usefixtures("info_log_level")
def test_push__verify_default_url_in_raw_httpx_transport(mock_module, mock_httpx_transport):
    # GIVEN a single workflow configured
    module = mock_module.module
    temp_dir = mock_module.temp_dir
    _ensure_workflow_py(temp_dir, module)

    # AND the push API call returns successfully
    mock_httpx_transport.handle_request.return_value = Response(
        status_code=200,
        text=json.dumps(
            {
                "workflow_sandbox_id": str(uuid4()),
            }
        ),
    )

    # WHEN calling `vellum push`
    runner = CliRunner()
    result = runner.invoke(cli_main, ["workflows", "push", module])

    # THEN it should succeed
    assert result.exit_code == 0

    # AND we should have called the push API with the correct args
    mock_httpx_transport.handle_request.assert_called_once()
    request = mock_httpx_transport.handle_request.call_args[0][0]
    assert str(request.url) == "https://api.vellum.ai/v1/workflows/push"

    # AND the new URL is in the message at the end
    assert "Visit at: https://app.vellum.ai/workflow-sandboxes/" in result.output


def test_push__no_config__module_found(mock_module, vellum_client):
    # GIVEN no config file set
    temp_dir = mock_module.temp_dir
    module = mock_module.module
    mock_module.set_pyproject_toml({"workflows": []})

    # AND a workflow exists in the module successfully
    workflow_py_file_content = _ensure_workflow_py(temp_dir, module)

    # AND the push API call returns successfully
    new_workflow_sandbox_id = str(uuid4())
    vellum_client.workflows.push.return_value = WorkflowPushResponse(
        workflow_sandbox_id=new_workflow_sandbox_id,
    )

    # WHEN calling `vellum push`
    runner = CliRunner()
    result = runner.invoke(cli_main, ["push", module])

    # THEN it should successfully push the workflow
    assert result.exit_code == 0, result.stdout

    # Get the last part of the module path and format it
    expected_artifact_name = f"{mock_module.module.replace('.', '__')}.tar.gz"

    # AND we should have called the push API with the correct args
    vellum_client.workflows.push.assert_called_once()
    call_args = vellum_client.workflows.push.call_args.kwargs
    assert json.loads(call_args["exec_config"])["workflow_raw_data"]["definition"]["name"] == "ExampleWorkflow"
    assert call_args["workflow_sandbox_id"] is None
    assert "deplyment_config" not in call_args

    # AND we should have pushed the correct artifact
    assert call_args["artifact"].name == expected_artifact_name
    extracted_files = _extract_tar_gz(call_args["artifact"].read())
    assert extracted_files["workflow.py"] == workflow_py_file_content

    # AND there should be a new entry in the lock file
    with open(os.path.join(temp_dir, "vellum.lock.json")) as f:
        lock_file_content = json.load(f)
        assert lock_file_content["workflows"][0] == {
            "container_image_name": None,
            "container_image_tag": None,
            "deployments": [],
            "ignore": None,
            "module": module,
            "target_directory": None,
            "workflow_sandbox_id": new_workflow_sandbox_id,
            "workspace": "default",
        }


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
    assert str(result.exception) == (
        f"Multiple workflows found. Please specify a single workflow to push. Found: {module}, {second_module}"
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
    expected_deployment_name = to_kebab_case(module.split(".")[-1])
    deployment_config = json.loads(call_args["deployment_config"])
    assert deployment_config["name"] == expected_deployment_name

    extracted_files = _extract_tar_gz(call_args["artifact"].read())
    assert extracted_files["workflow.py"] == workflow_py_file_content


@pytest.mark.usefixtures("info_log_level")
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

    # THEN it should fail with exit code 1 due to errors
    assert result.exit_code == 1

    # AND we should have called the push API with the dry-run option
    vellum_client.workflows.push.assert_called_once()
    call_args = vellum_client.workflows.push.call_args.kwargs
    assert call_args["dry_run"] is True

    # AND the report should be in the output
    assert "## Errors" in result.output
    assert "Serialization is not supported." in result.output
    assert "## Proposed Diffs" in result.output
    assert "iterable_item_added" in result.output


@pytest.mark.usefixtures("info_log_level")
def test_push__dry_run_option_no_errors_returns_success(mock_module, vellum_client):
    """Test that dry-run returns exit code 0 when there are no errors or diffs"""
    # GIVEN a workflow module with a valid workflow (using the same pattern as happy path test)
    temp_dir = mock_module.temp_dir
    module = mock_module.module
    _ensure_workflow_py(temp_dir, module)

    # AND the push API call returns successfully with no errors and no diffs
    vellum_client.workflows.push.return_value = WorkflowPushResponse(
        workflow_sandbox_id=str(uuid4()),
        proposed_diffs=None,
    )

    # WHEN calling `vellum push` with dry-run
    runner = CliRunner(mix_stderr=True)
    result = runner.invoke(cli_main, ["push", module, "--dry-run"])

    # THEN it should succeed with exit code 0
    assert result.exit_code == 0

    # AND we should have called the push API with the dry-run option
    vellum_client.workflows.push.assert_called_once()
    call_args = vellum_client.workflows.push.call_args.kwargs
    assert call_args["dry_run"] is True

    # AND the report should be in the output
    assert "## Errors" in result.output
    assert "No errors found." in result.output
    assert "## Proposed Diffs" in result.output


@pytest.mark.usefixtures("info_log_level")
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


def test_push__push_fails_due_to_400_error(mock_module, vellum_client):
    # GIVEN a single workflow configured
    temp_dir = mock_module.temp_dir
    module = mock_module.module

    # AND a workflow exists in the module successfully
    _ensure_workflow_py(temp_dir, module)

    # AND the push API call returns a 4xx response
    vellum_client.workflows.push.side_effect = ApiError(
        status_code=400,
        body={
            "detail": "Pushing the Workflow failed because you did something wrong",
        },
    )

    # WHEN calling `vellum push` on strict mode
    runner = CliRunner()
    result = runner.invoke(cli_main, ["push", module])

    # THEN it should fail with a user error code
    assert result.exit_code == 1

    # AND the error message should be in the error message
    assert "API request to /workflows/push failed." in result.output
    assert "Pushing the Workflow failed because you did something wrong" in result.output

    # AND the stack trace should not be
    assert "Traceback" not in result.output


def test_push__push_fails_due_to_404_error_with_id(mock_module, vellum_client):
    """
    Tests that a 404 error with a workflow sandbox ID shows a helpful error message.
    """

    # GIVEN a single workflow configured with a workflow_sandbox_id
    temp_dir = mock_module.temp_dir
    module = mock_module.module

    # AND a workflow exists in the module successfully
    _ensure_workflow_py(temp_dir, module)

    # AND the push API call returns a 404 response
    vellum_client.workflows.push.side_effect = ApiError(
        status_code=404,
        body={},
    )

    # WHEN calling `vellum push`
    runner = CliRunner()
    result = runner.invoke(cli_main, ["push", module])

    # THEN it should fail with a user error code
    assert result.exit_code == 1

    # AND the error message should be in the error message
    assert "Workflow Sandbox not found" in result.output
    assert mock_module.workflow_sandbox_id in result.output
    assert "workspace" in result.output

    # AND the stack trace should not be present
    assert "Traceback" not in result.output


def test_push__push_fails_due_to_404_error_without_id(tmp_path, vellum_client, monkeypatch):
    """
    Tests that a 404 error without a workflow sandbox ID shows a helpful error message.
    """

    # GIVEN a workflow module exists but has no workflow_sandbox_id configured
    module = "examples.mock.test_push__404_without_id"
    module_dir = tmp_path / "examples" / "mock" / "test_push__404_without_id"
    module_dir.mkdir(parents=True)

    # AND a workflow.py file exists
    workflow_file = module_dir / "workflow.py"
    workflow_file.write_text(
        "from vellum.workflows import BaseWorkflow\n\nclass ExampleWorkflow(BaseWorkflow):\n    pass\n"
    )

    # AND the pyproject.toml file exists without workflow_sandbox_id
    pyproject_file = tmp_path / "pyproject.toml"
    pyproject_file.write_text(f'[tool.vellum]\n[[tool.vellum.workflows]]\nmodule = "{module}"\n')

    monkeypatch.chdir(tmp_path)

    # AND the push API call returns a 404 response
    vellum_client.workflows.push.side_effect = ApiError(
        status_code=404,
        body={},
    )

    # WHEN calling `vellum push`
    runner = CliRunner()
    result = runner.invoke(cli_main, ["push", module])

    # THEN it should fail with a user error code
    assert result.exit_code == 1

    # AND the error message should be in the output
    assert "Workflow Sandbox not found" in result.output
    assert "/workflows/push" in result.output
    assert "404 response" in result.output

    # AND the stack trace should not be present
    assert "Traceback" not in result.output


@pytest.mark.parametrize(
    "file_data",
    [
        {
            "workflow.py": """\
from vellum.workflows import BaseWorkflow

class ExampleWorkflow(BaseWorkflow):
    pass
"""
        },
        {
            "nodes/start_node.py": """\
from vellum.workflows.nodes import CodeExecutionNode
from vellum.workflows.references import VellumSecretReference

class StartNode(CodeExecutionNode):
    code_inputs = {
        "foo": VellumSecretReference("MY_SECRET_KEY"),
    }
""",
            "workflow.py": """\
from vellum.workflows import BaseWorkflow
from .nodes.start_node import StartNode

class ExampleWorkflow(BaseWorkflow):
    graph = StartNode
""",
        },
        {
            "nodes/start_node.py": """\
from vellum.workflows.nodes import PromptDeploymentNode

class StartNode(PromptDeploymentNode):
    deployment = "my-deployment"
""",
            "workflow.py": """\
from vellum.workflows import BaseWorkflow
from .nodes.start_node import StartNode

class ExampleWorkflow(BaseWorkflow):
    graph = StartNode
""",
        },
        {
            "nodes/start_node.py": """\
from vellum.workflows.nodes import SubworkflowDeploymentNode

class StartNode(SubworkflowDeploymentNode):
    deployment = "my-deployment"
""",
            "workflow.py": """\
from vellum.workflows import BaseWorkflow
from .nodes.start_node import StartNode

class ExampleWorkflow(BaseWorkflow):
    graph = StartNode
""",
        },
    ],
    ids=[
        "base_case",
        "with_secret_reference",
        "with_prompt_deployment",
        "with_subworkflow_deployment",
    ],
)
def test_push__workspace_option__uses_different_api_key(mock_module, vellum_client_class, file_data):
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
    for file_name, content in file_data.items():
        _ensure_file(temp_dir, module, file_name, content)

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
        api_version=None,
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


@pytest.mark.usefixtures("info_log_level")
def test_push__workspace_option__uses_different_api_url_env(mock_module, mock_httpx_transport):
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
                    "api_url": "MY_OTHER_VELLUM_API_URL",
                }
            ],
        }
    )

    # AND the .env file has the other api key stored
    with open(os.path.join(temp_dir, ".env"), "w") as f:
        f.write(
            """\
VELLUM_API_KEY=abcdef123456
MY_OTHER_VELLUM_API_URL=https://app.aws-vpc-staging.vellum.ai
"""
        )

    # AND a workflow exists in the module successfully
    _ensure_workflow_py(temp_dir, module)

    # AND the push API call returns a new workflow sandbox id
    new_workflow_sandbox_id = str(uuid4())
    mock_httpx_transport.handle_request.return_value = Response(
        status_code=200,
        text=json.dumps(
            {
                "workflow_sandbox_id": new_workflow_sandbox_id,
            }
        ),
    )

    # WHEN calling `vellum push` on strict mode
    runner = CliRunner()
    result = runner.invoke(cli_main, ["push", module, "--workspace", "my_other_workspace"])

    # THEN it should succeed
    assert result.exit_code == 0, result.output

    # AND we should have called the push API once with the correct api url
    request = mock_httpx_transport.handle_request.call_args[0][0]
    assert str(request.url) == "https://app.aws-vpc-staging.vellum.ai/v1/workflows/push"

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

    # AND the new URL is in the message at the end
    assert "Visit at: https://app.aws-vpc-staging.vellum.ai/workflow-sandboxes/" in result.output


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
        api_version=None,
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


def test_push__use_default_workspace_if_not_specified__multiple_workflows_configured(mock_module, vellum_client):
    # GIVEN a config with a workspace configured
    temp_dir = mock_module.temp_dir
    module = mock_module.module
    workflow_sandbox_id = str(uuid4())
    mock_module.set_pyproject_toml(
        {
            "workspaces": [
                {"name": "my_other_workspace"},
            ],
            "workflows": [
                {"module": module, "workflow_sandbox_id": workflow_sandbox_id, "workspace": "default"},
                {"module": module, "workflow_sandbox_id": str(uuid4()), "workspace": "my_other_workspace"},
            ],
        }
    )

    # AND a workflow exists in the module successfully
    _ensure_workflow_py(temp_dir, module)

    # AND the push API call returns successfully
    vellum_client.workflows.push.return_value = WorkflowPushResponse(
        workflow_sandbox_id=workflow_sandbox_id,
    )

    # WHEN calling `vellum push` with a module without a workspace specified
    runner = CliRunner()
    result = runner.invoke(cli_main, ["workflows", "push", module])

    # THEN it should succeed
    assert result.exit_code == 0, result.output

    # AND check that lockfile should maintain that this workflow is using the default workspace
    with open(os.path.join(temp_dir, "vellum.lock.json")) as f:
        lock_file_content = json.load(f)
        configs = [w for w in lock_file_content["workflows"] if w["module"] == module]
        assert len(configs) == 2
        config = configs[0]
        assert config["workflow_sandbox_id"] == workflow_sandbox_id
        assert config["workspace"] == "default"


def test_push__deploy_with_malformed_release_tags_shows_friendly_validation_error(mock_module, vellum_client):
    # GIVEN a single workflow configured
    temp_dir = mock_module.temp_dir
    module = mock_module.module

    # AND a workflow exists in the module successfully
    _ensure_workflow_py(temp_dir, module)

    # AND the push API call would return successfully
    vellum_client.workflows.push.return_value = WorkflowPushResponse(
        workflow_sandbox_id=str(uuid4()),
    )

    # WHEN calling `vellum workflows push` with --deploy and --release-tag
    runner = CliRunner()
    result = runner.invoke(cli_main, ["workflows", "push", module, "--deploy", "--release-tag", None])  # type: ignore

    # THEN it should show the friendly error message instead of a raw Pydantic traceback
    assert "Invalid release tag format" in result.output
    assert "Release tags must be provided as separate arguments" in result.output
    assert "--release-tag tag1 --release-tag tag2" in result.output


@pytest.mark.usefixtures("info_log_level")
def test_push__deploy_with_release_tags_success(mock_module, vellum_client):
    # GIVEN a single workflow configured
    temp_dir = mock_module.temp_dir
    module = mock_module.module

    # AND a workflow exists in the module successfully
    _ensure_workflow_py(temp_dir, module)

    # AND the push API call returns successfully
    workflow_deployment_id = str(uuid4())
    vellum_client.workflows.push.return_value = WorkflowPushResponse(
        workflow_sandbox_id=str(uuid4()),
        workflow_deployment_id=workflow_deployment_id,
    )

    # WHEN calling `vellum workflows push` with --deploy and --release-tag
    runner = CliRunner()
    result = runner.invoke(cli_main, ["workflows", "push", module, "--deploy", "--release-tag", "v1.0.0"])

    # THEN it should succeed
    assert result.exit_code == 0, result.output

    # AND we should have called the push API with the correct deployment config
    vellum_client.workflows.push.assert_called_once()
    call_args = vellum_client.workflows.push.call_args.kwargs

    # AND the deployment_config should contain the release tags
    deployment_config_str = call_args["deployment_config"]
    deployment_config = json.loads(deployment_config_str)
    assert deployment_config["release_tags"] == ["v1.0.0"]

    # AND should show success message
    assert "Successfully pushed" in result.output
    assert "Updated vellum.lock.json file." in result.output


@pytest.mark.usefixtures("info_log_level")
def test_push__deploy_with_release_description_success(mock_module, vellum_client):
    # GIVEN a single workflow configured
    temp_dir = mock_module.temp_dir
    module = mock_module.module

    # AND a workflow exists in the module successfully
    _ensure_workflow_py(temp_dir, module)

    # AND the push API call returns successfully
    workflow_deployment_id = str(uuid4())
    vellum_client.workflows.push.return_value = WorkflowPushResponse(
        workflow_sandbox_id=str(uuid4()),
        workflow_deployment_id=workflow_deployment_id,
    )

    # WHEN calling `vellum workflows push` with --deploy and --release-description
    runner = CliRunner()
    result = runner.invoke(
        cli_main, ["workflows", "push", module, "--deploy", "--release-description", "This is a test release"]
    )

    # THEN it should succeed
    assert result.exit_code == 0, result.output

    # AND we should have called the push API with the correct deployment config
    vellum_client.workflows.push.assert_called_once()
    call_args = vellum_client.workflows.push.call_args.kwargs

    # AND the deployment_config should contain the release description
    deployment_config_str = call_args["deployment_config"]
    deployment_config = json.loads(deployment_config_str)
    assert deployment_config["release_description"] == "This is a test release"

    # AND should show success message
    assert "Successfully pushed" in result.output
    assert "Updated vellum.lock.json file." in result.output


def test_push__deploy_stores_deployment_config_in_lock_file(mock_module, vellum_client):
    # GIVEN a single workflow
    temp_dir = mock_module.temp_dir
    module = mock_module.module

    # AND a workflow exists in the module successfully
    _ensure_workflow_py(temp_dir, module)

    # AND the push API call returns successfully with a deployment
    workflow_deployment_id = str(uuid4())
    vellum_client.workflows.push.return_value = WorkflowPushResponse(
        workflow_sandbox_id=str(uuid4()),
        workflow_deployment_id=workflow_deployment_id,
    )

    # WHEN calling `vellum workflows push --deploy` for the first time
    runner = CliRunner()
    result = runner.invoke(cli_main, ["workflows", "push", module, "--deploy"])

    # THEN it should succeed
    assert result.exit_code == 0, result.output

    # AND the deployment config should be stored in the lock file with the deployment ID and module name
    with open(os.path.join(temp_dir, "vellum.lock.json")) as f:
        lock_data = json.loads(f.read())
        assert len(lock_data["workflows"][0]["deployments"]) == 1
        deployment = lock_data["workflows"][0]["deployments"][0]
        assert str(deployment["id"]) == workflow_deployment_id
        assert deployment["name"] == "test-push-deploy-stores-deployment-config-in-lock-file"
        assert deployment.get("label") is None
        assert deployment.get("description") is None
        assert deployment.get("release_tags") is None

    # AND when we do a second push
    vellum_client.workflows.push.reset_mock()
    vellum_client.workflows.push.return_value = WorkflowPushResponse(
        workflow_sandbox_id=str(uuid4()),
        workflow_deployment_id=workflow_deployment_id,
    )

    result = runner.invoke(cli_main, ["workflows", "push", module, "--deploy"])

    # THEN it should succeed
    assert result.exit_code == 0, result.output

    # AND we should have called the push API with the module name as deployment name
    vellum_client.workflows.push.assert_called_once()
    call_args = vellum_client.workflows.push.call_args.kwargs
    deployment_config_str = call_args["deployment_config"]
    deployment_config = json.loads(deployment_config_str)
    assert deployment_config["name"] == "test-push-deploy-stores-deployment-config-in-lock-file"


def test_push__custom_workspace_in_lockfile__uses_custom_workspace_without_flag(mock_module, vellum_client_class):
    """
    Tests that push respects the custom workspace from the lockfile when no --workspace flag is provided.
    """

    # GIVEN a workflow already configured in the lockfile with a custom workspace
    temp_dir = mock_module.temp_dir
    module = mock_module.module
    workflow_sandbox_id = mock_module.workflow_sandbox_id
    set_pyproject_toml = mock_module.set_pyproject_toml

    # AND the lockfile has the workflow with a custom workspace
    with open(os.path.join(temp_dir, "vellum.lock.json"), "w") as f:
        json.dump(
            {
                "version": "1.0",
                "workflows": [
                    {
                        "module": module,
                        "workflow_sandbox_id": workflow_sandbox_id,
                        "workspace": "my_custom_workspace",
                        "container_image_name": None,
                        "container_image_tag": None,
                        "deployments": [],
                        "ignore": None,
                        "target_directory": None,
                    }
                ],
                "workspaces": [],
            },
            f,
            indent=2,
        )

    # AND the custom workspace is defined in pyproject.toml
    set_pyproject_toml(
        {
            "workflows": [],
            "workspaces": [
                {
                    "name": "my_custom_workspace",
                    "api_key": "MY_CUSTOM_VELLUM_API_KEY",
                }
            ],
        }
    )

    # AND the .env file has the custom api key
    with open(os.path.join(temp_dir, ".env"), "w") as f:
        f.write(
            """\
VELLUM_API_KEY=abcdef123456
MY_CUSTOM_VELLUM_API_KEY=custom-key-xyz
"""
        )

    # AND a workflow exists in the module
    _ensure_workflow_py(temp_dir, module)

    # AND the push API returns successfully
    vellum_client_class.return_value.workflows.push.return_value = WorkflowPushResponse(
        workflow_sandbox_id=workflow_sandbox_id,
    )
    vellum_client_class.return_value._client_wrapper._environment.default = "https://api.vellum.ai/v1"

    # WHEN calling `vellum push` WITHOUT the --workspace flag
    runner = CliRunner()
    result = runner.invoke(cli_main, ["push", module])

    # THEN it should succeed
    assert result.exit_code == 0, result.output

    # AND the custom workspace API key should have been used
    vellum_client_class.assert_called_once_with(
        api_key="custom-key-xyz",
        environment=mock.ANY,
        api_version=None,
    )

    with open(os.path.join(temp_dir, "vellum.lock.json")) as f:
        lock_file_content = json.load(f)
        assert len(lock_file_content["workflows"]) == 1
        assert lock_file_content["workflows"][0]["workspace"] == "my_custom_workspace"
        assert lock_file_content["workflows"][0]["workflow_sandbox_id"] == workflow_sandbox_id


def test_push__workspace_option__nonexistent_workspace_should_fail(mock_module):
    """
    Tests that pushing with a nonexistent workspace that isn't default should fail.
    """

    # GIVEN a single workflow configured
    temp_dir = mock_module.temp_dir
    module = mock_module.module
    set_pyproject_toml = mock_module.set_pyproject_toml

    # AND a custom workspace is configured
    set_pyproject_toml(
        {
            "workflows": [
                {
                    "module": module,
                }
            ],
            "workspaces": [
                {
                    "name": "my_custom_workspace",
                    "api_key": "MY_CUSTOM_VELLUM_API_KEY",
                }
            ],
        }
    )

    # AND a workflow exists in the module successfully
    _ensure_workflow_py(temp_dir, module)

    # WHEN calling `vellum push` with a nonexistent workspace
    runner = CliRunner()
    result = runner.invoke(cli_main, ["push", module, "--workspace", "nonexistent_workspace"])

    # THEN it should exit with an error
    assert result.exit_code == 1

    # AND the error message should indicate the workspace doesn't exist
    assert "Workspace 'nonexistent_workspace' not found in config" in result.output
    assert "Available workspaces:" in result.output
    assert "default" in result.output
    assert "my_custom_workspace" in result.output
