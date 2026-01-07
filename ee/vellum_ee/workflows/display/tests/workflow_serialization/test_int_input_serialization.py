from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display

from tests.workflows.int_input_workflow.workflow import IntInputWorkflow


def test_serialize_workflow__int_input_schema_preserved():
    """
    Tests that an int input has its schema preserved during serialization.
    """

    # GIVEN a Workflow that has an int input
    # WHEN we serialize it
    workflow_display = get_workflow_display(workflow_class=IntInputWorkflow)
    serialized_workflow: dict = workflow_display.serialize()

    # THEN the input variables should include the schema field with type "integer"
    input_variables = serialized_workflow["input_variables"]
    assert len(input_variables) == 1

    # AND the schema should preserve the int type
    assert input_variables[0]["type"] == "NUMBER"
    assert input_variables[0]["schema"] == {"type": "integer"}
