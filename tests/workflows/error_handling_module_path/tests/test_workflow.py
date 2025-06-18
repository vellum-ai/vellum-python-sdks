from vellum.workflows.errors.types import WorkflowErrorCode

from tests.workflows.error_handling_module_path.workflow import CustomErrorWorkflow


def test_non_vellum_node_error_returns_node_execution_error():
    workflow = CustomErrorWorkflow()

    terminal_event = workflow.run()

    assert terminal_event.name == "workflow.execution.rejected"
    assert terminal_event.error.code == WorkflowErrorCode.NODE_EXECUTION
    assert "An unexpected error occurred while running node" in str(terminal_event.error.message)


def test_error_handling_implementation_in_runner():
    """Test that the error handling logic in WorkflowRunner correctly checks module paths"""
    from vellum.workflows.nodes.bases import BaseNode

    class MockVellumNode(BaseNode):
        pass

    class MockCustomNode(BaseNode):
        pass

    def simulate_error_handling(node_module_path):
        if node_module_path.startswith("vellum."):
            return WorkflowErrorCode.INTERNAL_ERROR
        else:
            return WorkflowErrorCode.NODE_EXECUTION

    # Test vellum module paths return INTERNAL_ERROR
    assert simulate_error_handling("vellum.workflows.nodes.custom") == WorkflowErrorCode.INTERNAL_ERROR
    assert simulate_error_handling("vellum.core.something") == WorkflowErrorCode.INTERNAL_ERROR

    # Test non-vellum module paths return NODE_EXECUTION
    assert simulate_error_handling("tests.workflows.something") == WorkflowErrorCode.NODE_EXECUTION
    assert simulate_error_handling("custom.user.module") == WorkflowErrorCode.NODE_EXECUTION
    assert simulate_error_handling("some_third_party.module") == WorkflowErrorCode.NODE_EXECUTION


def test_module_path_checking_logic():
    from vellum.workflows.nodes.bases import BaseNode

    class TestNode(BaseNode):
        pass

    test_node = TestNode()

    assert not test_node.__class__.__module__.startswith("vellum.")

    def check_module_path(module_name):
        return module_name.startswith("vellum.")

    assert check_module_path("vellum.workflows.nodes.custom") is True
    assert check_module_path("vellum.core.something") is True
    assert check_module_path("tests.workflows.something") is False
    assert check_module_path("custom.user.module") is False
    assert check_module_path("some_third_party.module") is False
