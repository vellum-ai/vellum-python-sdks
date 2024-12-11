from vellum.workflows import BaseWorkflow
from vellum.workflows.state import BaseState

from .inputs import Inputs
from .nodes.code_execution_node import CodeExecutionNode
from .nodes.final_output import FinalOutput


class Workflow(BaseWorkflow[Inputs, BaseState]):
    graph = CodeExecutionNode >> FinalOutput

    class Outputs(BaseWorkflow.Outputs):
        final_output = FinalOutput.Outputs.value
