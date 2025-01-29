from vellum.workflows import BaseWorkflow
from vellum.workflows.nodes.bases.base import BaseNode


class BasicInvalidOutputNode(BaseNode):
    class Outputs(BaseNode.Outputs):
        first_output: str
        second_output: str

    def run(self) -> Outputs:
        return self.Outputs(invalid_output="Hello", second_output="World")  # type: ignore


class BasicInvalidOutputWorkflow(BaseWorkflow):
    graph = BasicInvalidOutputNode

    class Outputs(BaseWorkflow.Outputs):
        output = BasicInvalidOutputNode.Outputs.first_output
