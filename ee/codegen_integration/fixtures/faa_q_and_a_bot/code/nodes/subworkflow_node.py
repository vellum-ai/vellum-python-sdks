from vellum.workflows.nodes.displayable import SubworkflowDeploymentNode

from ..inputs import Inputs


class SubworkflowNode(SubworkflowDeploymentNode):
    deployment = "mocked-workflow-deployment-release-name"
    release_tag = "LATEST"
    subworkflow_inputs = {
        "chat_history": Inputs.chat_history,
    }

    class Outputs(SubworkflowDeploymentNode.Outputs):
        chat_history: str
