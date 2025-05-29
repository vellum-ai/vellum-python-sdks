from typing import Any, Union

from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.displayable import FinalOutputNode, MapNode
from vellum.workflows.nodes.displayable.code_execution_node import CodeExecutionNode
from vellum.workflows.state import BaseState


class Inputs(BaseInputs):
    arr: list[str]


class SubworkflowInputs(BaseInputs):
    items: Any
    item: Any
    index: int


class ConcurrentMapCodeExecutionNode(CodeExecutionNode[BaseState, Union[float, int]]):
    code = """
def main(item: str) -> int:
    return len(item)
"""
    code_inputs = {
        "item": SubworkflowInputs.item,
    }
    runtime = "PYTHON_3_11_6"
    packages = []


class SubworkflowFinalOutput(FinalOutputNode[BaseState, Union[float, int]]):
    class Outputs(FinalOutputNode.Outputs):
        value = ConcurrentMapCodeExecutionNode.Outputs.result


class ConcurrentMapSubworkflow(BaseWorkflow[SubworkflowInputs, BaseState]):
    graph = ConcurrentMapCodeExecutionNode >> SubworkflowFinalOutput

    class Outputs(BaseWorkflow.Outputs):
        final_output = SubworkflowFinalOutput.Outputs.value


class ConcurrentMapNode(MapNode):
    items = Inputs.arr
    subworkflow = ConcurrentMapSubworkflow
    max_concurrency = 40


class MainFinalOutput(FinalOutputNode[BaseState, list]):
    class Outputs(FinalOutputNode.Outputs):
        value = ConcurrentMapNode.Outputs.final_output


class ConcurrentMapExecutionWorkflow(BaseWorkflow[Inputs, BaseState]):
    graph = ConcurrentMapNode >> MainFinalOutput

    class Outputs(BaseWorkflow.Outputs):
        final_output = MainFinalOutput.Outputs.value
