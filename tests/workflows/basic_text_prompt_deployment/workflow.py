from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs import BaseInputs
from vellum.workflows.nodes.displayable.prompt_deployment_node import PromptDeploymentNode
from vellum.workflows.outputs import BaseOutputs
from vellum.workflows.state import BaseState


class Inputs(BaseInputs):
    city: str
    date: str


class ExamplePromptDeploymentNode(PromptDeploymentNode):
    deployment = "example_prompt_deployment"
    prompt_inputs = {
        "city": Inputs.city,
        "date": Inputs.date,
    }
    ml_model_fallbacks = ["gpt-4o", "gemini-1.5-pro"]


class BasicTextPromptDeployment(BaseWorkflow[Inputs, BaseState]):
    graph = ExamplePromptDeploymentNode

    class Outputs(BaseOutputs):
        text = ExamplePromptDeploymentNode.Outputs.text
