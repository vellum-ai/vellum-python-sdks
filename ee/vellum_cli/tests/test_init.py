import io
import json
import os
from unittest.mock import patch
import zipfile

from click.testing import CliRunner
from pydash import snake_case

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


class MockTemplate:
    def __init__(self, id, label):
        self.id = id
        self.label = label


def test_init_command(vellum_client, mock_module):
    # GIVEN a module on the user's filesystem
    temp_dir = mock_module.temp_dir
    mock_module.set_pyproject_toml({"workflows": []})
    # GIVEN the vellum client returns a list of template workflows
    fake_templates = [
        MockTemplate(id="template-1", label="Example Workflow"),
        MockTemplate(id="template-2", label="Another Workflow"),
    ]
    vellum_client.workflow_sandboxes.list_workflow_sandbox_examples.return_value.results = fake_templates

    # AND the workflow pull API call returns a zip file
    vellum_client.workflows.pull.return_value = iter([_zip_file_map({"workflow.py": "print('hello')"})])

    # WHEN the user runs the `init` command and selects the first template
    runner = CliRunner()
    result = runner.invoke(cli_main, ["workflows", "init"], input="1\n")

    # THEN the command returns successfully
    assert result.exit_code == 0

    # AND `vellum_client.workflows.pull` is called with the selected template ID
    vellum_client.workflows.pull.assert_called_once_with(
        "template-1",
        request_options={"additional_query_parameters": {"include_sandbox": True}},
    )

    # AND the `workflow.py` file should be created in the correct module directory
    workflow_py = os.path.join(temp_dir, "example_workflow", "workflow.py")
    assert os.path.exists(workflow_py)
    with open(workflow_py) as f:
        assert f.read() == "print('hello')"

    # AND the vellum.lock.json file should be created
    vellum_lock_json = os.path.join(temp_dir, "vellum.lock.json")
    assert os.path.exists(vellum_lock_json)
    with open(vellum_lock_json) as f:
        lock_data = json.load(f)
        assert lock_data["workflows"] == [
            {
                "module": "example_workflow",
                "workflow_sandbox_id": "template-1",
                "ignore": None,
                "deployments": [],
                "container_image_name": None,
                "container_image_tag": None,
                "workspace": "default",
                "target_directory": None,
            }
        ]


def test_init_command__invalid_template_id(vellum_client, mock_module):
    # GIVEN a module on the user's filesystem
    temp_dir = mock_module.temp_dir
    mock_module.set_pyproject_toml({"workflows": []})
    # GIVEN the vellum client returns a list of template workflows
    fake_templates = [
        MockTemplate(id="template-1", label="Example Workflow"),
        MockTemplate(id="template-2", label="Another Workflow"),
    ]
    vellum_client.workflow_sandboxes.list_workflow_sandbox_examples.return_value.results = fake_templates

    # WHEN the user runs the `init` command, enters invalid input and then cancels
    runner = CliRunner()
    # Mock click.prompt to raise a KeyboardInterrupt (simulating Ctrl+C)
    with patch("click.prompt", side_effect=KeyboardInterrupt):
        runner = CliRunner()
        result = runner.invoke(cli_main, ["workflows", "init"])

    # THEN the command is aborted
    assert result.exit_code != 0
    assert "Aborted!" in result.output  # Click shows this message on Ctrl+C

    # AND `vellum_client.workflows.pull` is not called
    vellum_client.workflows.pull.assert_not_called()

    # AND no workflow files are created
    workflow_py = os.path.join(temp_dir, "example_workflow", "workflow.py")
    assert not os.path.exists(workflow_py)

    # AND the lock file remains empty
    vellum_lock_json = os.path.join(temp_dir, "vellum.lock.json")
    if os.path.exists(vellum_lock_json):
        with open(vellum_lock_json) as f:
            lock_data = json.load(f)
            assert lock_data["workflows"] == []


def test_init_command__no_templates(vellum_client, mock_module):
    # GIVEN a module on the user's filesystem
    temp_dir = mock_module.temp_dir
    mock_module.set_pyproject_toml({"workflows": []})
    # GIVEN the vellum client returns no template workflows
    vellum_client.workflow_sandboxes.list_workflow_sandbox_examples.return_value.results = []

    # WHEN the user runs the `init` command
    runner = CliRunner()
    result = runner.invoke(cli_main, ["workflows", "init"])

    # THEN the command gracefully exits
    assert result.exit_code == 0
    assert "No templates available" in result.output

    # AND `vellum_client.workflows.pull` is not called
    vellum_client.workflows.pull.assert_not_called()

    # AND no workflow files are created
    workflow_py = os.path.join(temp_dir, "example_workflow", "workflow.py")
    assert not os.path.exists(workflow_py)

    # AND the lock file remains empty
    vellum_lock_json = os.path.join(temp_dir, "vellum.lock.json")
    if os.path.exists(vellum_lock_json):
        with open(vellum_lock_json) as f:
            lock_data = json.load(f)
            assert lock_data["workflows"] == []


def test_init_command_target_directory_exists(vellum_client, mock_module):
    """
    GIVEN a target directory already exists
    WHEN the user tries to run the `init` command
    THEN the command should fail and exit without modifying existing files
    """
    temp_dir = mock_module.temp_dir
    existing_workflow_dir = os.path.join(temp_dir, "example_workflow")

    # Create the target directory to simulate it already existing
    os.makedirs(existing_workflow_dir, exist_ok=True)

    # Ensure directory exists before command execution
    assert os.path.exists(existing_workflow_dir)

    # GIVEN the vellum client returns a list of template workflows
    fake_templates = [
        MockTemplate(id="template-1", label="Example Workflow"),
    ]
    vellum_client.workflow_sandboxes.list_workflow_sandbox_examples.return_value.results = fake_templates

    # AND the workflow pull API call returns a zip file
    vellum_client.workflows.pull.return_value = iter([_zip_file_map({"workflow.py": "print('hello')"})])

    # WHEN the user runs the `init` command and selects the template
    runner = CliRunner()
    result = runner.invoke(cli_main, ["workflows", "init"], input="1\n")

    # THEN the command should detect the existing directory and abort
    assert result.exit_code == 0
    assert f"{existing_workflow_dir} already exists." in result.output

    # Ensure the directory still exists (wasn't deleted or modified)
    assert os.path.exists(existing_workflow_dir)

    # AND `vellum_client.workflows.pull` is not called
    vellum_client.workflows.pull.assert_not_called()

    # AND no workflow files are created
    workflow_py = os.path.join(temp_dir, "example_workflow", "workflow.py")
    assert not os.path.exists(workflow_py)

    # AND the lock file remains empty
    vellum_lock_json = os.path.join(temp_dir, "vellum.lock.json")
    if os.path.exists(vellum_lock_json):
        with open(vellum_lock_json) as f:
            lock_data = json.load(f)
            assert lock_data["workflows"] == []


def test_init_command_with_template_name(vellum_client, mock_module):
    # GIVEN a module on the user's filesystem
    temp_dir = mock_module.temp_dir
    mock_module.set_pyproject_toml({"workflows": []})

    # GIVEN the vellum client returns a list of template workflows
    fake_templates = [
        MockTemplate(id="template-1", label="Example Workflow"),
        MockTemplate(id="template-2", label="Another Workflow"),
    ]
    vellum_client.workflow_sandboxes.list_workflow_sandbox_examples.return_value.results = fake_templates

    # AND the workflow pull API call returns a zip file
    vellum_client.workflows.pull.return_value = iter([_zip_file_map({"workflow.py": "print('hello')"})])

    # WHEN the user runs the `init` command with a specific template name
    template_name = snake_case("Another Workflow")
    runner = CliRunner()
    result = runner.invoke(cli_main, ["workflows", "init", template_name])

    # THEN the command returns successfully
    assert result.exit_code == 0

    # AND `vellum_client.workflows.pull` is called with the correct template ID
    vellum_client.workflows.pull.assert_called_once_with(
        "template-2",  # ID of "Another Workflow"
        request_options={"additional_query_parameters": {"include_sandbox": True}},
    )

    # AND the workflow files should be created in the correct module directory
    workflow_py = os.path.join(temp_dir, "another_workflow", "workflow.py")

    assert os.path.exists(workflow_py)

    with open(workflow_py) as f:
        assert f.read() == "print('hello')"

    # AND the vellum.lock.json file should be created with the correct data
    vellum_lock_json = os.path.join(temp_dir, "vellum.lock.json")
    assert os.path.exists(vellum_lock_json)

    with open(vellum_lock_json) as f:
        lock_data = json.load(f)
        assert lock_data["workflows"] == [
            {
                "module": "another_workflow",
                "workflow_sandbox_id": "template-2",
                "ignore": None,
                "deployments": [],
                "container_image_name": None,
                "container_image_tag": None,
                "workspace": "default",
                "target_directory": None,
            }
        ]


def test_init_command_with_nonexistent_template_name(vellum_client, mock_module):
    # GIVEN a module on the user's filesystem
    temp_dir = mock_module.temp_dir
    mock_module.set_pyproject_toml({"workflows": []})

    # GIVEN the vellum client returns a list of template workflows
    fake_templates = [
        MockTemplate(id="template-1", label="Example Workflow"),
        MockTemplate(id="template-2", label="Another Workflow"),
    ]
    vellum_client.workflow_sandboxes.list_workflow_sandbox_examples.return_value.results = fake_templates

    # WHEN the user runs the `init` command with a non-existent template name
    nonexistent_template = "nonexistent_template"
    runner = CliRunner()
    result = runner.invoke(cli_main, ["workflows", "init", nonexistent_template])

    # THEN the command should indicate the template was not found
    assert result.exit_code == 0
    assert f"Template {nonexistent_template} not found" in result.output

    # AND `vellum_client.workflows.pull` is not called
    vellum_client.workflows.pull.assert_not_called()

    # AND no workflow files are created
    example_workflow_dir = os.path.join(temp_dir, "example_workflow")
    nonexistent_workflow_dir = os.path.join(temp_dir, nonexistent_template)

    assert not os.path.exists(example_workflow_dir)
    assert not os.path.exists(nonexistent_workflow_dir)

    # AND the lock file remains empty
    vellum_lock_json = os.path.join(temp_dir, "vellum.lock.json")
    if os.path.exists(vellum_lock_json):
        with open(vellum_lock_json) as f:
            lock_data = json.load(f)
            assert lock_data["workflows"] == []


def test_init__with_target_dir(vellum_client, mock_module):
    # GIVEN a module on the user's filesystem
    temp_dir = mock_module.temp_dir
    mock_module.set_pyproject_toml({"workflows": []})

    # GIVEN the vellum client returns a list of template workflows
    fake_templates = [
        MockTemplate(id="template-1", label="Example Workflow"),
    ]
    vellum_client.workflow_sandboxes.list_workflow_sandbox_examples.return_value.results = fake_templates

    # AND the workflow pull API call returns a zip file
    vellum_client.workflows.pull.return_value = iter([_zip_file_map({"workflow.py": "print('hello')"})])

    # AND a target directory
    target_dir = os.path.join(temp_dir, "dir")
    os.makedirs(target_dir, exist_ok=True)

    # WHEN the user runs the init command with target-dir
    runner = CliRunner()
    result = runner.invoke(cli_main, ["workflows", "init", "--target-dir", target_dir], input="1\n")

    # THEN the command returns successfully
    assert result.exit_code == 0

    # AND the `workflow.py` file should be created in the target directory
    module_path = os.path.join(target_dir, "example_workflow")
    workflow_py = os.path.join(module_path, "workflow.py")
    assert os.path.exists(workflow_py)
    with open(workflow_py) as f:
        assert f.read() == "print('hello')"

    # AND the files are not in the default module directory
    default_module_path = os.path.join(temp_dir, "example_workflow", "workflow.py")
    assert not os.path.exists(default_module_path)

    # AND the vellum.lock.json file should be created in the original directory
    vellum_lock_json = os.path.join(temp_dir, "vellum.lock.json")
    assert os.path.exists(vellum_lock_json)
    with open(vellum_lock_json) as f:
        lock_data = json.load(f)
        assert lock_data["workflows"] == [
            {
                "module": "example_workflow",
                "workflow_sandbox_id": "template-1",
                "ignore": None,
                "deployments": [],
                "container_image_name": None,
                "container_image_tag": None,
                "workspace": "default",
                "target_directory": module_path,
            }
        ]


def test_init__with_nested_target_dir(vellum_client, mock_module):
    # GIVEN a module on the user's filesystem
    temp_dir = mock_module.temp_dir
    mock_module.set_pyproject_toml({"workflows": []})

    # GIVEN the vellum client returns a list of template workflows
    fake_templates = [
        MockTemplate(id="template-1", label="Example Workflow"),
    ]
    vellum_client.workflow_sandboxes.list_workflow_sandbox_examples.return_value.results = fake_templates

    # AND the workflow pull API call returns a zip file
    vellum_client.workflows.pull.return_value = iter([_zip_file_map({"workflow.py": "print('hello')"})])

    # AND a nested target directory that doesn't exist yet
    nested_target_dir = os.path.join(temp_dir, "dir-1", "dir-2")

    # WHEN the user runs the init command with nested target-dir
    runner = CliRunner()
    result = runner.invoke(cli_main, ["workflows", "init", "--target-dir", nested_target_dir], input="1\n")

    # THEN the command returns successfully
    assert result.exit_code == 0

    # AND the nested directory with module subdirectory should be created
    module_path = os.path.join(nested_target_dir, "example_workflow")
    assert os.path.exists(module_path)

    # AND the workflow.py file is written to the nested target directory
    workflow_py = os.path.join(module_path, "workflow.py")
    assert os.path.exists(workflow_py)
    with open(workflow_py) as f:
        assert f.read() == "print('hello')"

    # AND the files are not in the default module directory
    default_module_path = os.path.join(temp_dir, "example_workflow", "workflow.py")
    assert not os.path.exists(default_module_path)

    # AND the vellum.lock.json file is still updated
    vellum_lock_json = os.path.join(temp_dir, "vellum.lock.json")
    assert os.path.exists(vellum_lock_json)
    with open(vellum_lock_json) as f:
        lock_data = json.load(f)
        assert lock_data["workflows"] == [
            {
                "module": "example_workflow",
                "workflow_sandbox_id": "template-1",
                "ignore": None,
                "deployments": [],
                "container_image_name": None,
                "container_image_tag": None,
                "workspace": "default",
                "target_directory": module_path,
            }
        ]


def test_init__with_template_name_and_target_dir(vellum_client, mock_module):
    # GIVEN a module on the user's filesystem
    temp_dir = mock_module.temp_dir
    mock_module.set_pyproject_toml({"workflows": []})

    # GIVEN the vellum client returns a list of template workflows
    fake_templates = [
        MockTemplate(id="template-1", label="Example Workflow"),
        MockTemplate(id="template-2", label="Another Workflow"),
    ]
    vellum_client.workflow_sandboxes.list_workflow_sandbox_examples.return_value.results = fake_templates

    # AND the workflow pull API call returns a zip file
    vellum_client.workflows.pull.return_value = iter([_zip_file_map({"workflow.py": "print('hello')"})])

    # AND a target directory
    target_dir = os.path.join(temp_dir, "dir")
    os.makedirs(target_dir, exist_ok=True)

    # WHEN the user runs the init command with a specific template name and target-dir
    template_name = snake_case("Another Workflow")
    runner = CliRunner()
    result = runner.invoke(cli_main, ["workflows", "init", template_name, "--target-dir", target_dir])

    # THEN the command returns successfully
    assert result.exit_code == 0

    # AND `vellum_client.workflows.pull` is called with the correct template ID
    vellum_client.workflows.pull.assert_called_once_with(
        "template-2",  # ID of "Another Workflow"
        request_options={"additional_query_parameters": {"include_sandbox": True}},
    )

    # AND the workflow files should be created in the target directory with the correct module subdirectory
    module_path = os.path.join(target_dir, "another_workflow")
    workflow_py = os.path.join(module_path, "workflow.py")
    assert os.path.exists(workflow_py)
    with open(workflow_py) as f:
        assert f.read() == "print('hello')"

    # AND the files are not in the default module directory
    default_module_path = os.path.join(temp_dir, "another_workflow", "workflow.py")
    assert not os.path.exists(default_module_path)

    # AND the vellum.lock.json file should be created with the correct data
    vellum_lock_json = os.path.join(temp_dir, "vellum.lock.json")
    assert os.path.exists(vellum_lock_json)

    with open(vellum_lock_json) as f:
        lock_data = json.load(f)
        assert lock_data["workflows"] == [
            {
                "module": "another_workflow",
                "workflow_sandbox_id": "template-2",
                "ignore": None,
                "deployments": [],
                "container_image_name": None,
                "container_image_tag": None,
                "workspace": "default",
                "target_directory": module_path,
            }
        ]
