import pytest
import io
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
        ["pull", "workflows"],
    ],
    ids=["pull", "pull_workflows"],
)
def test_pull(vellum_client, mock_module, base_command):
    # GIVEN a module on the user's filesystem
    temp_dir, module, _ = mock_module

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
    temp_dir, module, set_pyproject_toml = mock_module

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
    result = runner.invoke(cli_main, ["pull", "workflows", "--workflow-sandbox-id", workflow_sandbox_id])
    os.chdir(current_dir)

    # THEN the command returns successfully
    assert result.exit_code == 0

    # AND the pull api is called with exclude_code=True
    vellum_client.workflows.pull.assert_called_once()
    workflow_py = os.path.join(temp_dir, "workflow_87654321", "workflow.py")
    assert os.path.exists(workflow_py)
    with open(workflow_py) as f:
        assert f.read() == "print('hello')"


def test_pull__remove_missing_files(vellum_client, mock_module):
    # GIVEN a module on the user's filesystem
    temp_dir, module, _ = mock_module

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
    temp_dir, module, set_pyproject_toml = mock_module

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
    _, module, __ = mock_module

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
    _, module, __ = mock_module

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
