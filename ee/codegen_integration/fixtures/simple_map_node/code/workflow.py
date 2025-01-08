from vellum.workflows import BaseWorkflow
from vellum.workflows.state import BaseState

from .inputs import Inputs
from .nodes.code_execution_node import CodeExecutionNode
from .nodes.final_output import FinalOutput
from .nodes.map_node import MapNode


class Workflow(BaseWorkflow[Inputs, BaseState]):
    graph = CodeExecutionNode >> MapNode >> FinalOutput

    class Outputs(BaseWorkflow.Outputs):
        final_output = FinalOutput.Outputs.value
