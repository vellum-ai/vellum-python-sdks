from tests.workflows.circular_lazy_reference.workflow import CircularLazyReferenceWorkflow


def test_workflow__happy_path():
    # GIVEN a workflow definition that contains two nodes that reference each other
    workflow = CircularLazyReferenceWorkflow()

    # WHEN the workflow is executed
    final_event = workflow.run()

    # THEN the workflow should return the correct result
    assert final_event.name == "workflow.execution.fulfilled", final_event.body
    assert final_event.outputs.final_value == "World Hello World Hello Start"
