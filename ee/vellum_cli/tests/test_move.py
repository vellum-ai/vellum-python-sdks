import os

from click.testing import CliRunner

from vellum_cli import main
from vellum_cli.config import load_vellum_cli_config


def test_move__happy_path(mock_module):
    """
    Test that the move command successfully moves a module and updates configuration.
    """

    temp_dir = mock_module.temp_dir
    old_module = mock_module.module
    new_module = "examples.new.workflow"

    old_module_dir = os.path.join(temp_dir, *old_module.split("."))
    os.makedirs(old_module_dir, exist_ok=True)
    with open(os.path.join(old_module_dir, "workflow.py"), "w") as f:
        f.write("# test workflow")

    runner = CliRunner()
    result = runner.invoke(main, ["workflows", "move", old_module, new_module])

    assert result.exit_code == 0

    assert not os.path.exists(old_module_dir)

    new_module_dir = os.path.join(temp_dir, *new_module.split("."))
    assert os.path.exists(new_module_dir)
    assert os.path.exists(os.path.join(new_module_dir, "workflow.py"))

    config = load_vellum_cli_config()
    workflow_config = next((w for w in config.workflows if w.module == new_module), None)
    assert workflow_config is not None
    assert workflow_config.workflow_sandbox_id == mock_module.workflow_sandbox_id


def test_move__old_module_not_exists(mock_module):
    """
    Test that the move command fails when the old module doesn't exist.
    """

    old_module = "nonexistent.module"
    new_module = "examples.new.workflow"

    runner = CliRunner()
    result = runner.invoke(main, ["workflows", "move", old_module, new_module])

    assert result.exit_code != 0
    assert "does not exist in the filesystem" in str(result.exception)


def test_move__new_module_already_exists(mock_module):
    """
    Test that the move command fails when the new module already exists.
    """

    temp_dir = mock_module.temp_dir
    old_module = mock_module.module
    new_module = "examples.existing.workflow"

    old_module_dir = os.path.join(temp_dir, *old_module.split("."))
    new_module_dir = os.path.join(temp_dir, *new_module.split("."))
    os.makedirs(old_module_dir, exist_ok=True)
    os.makedirs(new_module_dir, exist_ok=True)

    runner = CliRunner()
    result = runner.invoke(main, ["workflows", "move", old_module, new_module])

    assert result.exit_code != 0
    assert "already exists" in str(result.exception)


def test_move__no_workflow_config_found(mock_module):
    """
    Test that the move command fails when no workflow config is found.
    """

    temp_dir = mock_module.temp_dir
    old_module = "examples.unconfigured.workflow"
    new_module = "examples.new.workflow"

    old_module_dir = os.path.join(temp_dir, *old_module.split("."))
    os.makedirs(old_module_dir, exist_ok=True)

    runner = CliRunner()
    result = runner.invoke(main, ["workflows", "move", old_module, new_module])

    assert result.exit_code != 0
    assert "No workflow configuration found" in str(result.exception)


def test_move__with_workspace_filter(mock_module):
    """
    Test that the move command works with workspace filtering.
    """

    temp_dir = mock_module.temp_dir
    old_module = mock_module.module
    new_module = "examples.new.workflow"
    workspace = "default"

    old_module_dir = os.path.join(temp_dir, *old_module.split("."))
    os.makedirs(old_module_dir, exist_ok=True)
    with open(os.path.join(old_module_dir, "workflow.py"), "w") as f:
        f.write("# test workflow")

    runner = CliRunner()
    result = runner.invoke(main, ["workflows", "move", old_module, new_module, "--workspace", workspace])

    assert result.exit_code == 0

    config = load_vellum_cli_config()
    workflow_config = next((w for w in config.workflows if w.module == new_module), None)
    assert workflow_config is not None
    assert workflow_config.workspace == workspace


def test_move__preserves_workflow_metadata(mock_module):
    """
    Test that the move command preserves all workflow metadata except the module name.
    """

    temp_dir = mock_module.temp_dir
    old_module = mock_module.module
    new_module = "examples.new.workflow"

    config = load_vellum_cli_config()
    original_config = next((w for w in config.workflows if w.module == old_module), None)
    assert original_config is not None
    original_config.container_image_name = "test-image"
    original_config.container_image_tag = "v1.0"
    original_config.ignore = "sandbox.py"
    config.save()

    old_module_dir = os.path.join(temp_dir, *old_module.split("."))
    os.makedirs(old_module_dir, exist_ok=True)
    with open(os.path.join(old_module_dir, "workflow.py"), "w") as f:
        f.write("# test workflow")

    runner = CliRunner()
    result = runner.invoke(main, ["workflows", "move", old_module, new_module])

    assert result.exit_code == 0

    config = load_vellum_cli_config()
    workflow_config = next((w for w in config.workflows if w.module == new_module), None)
    assert workflow_config is not None
    assert workflow_config.workflow_sandbox_id == mock_module.workflow_sandbox_id
    assert workflow_config.container_image_name == "test-image"
    assert workflow_config.container_image_tag == "v1.0"
    assert workflow_config.ignore == "sandbox.py"
