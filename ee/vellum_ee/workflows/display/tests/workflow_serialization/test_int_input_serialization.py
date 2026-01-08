from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs import BaseInputs
from vellum.workflows.nodes import FinalOutputNode
from vellum.workflows.state import BaseState
from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display


class IntInputs(BaseInputs):
    count: int


class OutputNode(FinalOutputNode):
    class Outputs(FinalOutputNode.Outputs):
        value = IntInputs.count


class IntInputWorkflow(BaseWorkflow[IntInputs, BaseState]):
    graph = OutputNode

    class Outputs(BaseWorkflow.Outputs):
        value = OutputNode.Outputs.value


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
