from vellum.workflows.nodes.displayable import SubworkflowDeploymentNode

from ..inputs import Inputs


class SubworkflowDeployment(SubworkflowDeploymentNode):
    deployment = "mocked-workflow-deployment-release-name"
    release_tag = "LATEST"
    subworkflow_inputs = {
        "test": Inputs.test,
    }

    class Outputs(SubworkflowDeploymentNode.Outputs):
        chat_history: str
