import time
from typing import ClassVar, Iterator, List, Set, Type

from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.nodes.displayable.subworkflow_deployment_node.node import SubworkflowDeploymentNode
from vellum.workflows.outputs import BaseOutputs
from vellum.workflows.outputs.base import BaseOutput
from vellum.workflows.state import BaseState


class State(BaseState):
    execution_times: List[float] = []


class MockSubworkflowDeploymentNode(SubworkflowDeploymentNode[State]):
    deployment = "mock-deployment-id"
    subworkflow_inputs = {}

    def run(self) -> Iterator[BaseOutput]:
        start_time = time.time()
        self.state.execution_times.append(start_time)
        time.sleep(0.2)
        yield BaseOutput(name="result", value=f"completed at {start_time}")


class FirstSubworkflowNode(MockSubworkflowDeploymentNode):
    pass


class SecondSubworkflowNode(MockSubworkflowDeploymentNode):
    pass


class ThirdSubworkflowNode(MockSubworkflowDeploymentNode):
    pass


class FourthSubworkflowNode(MockSubworkflowDeploymentNode):
    pass


class SubworkflowConcurrencyLimitWorkflow(BaseWorkflow[BaseInputs, State]):
    graph: ClassVar[Set[Type[BaseNode[State]]]] = {
        FirstSubworkflowNode,
        SecondSubworkflowNode,
        ThirdSubworkflowNode,
        FourthSubworkflowNode,
    }

    class Outputs(BaseOutputs):
        execution_times = State.execution_times
