from vellum_ee.workflows.display.workflows.base_workflow_display import BaseWorkflowDisplay


def test_serialize_module_happy_path():
    """Test that serialize_module works with a valid module path."""
    module_path = "tests.workflows.trivial"

    result = BaseWorkflowDisplay.serialize_module(module_path)

    assert hasattr(result, "exec_config")
    assert hasattr(result, "errors")
    assert isinstance(result.exec_config, dict)
    assert isinstance(result.errors, list)
    assert "workflow_raw_data" in result.exec_config
    assert "input_variables" in result.exec_config
    assert "output_variables" in result.exec_config


def test_serialize_module_includes_additional_files():
    """Test that serialize_module includes additional files from the module directory."""
    module_path = "tests.workflows.module_with_additional_files"

    result = BaseWorkflowDisplay.serialize_module(module_path)

    assert hasattr(result, "exec_config")
    assert hasattr(result, "errors")
    assert isinstance(result.exec_config, dict)
    assert isinstance(result.errors, list)

    assert "module_data" in result.exec_config
    assert "additional_files" in result.exec_config["module_data"]

    additional_files = result.exec_config["module_data"]["additional_files"]
    assert isinstance(additional_files, dict)

    assert "helper.py" in additional_files
    assert "data.txt" in additional_files
    assert "utils/constants.py" in additional_files

    assert "workflow.py" not in additional_files
    assert "__init__.py" not in additional_files
    assert "utils/__init__.py" in additional_files
    assert "nodes/test_node.py" not in additional_files

    assert "def helper_function():" in additional_files["helper.py"]
    assert "sample data file" in additional_files["data.txt"]
    assert "CONSTANT_VALUE" in additional_files["utils/constants.py"]
