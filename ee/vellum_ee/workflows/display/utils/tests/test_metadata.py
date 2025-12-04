import pytest

from vellum_ee.workflows.display.utils.metadata import _build_metadata_class_path


def build_metadata_class_path_test_cases():
    return [
        # (module, class_name, workflow_root, expected)
        ("my_workflow.nodes.my_node", "MyNode", "my_workflow", ".nodes.my_node.MyNode"),
        ("my_workflow", "MyWorkflow", "my_workflow", ".MyWorkflow"),
        ("my_workflow.triggers.scheduled", "ScheduleTrigger", "my_workflow", ".triggers.scheduled.ScheduleTrigger"),
        ("external.module", "ExternalClass", "my_workflow", "external.module.ExternalClass"),
        ("vellum.workflows.triggers.manual", "Manual", "my_workflow", "vellum.workflows.triggers.manual.Manual"),
        ("my_workflow.nodes.my_node", "MyNode", None, "my_workflow.nodes.my_node.MyNode"),
    ]


@pytest.mark.parametrize(
    "module, class_name, workflow_root, expected",
    build_metadata_class_path_test_cases(),
)
def test_build_metadata_class_path(module, class_name, workflow_root, expected):
    """
    Tests that _build_metadata_class_path correctly formats class paths relative to workflow root.
    """
    # GIVEN a module path, class name, and workflow root
    # WHEN we build the metadata class path
    result = _build_metadata_class_path(module, class_name, workflow_root)

    # THEN we should get the expected formatted path
    assert result == expected
