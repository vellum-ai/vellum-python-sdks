from typing import Optional

from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases import BaseNode


class Inputs(BaseInputs):
    initial_value: Optional[str] = None


class StartNode(BaseNode):
    initial_value = Inputs.initial_value

    class Outputs(BaseNode.Outputs):
        final_value: Optional[str]

    def run(self) -> Outputs:
        return StartNode.Outputs(final_value=self.initial_value)


class OptionalInputsWorkflow(BaseWorkflow):
    graph = StartNode

    class Outputs(BaseWorkflow.Outputs):
        final_value = StartNode.Outputs.final_value
