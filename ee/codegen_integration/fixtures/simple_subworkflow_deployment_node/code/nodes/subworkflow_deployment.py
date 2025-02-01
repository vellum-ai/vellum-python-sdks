from vellum.workflows.nodes.displayable import SubworkflowDeploymentNode

from ..inputs import Inputs


class SubworkflowDeployment(SubworkflowDeploymentNode):
    deployment = "deployment-test"
    release_tag = "LATEST"
    subworkflow_inputs = {
        "test": Inputs.test,
    }

    class Outputs(SubworkflowDeploymentNode.Outputs):
        final_output: str
