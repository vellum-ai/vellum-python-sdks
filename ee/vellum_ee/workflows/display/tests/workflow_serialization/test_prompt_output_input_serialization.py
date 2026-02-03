from vellum.client.types import PromptOutput
from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs import BaseInputs
from vellum.workflows.nodes import FinalOutputNode
from vellum.workflows.state import BaseState
from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display


class PromptOutputInputs(BaseInputs):
    prompt_result: PromptOutput


class OutputNode(FinalOutputNode):
    class Outputs(FinalOutputNode.Outputs):
        value = PromptOutputInputs.prompt_result


class PromptOutputInputWorkflow(BaseWorkflow[PromptOutputInputs, BaseState]):
    graph = OutputNode

    class Outputs(BaseWorkflow.Outputs):
        value = OutputNode.Outputs.value


def test_serialize_workflow__prompt_output_input_schema():
    """
    Tests that a PromptOutput input has its schema serialized as the union type.
    """

    # GIVEN a Workflow that has a PromptOutput input
    # WHEN we serialize it
    workflow_display = get_workflow_display(workflow_class=PromptOutputInputWorkflow)
    serialized_workflow: dict = workflow_display.serialize()

    # THEN the input variables should include the schema field
    input_variables = serialized_workflow["input_variables"]
    assert len(input_variables) == 1

    input_var = input_variables[0]
    assert input_var["key"] == "prompt_result"
    assert input_var["type"] == "JSON"

    # AND the schema should reference the PromptOutput union type
    assert input_var["schema"] == {"$ref": "#/$defs/vellum.client.types.prompt_output.PromptOutput"}
