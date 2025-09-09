from vellum.client.types import VellumAudio, VellumDocument, VellumImage, VellumVideo
from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs import BaseInputs
from vellum.workflows.nodes.displayable.prompt_deployment_node import PromptDeploymentNode
from vellum.workflows.outputs import BaseOutputs
from vellum.workflows.state import BaseState


class Inputs(BaseInputs):
    audio_variable: VellumAudio
    video_variable: VellumVideo
    image_variable: VellumImage
    document_variable: VellumDocument


class ExamplePromptDeploymentNode(PromptDeploymentNode):
    deployment = "example_prompt_deployment"
    prompt_inputs = {
        "audio_variable": Inputs.audio_variable,
        "video_variable": Inputs.video_variable,
        "image_variable": Inputs.image_variable,
        "document_variable": Inputs.document_variable,
    }


class BasicPromptDeploymentWorkflow(BaseWorkflow[Inputs, BaseState]):
    graph = ExamplePromptDeploymentNode

    class Outputs(BaseOutputs):
        results = ExamplePromptDeploymentNode.Outputs.results
        text = ExamplePromptDeploymentNode.Outputs.text
