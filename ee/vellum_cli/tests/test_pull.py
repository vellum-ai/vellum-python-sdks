import pytest
import io
import json
import os
import tempfile
from uuid import uuid4
import zipfile

from click.testing import CliRunner

from vellum_cli import main as cli_main


def _zip_file_map(file_map: dict[str, str]) -> bytes:
    # Create an in-memory bytes buffer to store the zip
    zip_buffer = io.BytesIO()

    # Create zip file and add files from file_map
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for filename, content in file_map.items():
            zip_file.writestr(filename, content)

    # Get the bytes from the buffer
    zip_bytes = zip_buffer.getvalue()
    zip_buffer.close()

    return zip_bytes


@pytest.mark.parametrize(
    "base_command",
    [
        ["pull"],
        ["workflows", "pull"],
    ],
    ids=["pull", "workflows_pull"],
)
def test_pull(vellum_client, mock_module, base_command):
    # GIVEN a module on the user's filesystem
    temp_dir = mock_module.temp_dir
    module = mock_module.module

    # AND the workflow pull API call returns a zip file
    vellum_client.workflows.pull.return_value = iter([_zip_file_map({"workflow.py": "print('hello')"})])

    # WHEN the user runs the pull command
    runner = CliRunner()
    result = runner.invoke(cli_main, base_command + [module])

    # THEN the command returns successfully
    assert result.exit_code == 0

    # AND the workflow.py file is written to the module directory
    workflow_py = os.path.join(temp_dir, *module.split("."), "workflow.py")
    assert os.path.exists(workflow_py)
    with open(workflow_py) as f:
        assert f.read() == "print('hello')"


def test_pull__second_module(vellum_client, mock_module):
    # GIVEN a module on the user's filesystem
    temp_dir = mock_module.temp_dir
    module = mock_module.module
    set_pyproject_toml = mock_module.set_pyproject_toml

    # AND the workflow pull API call returns a zip file
    vellum_client.workflows.pull.return_value = iter([_zip_file_map({"workflow.py": "print('hello')"})])

    # AND the module we're about to pull is configured second
    set_pyproject_toml(
        {
            "workflows": [
                {"module": "another.module", "workflow_sandbox_id": str(uuid4())},
                {"module": module, "workflow_sandbox_id": str(uuid4())},
            ]
        }
    )

    # WHEN the user runs the pull command
    runner = CliRunner()
    result = runner.invoke(cli_main, ["pull", module])

    # THEN the command returns successfully
    assert result.exit_code == 0

    # AND the workflow.py file is written to the module directory
    workflow_py = os.path.join(temp_dir, *module.split("."), "workflow.py")
    assert os.path.exists(workflow_py)
    with open(workflow_py) as f:
        assert f.read() == "print('hello')"


def test_pull__sandbox_id_with_no_config(vellum_client):
    # GIVEN a workflow sandbox id
    workflow_sandbox_id = "87654321-0000-0000-0000-000000000000"

    # AND the workflow pull API call returns a zip file
    vellum_client.workflows.pull.return_value = iter([_zip_file_map({"workflow.py": "print('hello')"})])

    # AND we are currently in a new directory
    current_dir = os.getcwd()
    temp_dir = tempfile.mkdtemp()
    os.chdir(temp_dir)

    # WHEN the user runs the pull command with the workflow sandbox id and no module
    runner = CliRunner()
    result = runner.invoke(cli_main, ["workflows", "pull", "--workflow-sandbox-id", workflow_sandbox_id])
    os.chdir(current_dir)

    # THEN the command returns successfully
    assert result.exit_code == 0

    # AND the pull api is called with the workflow sandbox id
    vellum_client.workflows.pull.assert_called_once()
    workflow_py = os.path.join(temp_dir, "workflow_87654321", "workflow.py")
    assert os.path.exists(workflow_py)
    with open(workflow_py) as f:
        assert f.read() == "print('hello')"

    # AND the vellum.lock.json file is created
    vellum_lock_json = os.path.join(temp_dir, "vellum.lock.json")
    assert os.path.exists(vellum_lock_json)
    with open(vellum_lock_json) as f:
        lock_data = json.loads(f.read())
        assert lock_data == {
            "version": "1.0",
            "workflows": [
                {
                    "module": "workflow_87654321",
                    "workflow_sandbox_id": "87654321-0000-0000-0000-000000000000",
                    "ignore": None,
                    "deployments": [],
                }
            ],
        }


def test_pull__sandbox_id_with_other_workflow_configured(vellum_client, mock_module):
    # GIVEN a pyproject.toml with a workflow configured
    temp_dir = mock_module.temp_dir

    # AND a different workflow sandbox id
    workflow_sandbox_id = "87654321-0000-0000-0000-000000000000"

    # AND the workflow pull API call returns a zip file
    vellum_client.workflows.pull.return_value = iter([_zip_file_map({"workflow.py": "print('hello')"})])

    # WHEN the user runs the pull command with the new workflow sandbox id
    runner = CliRunner()
    result = runner.invoke(cli_main, ["workflows", "pull", "--workflow-sandbox-id", workflow_sandbox_id])

    # THEN the command returns successfully
    assert result.exit_code == 0

    # AND the pull api is called with the new workflow sandbox id
    vellum_client.workflows.pull.assert_called_once()
    call_args = vellum_client.workflows.pull.call_args.args
    assert call_args[0] == workflow_sandbox_id

    # AND the workflow.py file is written to the module directory
    workflow_py = os.path.join(temp_dir, "workflow_87654321", "workflow.py")
    assert os.path.exists(workflow_py)
    with open(workflow_py) as f:
        assert f.read() == "print('hello')"


def test_pull__workflow_deployment_with_no_config(vellum_client):
    # GIVEN a workflow deployment
    workflow_deployment = "my-deployment"

    # AND the workflow pull API call returns a zip file
    vellum_client.workflows.pull.return_value = iter([_zip_file_map({"workflow.py": "print('hello')"})])

    # AND we are currently in a new directory
    current_dir = os.getcwd()
    temp_dir = tempfile.mkdtemp()
    os.chdir(temp_dir)

    # WHEN the user runs the pull command with the workflow deployment
    runner = CliRunner()
    result = runner.invoke(cli_main, ["workflows", "pull", "--workflow-deployment", workflow_deployment])
    os.chdir(current_dir)

    # THEN the command returns successfully
    assert result.exit_code == 0

    # AND the pull api is called with the workflow deployment
    vellum_client.workflows.pull.assert_called_once()
    workflow_py = os.path.join(temp_dir, "my_deployment", "workflow.py")
    assert os.path.exists(workflow_py)
    with open(workflow_py) as f:
        assert f.read() == "print('hello')"

    # AND the vellum.lock.json file is created
    vellum_lock_json = os.path.join(temp_dir, "vellum.lock.json")
    assert os.path.exists(vellum_lock_json)
    with open(vellum_lock_json) as f:
        lock_data = json.loads(f.read())
        assert lock_data == {
            "version": "1.0",
            "workflows": [
                {
                    "module": "my_deployment",
                    "workflow_sandbox_id": None,
                    "ignore": None,
                    "deployments": [],
                }
            ],
        }


def test_pull__both_workflow_sandbox_id_and_deployment(vellum_client):
    # GIVEN a workflow sandbox id
    workflow_sandbox_id = "87654321-0000-0000-0000-000000000000"

    # AND a workflow deployment
    workflow_deployment = "my-deployment"

    # AND the workflow pull API call returns a zip file
    vellum_client.workflows.pull.return_value = iter([_zip_file_map({"workflow.py": "print('hello')"})])

    # AND we are currently in a new directory
    current_dir = os.getcwd()
    temp_dir = tempfile.mkdtemp()
    os.chdir(temp_dir)

    # WHEN the user runs the pull command with the workflow deployment
    runner = CliRunner()
    result = runner.invoke(
        cli_main,
        [
            "workflows",
            "pull",
            "--workflow-sandbox-id",
            workflow_sandbox_id,
            "--workflow-deployment",
            workflow_deployment,
        ],
    )
    os.chdir(current_dir)

    # THEN the command returns successfully
    assert result.exit_code == 1
    assert "Cannot specify both workflow_sandbox_id and workflow_deployment" == str(result.exception)


def test_pull__remove_missing_files(vellum_client, mock_module):
    # GIVEN a module on the user's filesystem
    temp_dir = mock_module.temp_dir
    module = mock_module.module

    # AND the workflow pull API call returns a zip file
    vellum_client.workflows.pull.return_value = iter([_zip_file_map({"workflow.py": "print('hello')"})])

    # AND there is already a different file in the module directory
    other_file_path = os.path.join(temp_dir, *module.split("."), "other_file.py")
    os.makedirs(os.path.dirname(other_file_path), exist_ok=True)
    with open(other_file_path, "w") as f:
        f.write("print('hello')")

    # WHEN the user runs the pull command
    runner = CliRunner()
    result = runner.invoke(cli_main, ["pull", module])

    # THEN the command returns successfully
    assert result.exit_code == 0

    # AND the workflow.py file is written to the module directory
    assert os.path.exists(os.path.join(temp_dir, *module.split("."), "workflow.py"))
    with open(os.path.join(temp_dir, *module.split("."), "workflow.py")) as f:
        assert f.read() == "print('hello')"

    # AND the other_file.py file is deleted
    assert not os.path.exists(other_file_path)


def test_pull__remove_missing_files__ignore_pattern(vellum_client, mock_module):
    # GIVEN a module on the user's filesystem
    temp_dir = mock_module.temp_dir
    module = mock_module.module
    set_pyproject_toml = mock_module.set_pyproject_toml

    # AND the workflow pull API call returns a zip file
    vellum_client.workflows.pull.return_value = iter([_zip_file_map({"workflow.py": "print('hello')"})])

    # AND there is already a different file in the module directory
    other_file_path = os.path.join(temp_dir, *module.split("."), "other_file.py")
    os.makedirs(os.path.dirname(other_file_path), exist_ok=True)
    with open(other_file_path, "w") as f:
        f.write("print('hello')")

    # AND there is already a test file
    test_file_path = os.path.join(temp_dir, *module.split("."), "tests", "test_workflow.py")
    os.makedirs(os.path.dirname(test_file_path), exist_ok=True)
    with open(test_file_path, "w") as f:
        f.write("print('hello')")

    # AND the ignore pattern is set to tests
    set_pyproject_toml(
        {
            "workflows": [
                {
                    "module": module,
                    "workflow_sandbox_id": str(uuid4()),
                    "ignore": "tests/*",
                }
            ]
        }
    )

    # WHEN the user runs the pull command
    runner = CliRunner()
    result = runner.invoke(cli_main, ["pull", module])

    # THEN the command returns successfully
    assert result.exit_code == 0

    # AND the workflow.py file is written to the module directory
    assert os.path.exists(os.path.join(temp_dir, *module.split("."), "workflow.py"))
    with open(os.path.join(temp_dir, *module.split("."), "workflow.py")) as f:
        assert f.read() == "print('hello')"

    # AND the other_file.py file is deleted
    assert not os.path.exists(other_file_path)

    # AND the tests/test_workflow.py file is untouched
    assert os.path.exists(test_file_path)


def test_pull__include_json(vellum_client, mock_module):
    # GIVEN a module on the user's filesystem
    module = mock_module.module

    # AND the workflow pull API call returns a zip file
    vellum_client.workflows.pull.return_value = iter(
        [_zip_file_map({"workflow.py": "print('hello')", "workflow.json": "{}"})]
    )

    # WHEN the user runs the pull command
    runner = CliRunner()
    result = runner.invoke(cli_main, ["pull", module, "--include-json"])

    # THEN the command returns successfully
    assert result.exit_code == 0

    # AND the pull api is called with include_json=True
    vellum_client.workflows.pull.assert_called_once()
    call_args = vellum_client.workflows.pull.call_args.kwargs
    assert call_args["request_options"]["additional_query_parameters"] == {"include_json": True}


def test_pull__exclude_code(vellum_client, mock_module):
    # GIVEN a module on the user's filesystem
    module = mock_module.module

    # AND the workflow pull API call returns a zip file
    vellum_client.workflows.pull.return_value = iter(
        [_zip_file_map({"workflow.py": "print('hello')", "workflow.json": "{}"})]
    )

    # WHEN the user runs the pull command
    runner = CliRunner()
    result = runner.invoke(cli_main, ["pull", module, "--exclude-code"])

    # THEN the command returns successfully
    assert result.exit_code == 0

    # AND the pull api is called with exclude_code=True
    vellum_client.workflows.pull.assert_called_once()
    call_args = vellum_client.workflows.pull.call_args.kwargs
    assert call_args["request_options"]["additional_query_parameters"] == {"exclude_code": True}


def test_pull__sandbox_id_with_other_workflow_deployment_in_lock(vellum_client, mock_module):
    # GIVEN a pyproject.toml with a workflow configured
    temp_dir = mock_module.temp_dir
    module = mock_module.module
    workflow_sandbox_id = mock_module.workflow_sandbox_id

    # AND there's a workflow deployment in the lock file
    vellum_lock_json = os.path.join(temp_dir, "vellum.lock.json")
    with open(vellum_lock_json, "w") as f:
        json.dump(
            {
                "version": "1.0",
                "workflows": [
                    {
                        "module": module,
                        "workflow_sandbox_id": "0edc07cd-45b9-43e8-99bc-1f181972a857",
                        "ignore": "tests/*",
                        "deployments": [
                            {
                                "id": "7e5a7610-4c46-4bc9-b06e-0fc6a9e28959",
                                "label": None,
                                "name": None,
                                "description": None,
                                "release_tags": None,
                            }
                        ],
                    }
                ],
            },
            f,
        )

    # AND a different workflow sandbox id
    new_workflow_sandbox_id = "87654321-0000-0000-0000-000000000000"

    # AND the workflow pull API call returns a zip file
    vellum_client.workflows.pull.return_value = iter([_zip_file_map({"workflow.py": "print('hello')"})])

    # WHEN the user runs the pull command with the new workflow sandbox id
    runner = CliRunner()
    result = runner.invoke(cli_main, ["workflows", "pull", "--workflow-sandbox-id", new_workflow_sandbox_id])

    # THEN the command returns successfully
    assert result.exit_code == 0

    # AND the lock file is updated to preserve the deployment and include the new workflow
    with open(vellum_lock_json) as f:
        lock_data = json.load(f)
        assert lock_data["workflows"] == [
            {
                "module": module,
                "workflow_sandbox_id": workflow_sandbox_id,
                "ignore": "tests/*",
                "deployments": [
                    {
                        "id": "7e5a7610-4c46-4bc9-b06e-0fc6a9e28959",
                        "label": None,
                        "name": None,
                        "description": None,
                        "release_tags": None,
                    },
                ],
            },
            {
                "module": "workflow_87654321",
                "workflow_sandbox_id": new_workflow_sandbox_id,
                "ignore": None,
                "deployments": [],
            },
        ]


def test_pull__handle_error_log(vellum_client, mock_module):
    # GIVEN a pyproject.toml with a workflow configured
    temp_dir = mock_module.temp_dir
    module = mock_module.module
    workflow_sandbox_id = mock_module.workflow_sandbox_id

    # AND the workflow pull API call returns a zip file with an error log
    vellum_client.workflows.pull.return_value = iter(
        [_zip_file_map({"workflow.py": "print('hello')", "error.log": "test error"})]
    )

    # WHEN the user runs the pull command with the new workflow sandbox id
    runner = CliRunner()
    result = runner.invoke(cli_main, ["workflows", "pull", "--workflow-sandbox-id", workflow_sandbox_id])

    # THEN the command returns successfully
    assert result.exit_code == 0

    # AND the error log file is not written to the module directory
    assert not os.path.exists(os.path.join(temp_dir, *module.split("."), "error.log"))

    # AND the error log is printed to the console
    assert result.output.endswith("\x1b[31;20mtest error\x1b[0m\n")


def test_pull__strict__with_error(vellum_client, mock_module):
    # GIVEN a pyproject.toml with a workflow configured
    workflow_sandbox_id = mock_module.workflow_sandbox_id

    # AND the workflow pull API call returns a zip file
    vellum_client.workflows.pull.return_value = iter([_zip_file_map({"workflow.py": "print('hello')"})])

    # WHEN the user runs the pull command with the new workflow sandbox id
    runner = CliRunner()
    result = runner.invoke(cli_main, ["workflows", "pull", "--strict", "--workflow-sandbox-id", workflow_sandbox_id])

    # THEN the command returns successfully
    assert result.exit_code == 0

    # AND the pull api is called with strict=True
    vellum_client.workflows.pull.assert_called_once()
    call_args = vellum_client.workflows.pull.call_args.kwargs
    assert call_args["request_options"]["additional_query_parameters"] == {"strict": True}


def test_pull__include_sandbox(vellum_client, mock_module):
    # GIVEN a module on the user's filesystem
    module = mock_module.module
    temp_dir = mock_module.temp_dir

    # AND the workflow pull API call returns a zip file
    vellum_client.workflows.pull.return_value = iter(
        [_zip_file_map({"workflow.py": "print('hello')", "sandbox.py": "print('hello')"})]
    )

    # WHEN the user runs the pull command
    runner = CliRunner()
    result = runner.invoke(cli_main, ["pull", module, "--include-sandbox"])

    # THEN the command returns successfully
    assert result.exit_code == 0, result.output

    # AND the pull api is called with include_sandbox=True
    vellum_client.workflows.pull.assert_called_once()
    call_args = vellum_client.workflows.pull.call_args.kwargs
    assert call_args["request_options"]["additional_query_parameters"] == {"include_sandbox": True}

    # AND the sandbox.py should be added to the ignore list
    lock_json = os.path.join(temp_dir, "vellum.lock.json")
    with open(lock_json) as f:
        lock_data = json.load(f)
        assert lock_data["workflows"][0]["ignore"] == "sandbox.py"
