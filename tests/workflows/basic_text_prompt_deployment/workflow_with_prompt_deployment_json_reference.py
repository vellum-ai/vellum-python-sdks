from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs import BaseInputs
from vellum.workflows.nodes import TemplatingNode
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


class ExampleTemplatingNode(TemplatingNode[BaseState, str]):
    template = "The weather in {{ city }} on {{ date }} is {{ weather }}."

    inputs = {
        "city": Inputs.city,
        "date": Inputs.date,
        "weather": ExamplePromptDeploymentNode.Outputs.json,
    }


class WorkflowWithPromptDeploymentJsonReferenceWorkflow(BaseWorkflow[Inputs, BaseState]):
    graph = ExamplePromptDeploymentNode >> ExampleTemplatingNode

    class Outputs(BaseOutputs):
        text = ExampleTemplatingNode.Outputs.result
