from vellum.workflows.nodes import BaseNode

from tests.workflows.basic_inline_prompt_node_with_functions_and_dependencies.inputs import WorkflowInputs


class StartNode(BaseNode):
    noun = WorkflowInputs.noun

    class Outputs(BaseNode.Outputs):
        final_noun: str

    def run(self) -> Outputs:
        final_value = "animal"
        return self.Outputs(final_noun=final_value)
