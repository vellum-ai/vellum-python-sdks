from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.state.base import BaseState
from vellum.workflows.workflows.base import BaseWorkflow


class Inputs(BaseInputs):
    threshold: int


class State(BaseState):
    pass


class ProcessNode(BaseNode[State]):
    class Outputs(BaseNode.Outputs):
        result: str

    def run(self) -> Outputs:
        return self.Outputs(result="default_result")


class NodeOutputMockWhenConditionsWorkflow(BaseWorkflow[Inputs, State]):
    graph = ProcessNode

    class Outputs(BaseWorkflow.Outputs):
        final_result = ProcessNode.Outputs.result
        execution_count = ProcessNode.Execution.count
