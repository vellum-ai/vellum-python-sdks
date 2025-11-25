import pytest

from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display

from .workflow import ShadowedBaseNodeWorkflow


def test_serialize_workflow__base_node_shadowed_by_workflow_class():
    """
    Tests that serialization raises a helpful error when a base node class
    has been shadowed by another class with the same name in the same module.
    """
    # GIVEN a workflow where a base node class has been shadowed by a workflow class
    # (defined in workflow.py at the module level)

    # WHEN we try to serialize the workflow
    workflow_display = get_workflow_display(workflow_class=ShadowedBaseNodeWorkflow)

    # THEN it should raise a ValueError with a helpful message
    with pytest.raises(ValueError) as exc_info:
        workflow_display.serialize()

    assert "shadowed by another class with the same name" in str(exc_info.value)
    assert "NestedWorkflow" in str(exc_info.value)
