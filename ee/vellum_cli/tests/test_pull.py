import pytest
import io
import json
import os
import tempfile
from uuid import uuid4
import zipfile

from click.testing import CliRunner

from vellum.client.core.api_error import ApiError
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
    workflow_sandbox_id = mock_module.workflow_sandbox_id

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

    # AND the vellum.lock.json file is created
    vellum_lock_json = os.path.join(temp_dir, "vellum.lock.json")
    assert os.path.exists(vellum_lock_json)
    with open(vellum_lock_json) as f:
        lock_data = json.load(f)
        assert lock_data == {
            "version": "1.0",
            "workflows": [
                {
                    "module": module,
                    "workflow_sandbox_id": workflow_sandbox_id,
                    "container_image_name": None,
                    "container_image_tag": None,
                    "ignore": None,
                    "deployments": [],
                    "workspace": "default",
                    "target_directory": None,
                }
            ],
            "workspaces": [],
        }


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


@pytest.mark.parametrize(
    "base_command",
    [
        ["pull"],
        ["workflows", "pull"],
    ],
    ids=["pull", "workflows_pull"],
)
def test_pull__with_target_dir(vellum_client, mock_module, base_command):
    # GIVEN a module on the user's filesystem
    temp_dir = mock_module.temp_dir
    module = mock_module.module
    workflow_sandbox_id = mock_module.workflow_sandbox_id

    # AND a target directory
    target_dir = os.path.join(temp_dir, "dir")
    os.makedirs(target_dir, exist_ok=True)

    # AND the workflow pull API call returns a zip file
    vellum_client.workflows.pull.return_value = iter([_zip_file_map({"workflow.py": "print('hello')"})])

    # WHEN the user runs the pull command with target-dir
    runner = CliRunner()
    result = runner.invoke(cli_main, base_command + [module, "--target-dir", target_dir])

    # THEN the command returns successfully
    assert result.exit_code == 0

    # AND the workflow.py file is written to the target directory
    module_path = os.path.join(target_dir, *module.split("."))
    workflow_py = os.path.join(module_path, "workflow.py")
    assert os.path.exists(workflow_py)
    with open(workflow_py) as f:
        assert f.read() == "print('hello')"

    # AND the files are not in the default module directory
    default_module_path = os.path.join(temp_dir, *module.split("."), "workflow.py")
    assert not os.path.exists(default_module_path)

    # AND the vellum.lock.json file is still updated
    vellum_lock_json = os.path.join(temp_dir, "vellum.lock.json")
    assert os.path.exists(vellum_lock_json)
    with open(vellum_lock_json) as f:
        lock_data = json.load(f)
        assert lock_data == {
            "version": "1.0",
            "workflows": [
                {
                    "module": module,
                    "workflow_sandbox_id": workflow_sandbox_id,
                    "container_image_name": None,
                    "container_image_tag": None,
                    "ignore": None,
                    "deployments": [],
                    "workspace": "default",
                    "target_directory": module_path,
                }
            ],
            "workspaces": [],
        }


@pytest.mark.parametrize(
    "base_command",
    [
        ["pull"],
        ["workflows", "pull"],
    ],
    ids=["pull", "workflows_pull"],
)
def test_pull__with_nested_target_dir(vellum_client, mock_module, base_command):
    # GIVEN a module on the user's filesystem
    temp_dir = mock_module.temp_dir
    module = mock_module.module
    workflow_sandbox_id = mock_module.workflow_sandbox_id

    # AND a nested target directory that doesn't exist yet
    nested_target_dir = os.path.join(temp_dir, "dir-1", "dir-2")

    # AND the workflow pull API call returns a zip file
    vellum_client.workflows.pull.return_value = iter([_zip_file_map({"workflow.py": "print('hello')"})])

    # WHEN the user runs the pull command with nested target-dir
    runner = CliRunner()
    result = runner.invoke(cli_main, base_command + [module, "--target-dir", nested_target_dir])

    # THEN the command returns successfully
    assert result.exit_code == 0

    # AND the nested directory with module subdirectory should be created
    module_path = os.path.join(nested_target_dir, *module.split("."))
    assert os.path.exists(module_path)

    # AND the nested directory should be created
    assert os.path.exists(module_path)

    # AND the workflow.py file is written to the nested target directory
    workflow_py = os.path.join(module_path, "workflow.py")
    assert os.path.exists(workflow_py)
    with open(workflow_py) as f:
        assert f.read() == "print('hello')"

    # AND the files are not in the default module directory
    default_module_path = os.path.join(temp_dir, *module.split("."), "workflow.py")
    assert not os.path.exists(default_module_path)

    # AND the vellum.lock.json file is still updated
    vellum_lock_json = os.path.join(temp_dir, "vellum.lock.json")
    assert os.path.exists(vellum_lock_json)
    with open(vellum_lock_json) as f:
        lock_data = json.load(f)
        assert lock_data == {
            "version": "1.0",
            "workflows": [
                {
                    "module": module,
                    "workflow_sandbox_id": workflow_sandbox_id,
                    "container_image_name": None,
                    "container_image_tag": None,
                    "ignore": None,
                    "deployments": [],
                    "workspace": "default",
                    "target_directory": module_path,
                }
            ],
            "workspaces": [],
        }


def test_pull__sandbox_id_with_no_config(vellum_client):
    # GIVEN a workflow sandbox id
    workflow_sandbox_id = "87654321-0000-0000-0000-000000000000"

    # AND the workflow pull API call returns a zip file
    vellum_client.workflows.pull.return_value = iter(
        [
            _zip_file_map(
                {"workflow.py": "print('hello')", "metadata.json": json.dumps({"label": "Super Cool Workflow"})}
            )
        ]
    )

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
    workflow_py = os.path.join(temp_dir, "super_cool_workflow", "workflow.py")
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
            "workspaces": [],
            "workflows": [
                {
                    "module": "super_cool_workflow",
                    "workflow_sandbox_id": "87654321-0000-0000-0000-000000000000",
                    "ignore": None,
                    "deployments": [],
                    "container_image_tag": None,
                    "container_image_name": None,
                    "workspace": "default",
                    "target_directory": None,
                }
            ],
        }


def test_pull__sandbox_id_with_other_workflow_configured(vellum_client, mock_module):
    # GIVEN a pyproject.toml with a workflow configured
    temp_dir = mock_module.temp_dir

    # AND a different workflow sandbox id
    workflow_sandbox_id = "87654321-0000-0000-0000-000000000000"

    # AND the workflow pull API call returns a zip file
    vellum_client.workflows.pull.return_value = iter(
        [
            _zip_file_map(
                {"workflow.py": "print('hello')", "metadata.json": json.dumps({"label": "Super Cool Workflow"})}
            )
        ]
    )

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
    workflow_py = os.path.join(temp_dir, "super_cool_workflow", "workflow.py")
    assert os.path.exists(workflow_py)
    with open(workflow_py) as f:
        assert f.read() == "print('hello')"


def test_pull__workflow_deployment_with_no_config(vellum_client):
    # GIVEN a workflow deployment
    workflow_deployment = "my-deployment"

    # AND the workflow pull API call returns a zip file
    vellum_client.workflows.pull.return_value = iter(
        [
            _zip_file_map(
                {
                    "workflow.py": "print('hello')",
                    "metadata.json": json.dumps({"deployment_name": workflow_deployment, "label": "Some Label"}),
                }
            )
        ]
    )

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
                    "container_image_tag": None,
                    "container_image_name": None,
                    "workspace": "default",
                    "target_directory": None,
                }
            ],
            "workspaces": [],
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
                        "workflow_sandbox_id": workflow_sandbox_id,
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
    vellum_client.workflows.pull.return_value = iter(
        [
            _zip_file_map(
                {
                    "workflow.py": "print('hello')",
                    "metadata.json": json.dumps(
                        {
                            "runner_config": {"container_image_name": "test", "container_image_tag": "1.0"},
                            "label": "Super Cool Workflow",
                        }
                    ),
                }
            )
        ]
    )

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
                "container_image_name": None,
                "container_image_tag": None,
                "workspace": "default",
                "target_directory": None,
            },
            {
                "module": "super_cool_workflow",
                "workflow_sandbox_id": new_workflow_sandbox_id,
                "ignore": None,
                "deployments": [],
                "container_image_name": "test",
                "container_image_tag": "1.0",
                "workspace": "default",
                "target_directory": None,
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


def test_pull__same_pull_twice__one_entry_in_lockfile(vellum_client, mock_module):
    # GIVEN a module on the user's filesystem
    module = mock_module.module
    temp_dir = mock_module.temp_dir
    workflow_sandbox_id = mock_module.workflow_sandbox_id

    # AND the workflow pull API call returns a zip file both times
    zip_contents = _zip_file_map({"workflow.py": "print('hello')"})
    responses = iter([zip_contents, zip_contents])

    def workflows_pull_side_effect(*args, **kwargs):
        return iter([next(responses)])

    vellum_client.workflows.pull.side_effect = workflows_pull_side_effect

    # AND the user runs the pull command once
    runner = CliRunner()
    runner.invoke(cli_main, ["pull", module])

    # WHEN the user runs the pull command again but with the workflow sandbox id
    result = runner.invoke(cli_main, ["workflows", "pull", "--workflow-sandbox-id", workflow_sandbox_id])

    # THEN the command returns successfully
    assert result.exit_code == 0, (result.output, result.exception)

    # AND the lockfile should only have one entry
    lock_json = os.path.join(temp_dir, "vellum.lock.json")
    with open(lock_json) as f:
        lock_data = json.load(f)
        assert len(lock_data["workflows"]) == 1


def test_pull__module_not_in_config(vellum_client, mock_module):
    # GIVEN a module on the user's filesystem
    module = mock_module.module
    temp_dir = mock_module.temp_dir
    workflow_sandbox_id = mock_module.workflow_sandbox_id
    set_pyproject_toml = mock_module.set_pyproject_toml

    # AND the pyproject.toml does not have the module configured
    set_pyproject_toml({"workflows": []})

    # AND the workflow pull API call returns a zip file
    vellum_client.workflows.pull.return_value = iter([_zip_file_map({"workflow.py": "print('hello')"})])

    # WHEN the user runs the pull command again with the workflow sandbox id and module
    runner = CliRunner()
    result = runner.invoke(cli_main, ["workflows", "pull", module, "--workflow-sandbox-id", workflow_sandbox_id])

    # THEN the command returns successfully
    assert result.exit_code == 0, (result.output, result.exception)

    # AND the lockfile should have the new entry
    lock_json = os.path.join(temp_dir, "vellum.lock.json")
    with open(lock_json) as f:
        lock_data = json.load(f)
        assert lock_data["workflows"] == [
            {
                "module": module,
                "workflow_sandbox_id": workflow_sandbox_id,
                "ignore": None,
                "deployments": [],
                "container_image_name": None,
                "container_image_tag": None,
                "workspace": "default",
                "target_directory": None,
            }
        ]


def test_pull__multiple_instances_of_same_module__keep_when_pulling_another_module(vellum_client, mock_module):
    # GIVEN a module on the user's filesystem
    module = mock_module.module
    temp_dir = mock_module.temp_dir
    workflow_sandbox_id = mock_module.workflow_sandbox_id

    # AND the vellum lock file has two instances of some other module
    lock_data = {
        "workflows": [
            {
                "module": "some_other_module",
                "workflow_sandbox_id": str(uuid4()),
                "workspace": "default",
            },
            {
                "module": "some_other_module",
                "workflow_sandbox_id": str(uuid4()),
                "workspace": "other",
            },
        ]
    }
    lock_json = os.path.join(temp_dir, "vellum.lock.json")
    with open(lock_json, "w") as f:
        json.dump(lock_data, f)

    # AND the workflow pull API call returns a zip file
    vellum_client.workflows.pull.return_value = iter([_zip_file_map({"workflow.py": "print('hello')"})])

    # WHEN the user runs the pull command on the new module
    runner = CliRunner()
    result = runner.invoke(cli_main, ["workflows", "pull", module, "--workflow-sandbox-id", workflow_sandbox_id])

    # THEN the command returns successfully
    assert result.exit_code == 0, (result.output, result.exception)

    # AND the lockfile should have all three entries
    with open(lock_json) as f:
        lock_data = json.load(f)
        assert len(lock_data["workflows"]) == 3


def test_pull__module_name_from_deployment_name(vellum_client):
    # GIVEN a workflow deployment
    workflow_deployment = "test-workflow-deployment-id"

    # AND the workflow pull API call returns a zip file with metadata containing a deployment_name
    deployment_name = "Test Deployment"
    vellum_client.workflows.pull.return_value = iter(
        [
            _zip_file_map(
                {
                    "workflow.py": "print('hello')",
                    "metadata.json": json.dumps({"deployment_name": deployment_name, "label": "Some Label"}),
                }
            )
        ]
    )

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

    # AND the module name is derived from the deployment_name in metadata.json (snake_cased)
    vellum_lock_json = os.path.join(temp_dir, "vellum.lock.json")
    assert os.path.exists(vellum_lock_json)
    with open(vellum_lock_json) as f:
        lock_data = json.loads(f.read())
        assert lock_data["workflows"][0]["module"] == "test_deployment"

    # AND the workflow.py file is written to the module directory with the correct name
    workflow_py = os.path.join(temp_dir, "test_deployment", "workflow.py")
    assert os.path.exists(workflow_py)
    with open(workflow_py) as f:
        assert f.read() == "print('hello')"


def test_pull__invalid_zip_file(vellum_client):
    workflow_deployment = "test-workflow-deployment-id"

    # GIVEN a workflow pull API call returns an invalid zip file
    vellum_client.workflows.pull.return_value = iter([b"invalid"])  # Return bytes instead of string

    # WHEN the user runs the pull command
    runner = CliRunner()
    result = runner.invoke(cli_main, ["workflows", "pull", "--workflow-deployment", workflow_deployment])

    # THEN the command returns an error
    assert result.exit_code == 1
    assert (
        str(result.exception)
        == "The API we tried to pull from returned an invalid zip file. Please make sure your `VELLUM_API_URL` environment variable is set correctly."  # noqa: E501
    )


def test_pull__json_decode_error(vellum_client):
    workflow_deployment = "test-workflow-deployment-id"

    # GIVEN a workflow pull API call that returns a generator which raises an error when consumed
    def mock_error_generator():
        # This generator yields nothing but raises when consumed
        if False:  # This ensures the generator is created but yields nothing
            yield b""
        raise ApiError(status_code=400, body="Invalid JSON")

    vellum_client.workflows.pull.return_value = mock_error_generator()

    # WHEN the user runs the pull command
    runner = CliRunner()
    result = runner.invoke(cli_main, ["workflows", "pull", "--workflow-deployment", workflow_deployment])

    # THEN the command returns an error
    assert result.exit_code == 1
    assert (
        str(result.exception)
        == "The API we tried to pull is invalid. Please make sure your `VELLUM_API_URL` environment variable is set correctly."  # noqa: E501
    )


def test_pull__unauthorized_error_path(vellum_client):
    workflow_deployment = "test-workflow-deployment-id"

    # GIVEN an unauthorized error with the error message from the API
    def mock_error_generator():
        yield b""
        raise ApiError(status_code=403, body={"detail": "Authentication credentials were not provided."})

    vellum_client.workflows.pull.return_value = mock_error_generator()

    # WHEN the user runs the pull command
    runner = CliRunner()
    result = runner.invoke(cli_main, ["workflows", "pull", "--workflow-deployment", workflow_deployment])

    # THEN the command returns an error
    assert result.exit_code == 1
    assert str(result.exception) == "Please make sure your `VELLUM_API_KEY` environment variable is set correctly."
