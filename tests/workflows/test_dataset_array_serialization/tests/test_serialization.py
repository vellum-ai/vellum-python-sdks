from vellum_ee.workflows.display.workflows.base_workflow_display import BaseWorkflowDisplay

from tests.workflows.test_dataset_array_serialization.workflow import Inputs, TestDatasetArraySerializationWorkflow


def test_serialize_module_with_array_input():
    """
    Tests that serialize_module correctly serializes dataset with array of strings inputs.

    This test verifies that when a dataset row contains an input that is mapped to an
    array of strings, the serialization preserves the array structure and values correctly.
    This addresses the issue where scenarios were being lost during vellum push.
    """
    module_path = "tests.workflows.test_dataset_array_serialization"

    result = BaseWorkflowDisplay.serialize_module(module_path)

    assert hasattr(result, "dataset")

    assert result.dataset is not None
    assert isinstance(result.dataset, list)

    assert len(result.dataset) == 3

    assert result.dataset[0]["label"] == "Scenario 1"

    assert "tags" in result.dataset[0]["inputs"]
    assert isinstance(result.dataset[0]["inputs"]["tags"], list)
    assert result.dataset[0]["inputs"]["tags"] == ["python", "typescript", "javascript"]

    assert result.dataset[1]["label"] == "Backend Tags"

    assert "tags" in result.dataset[1]["inputs"]
    assert isinstance(result.dataset[1]["inputs"]["tags"], list)
    assert result.dataset[1]["inputs"]["tags"] == ["django", "flask", "fastapi"]

    assert result.dataset[2]["label"] == "Frontend Tags"

    assert "tags" in result.dataset[2]["inputs"]
    assert isinstance(result.dataset[2]["inputs"]["tags"], list)
    assert result.dataset[2]["inputs"]["tags"] == ["react", "vue", "angular"]


def test_workflow_execution_with_array_input():
    """
    Tests that the workflow can successfully execute with array of strings input.
    """
    workflow = TestDatasetArraySerializationWorkflow()

    inputs = Inputs(tags=["python", "typescript", "javascript"])

    final_event = workflow.run(inputs=inputs)

    # THEN the workflow should complete successfully
    assert final_event.name == "workflow.execution.fulfilled", final_event

    assert final_event.outputs["final_result"] == "Tags: python, typescript, javascript"
