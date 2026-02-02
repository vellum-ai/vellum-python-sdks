from vellum_ee.workflows.display.workflows.base_workflow_display import BaseWorkflowDisplay


def test_serialize_module__invalid_mocks_reference():
    """
    Tests that serialization returns an error when sandbox.py has an invalid Mocks reference on a node.
    """

    # GIVEN a workflow module with a sandbox.py that references CodeExecution.Mocks.Outputs
    # which doesn't exist - nodes don't have a Mocks nested class
    module = "tests.workflows.test_sandbox_invalid_mocks_reference"

    # WHEN we serialize the module
    result = BaseWorkflowDisplay.serialize_module(module)

    # THEN the result should contain an error about the invalid attribute access
    assert len(result.errors) > 0

    # AND the error should be an AttributeError from trying to access a non-existent attribute
    error_messages = [error.message for error in result.errors]
    assert any(
        "__annotations__" in msg or "has no attribute" in msg for msg in error_messages
    ), f"Expected attribute error in error messages, got: {error_messages}"


def test_serialize_module__invalid_runner_kwarg():
    """
    Tests that serialization returns an error when sandbox.py uses an invalid kwarg on WorkflowSandboxRunner.
    """

    # GIVEN a workflow module with a sandbox.py that uses 'scenarios' kwarg instead of 'dataset'
    module = "tests.workflows.test_sandbox_invalid_runner_kwarg"

    # WHEN we serialize the module
    result = BaseWorkflowDisplay.serialize_module(module)

    # THEN the result should contain an error about the invalid keyword argument
    assert len(result.errors) > 0

    # AND the error message should mention the unexpected keyword argument 'scenarios'
    error_messages = [error.message for error in result.errors]
    assert any(
        "scenarios" in msg for msg in error_messages
    ), f"Expected 'scenarios' in error messages, got: {error_messages}"


def test_serialize_module__state_mutable_default_validation():
    """
    Tests that serialization returns a validation error when a state variable uses a mutable default
    (e.g., = []) instead of Field(default_factory=list).
    """

    # GIVEN a workflow module with a state class that uses a mutable default (= [])
    module = "tests.workflows.test_state_mutable_default_validation"

    # WHEN we serialize the module
    result = BaseWorkflowDisplay.serialize_module(module)

    # THEN the result should contain an error about mutable defaults
    assert len(result.errors) > 0

    # AND the error message should mention mutable default, Field(default_factory=list), and the attribute name
    error_messages = [error.message for error in result.errors]
    assert any(
        "Mutable default value detected" in msg and "Field(default_factory=list)" in msg and "State.chat_history" in msg
        for msg in error_messages
    ), f"Expected mutable default error in error messages, got: {error_messages}"


def test_serialize_module__orphan_node_in_workflow_file():
    """
    Tests that serialization returns an error when a node is defined in workflow.py
    but not included in the workflow's graph or unused_graphs.
    """

    # GIVEN a workflow module with a node defined in workflow.py that is not in graph or unused_graphs
    module = "tests.workflows.test_orphan_node_serialization_error"

    # WHEN we serialize the module
    result = BaseWorkflowDisplay.serialize_module(module)

    # THEN the result should contain an error about the orphan node
    assert len(result.errors) > 0

    # AND the error message should mention the orphan node and that it's not in graph or unused_graphs
    error_messages = [error.message for error in result.errors]
    assert any(
        "OrphanNode" in msg and "not included in" in msg and "graph or unused_graphs" in msg for msg in error_messages
    ), f"Expected orphan node error in error messages, got: {error_messages}"


def test_serialize_module__orphan_node_in_nodes_directory():
    """
    Tests that serialization returns an error when a node is defined in the nodes/ directory
    but not included in the workflow's graph or unused_graphs.
    """

    # GIVEN a workflow module with a node defined in nodes/orphan_node.py that is not in graph or unused_graphs
    module = "tests.workflows.test_orphan_node_in_nodes_dir"

    # WHEN we serialize the module
    result = BaseWorkflowDisplay.serialize_module(module)

    # THEN the result should contain an error about the orphan node
    assert len(result.errors) > 0

    # AND the error message should mention the orphan node and that it's not in graph or unused_graphs
    error_messages = [error.message for error in result.errors]
    assert any(
        "OrphanNodeInNodesDir" in msg and "not included in" in msg and "graph or unused_graphs" in msg
        for msg in error_messages
    ), f"Expected orphan node error in error messages, got: {error_messages}"


def test_serialize_module__runner_run_called_during_serialization():
    """
    Tests that serialization returns an error when runner.run() is called outside
    of 'if __name__ == "__main__"' block in sandbox.py, but still extracts the dataset.
    """

    # GIVEN a workflow module with a sandbox.py that calls runner.run() at module level
    module = "tests.workflows.test_sandbox_runner_run_during_serialization"

    # WHEN we serialize the module
    result = BaseWorkflowDisplay.serialize_module(module)

    # THEN the result should contain an error about runner.run() being called during serialization
    assert len(result.errors) > 0

    # AND the error message should mention that runner.run() should not be called during serialization
    error_messages = [error.message for error in result.errors]
    assert any(
        "runner.run()" in msg and "serialization" in msg.lower() for msg in error_messages
    ), f"Expected runner.run() serialization error in error messages, got: {error_messages}"

    # AND the dataset should still be serialized despite the error
    assert result.dataset is not None
    assert len(result.dataset) == 1
    assert result.dataset[0]["label"] == "Scenario 1"
