from vellum.workflows import BaseWorkflow
from vellum.workflows.nodes.bases import BaseNode


class StartNode(BaseNode):
    pass


class InputNode(BaseNode):
    class ExternalInputs(BaseNode.ExternalInputs):
        message: str


class InputNode2(BaseNode):
    class ExternalInputs(BaseNode.ExternalInputs):
        message: str


class EndNode(BaseNode):
    middle_message = InputNode.ExternalInputs.message
    middle_message2 = InputNode2.ExternalInputs.message

    class Outputs(BaseNode.Outputs):
        final_value: str

    def run(self) -> Outputs:
        return self.Outputs(final_value=f"{self.middle_message} {self.middle_message2}")


class BasicInputNodeWorkflow(BaseWorkflow):
    """
    This Workflow has two nodes that accept `ExternalInputs` of the same shape to ensure that they
    could each receive external data separately.
    """

    graph = StartNode >> InputNode >> InputNode2 >> EndNode

    class Outputs(BaseWorkflow.Outputs):
        final_value = EndNode.Outputs.final_value
