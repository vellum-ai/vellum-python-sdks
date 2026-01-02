from vellum_ee.workflows.display.workflows.base_workflow_display import BaseWorkflowDisplay


def test_serialize_module__dataset_mocks_are_stable():
    """
    Tests that serialization produces stable, deterministic output for DatasetRow mocks
    across multiple serializations.
    """

    # GIVEN a workflow module with a sandbox.py that has DatasetRow with mocks
    module = "tests.workflows.test_sandbox_dataset_mocks_serialization"

    # WHEN we serialize the module twice
    result_1 = BaseWorkflowDisplay.serialize_module(module)
    result_2 = BaseWorkflowDisplay.serialize_module(module)

    # THEN both serializations should succeed without errors
    assert len(result_1.errors) == 0, f"First serialization had errors: {result_1.errors}"
    assert len(result_2.errors) == 0, f"Second serialization had errors: {result_2.errors}"

    # AND both should have a dataset
    assert result_1.dataset is not None, "First serialization should have a dataset"
    assert result_2.dataset is not None, "Second serialization should have a dataset"

    # AND the datasets should be identical (stable serialization)
    assert result_1.dataset == result_2.dataset, (
        f"Datasets should be identical across serializations.\n"
        f"First: {result_1.dataset}\n"
        f"Second: {result_2.dataset}"
    )
