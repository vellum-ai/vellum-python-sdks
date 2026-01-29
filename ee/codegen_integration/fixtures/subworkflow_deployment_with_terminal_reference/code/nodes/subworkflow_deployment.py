from vellum.workflows.nodes.displayable import SubworkflowDeploymentNode


class SubworkflowDeployment(SubworkflowDeploymentNode):
    deployment = "mocked-workflow-deployment-release-name"
    release_tag = "LATEST"
    subworkflow_inputs = {}

    class Outputs(SubworkflowDeploymentNode.Outputs):
        feedback: str

    class Display(SubworkflowDeploymentNode.Display):
        x = 400
        y = 200
