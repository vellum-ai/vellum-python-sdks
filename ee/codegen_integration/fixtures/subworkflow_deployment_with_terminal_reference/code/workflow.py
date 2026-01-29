from vellum.workflows import BaseWorkflow

from .nodes.final_output import FinalOutput
from .nodes.subworkflow_deployment import SubworkflowDeployment


class Workflow(BaseWorkflow):
    graph = SubworkflowDeployment >> FinalOutput

    class Outputs(BaseWorkflow.Outputs):
        feedback = FinalOutput.Outputs.value
