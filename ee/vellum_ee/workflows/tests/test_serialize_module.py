import pytest
from unittest.mock import Mock

from vellum.client import Vellum as VellumClient
from vellum_ee.workflows.display.workflows.base_workflow_display import BaseWorkflowDisplay


def test_serialize_module_happy_path():
    """Test that serialize_module works with a valid module path."""
    module_path = "tests.workflows.basic_final_output_node"

    result = BaseWorkflowDisplay.serialize_module(module_path)

    assert isinstance(result, dict)
    assert "workflow_raw_data" in result
    assert "input_variables" in result
    assert "output_variables" in result


def test_serialize_module_with_client():
    """Test that serialize_module works with a custom client."""
    module_path = "tests.workflows.basic_final_output_node"
    mock_client = Mock(spec=VellumClient)

    result = BaseWorkflowDisplay.serialize_module(module_path, client=mock_client)

    assert isinstance(result, dict)
    assert "workflow_raw_data" in result


def test_serialize_module_with_dry_run():
    """Test that serialize_module works with dry_run=True."""
    module_path = "tests.workflows.basic_final_output_node"

    result = BaseWorkflowDisplay.serialize_module(module_path, dry_run=True)

    assert isinstance(result, dict)
    assert "workflow_raw_data" in result


def test_serialize_module_invalid_module():
    """Test that serialize_module raises appropriate error for invalid module."""
    module_path = "nonexistent.module.path"

    with pytest.raises((ImportError, ModuleNotFoundError)):
        BaseWorkflowDisplay.serialize_module(module_path)
