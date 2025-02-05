import pytest

from tests.workflows.circular_lazy_reference.workflow import CircularLazyReferenceWorkflow


@pytest.mark.skip(reason="https://github.com/vellum-ai/vellum/pull/7810")
def test_workflow__happy_path():
    # GIVEN a workflow definition that contains two nodes that reference each other
    workflow = CircularLazyReferenceWorkflow()

    # WHEN the workflow is executed
    final_event = workflow.run()

    # THEN the workflow should return the correct result
    assert final_event.name == "workflow.execution.fulfilled"
    assert final_event.outputs.final_value == 2
