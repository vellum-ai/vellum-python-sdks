from tests.workflows.pydantic_output_reference.workflow import PydanticOutputReferenceWorkflow


def test_run_workflow__pydantic_field_reference():
    """
    Tests that a node can reference a specific field from a Pydantic model output of a previous node.
    """

    # GIVEN a workflow where FirstNode outputs a Pydantic model
    # AND SecondNode references a field from that model
    workflow = PydanticOutputReferenceWorkflow()

    # WHEN we run the workflow
    terminal_event = workflow.run()

    # THEN the workflow should have completed successfully
    assert terminal_event.name == "workflow.execution.fulfilled", terminal_event

    # AND the output should contain the greeting using the referenced field
    assert terminal_event.outputs == {"greeting": "Hello, Alice!"}
