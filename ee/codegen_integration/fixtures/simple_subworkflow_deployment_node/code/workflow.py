from vellum.workflows import BaseWorkflow
from vellum.workflows.state import BaseState

from .inputs import Inputs
from .nodes.final_output import FinalOutput
from .nodes.subworkflow_deployment import SubworkflowDeployment


class Workflow(BaseWorkflow[Inputs, BaseState]):
    graph = SubworkflowDeployment >> FinalOutput

    class Outputs(BaseWorkflow.Outputs):
        final_output = FinalOutput.Outputs.value
